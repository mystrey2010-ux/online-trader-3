import os
import json
import time
import logging
import sys
import subprocess
import pandas as pd
import numpy as np
import random
from datetime import datetime
import ccxt

# ============================================
# PRIMARY GOAL: A SELF-IMPROVING Trading Bot
# ============================================
# This bot trades BTC/USDT using RSI signals with automatic stop-loss protection.
# KEY FEATURES for Novice Developers:
#   • Self-improving brain: Adjusts strategy parameters after every 3 trades
#   • Scientific method: Hypotheses logged in hypothesis_ledger
#   • Stop-loss protection: Automatic exit on -1.6% price drop (Priority #1)
#   • Position accumulation: Value-weighted average entry price across BUYs
#   • Paper trading mode: Kraken CLI for risk-free testing (LIVE_TRADING_ENABLED=false)
# ============================================

# --- CONFIGURATION & LOGGING SETUP ---
LOG_FILE = "trader.log"
CONFIG_PATH = "config.json"
LIVE_TRADING_ENABLED = os.getenv("LIVE_TRADING_ENABLED", "false").lower() == "true"
DEFAULT_SL_COOLDOWN = 300  # fallback if config missing


# Redirect STDOUT and STDERR to trader.log
class LoggerRedirect:
    def __init__(self, log_file):
        self.log_file = log_file
        self.stream = open(log_file, "a")

    def write(self, message):
        if not message or not message.strip():
            return
        self.stream.write(message)
        self.stream.flush()

    def flush(self):
        self.stream.flush()

sys.stdout = LoggerRedirect(LOG_FILE)
sys.stderr = LoggerRedirect(LOG_FILE)

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler(LOG_FILE)]
)

def load_config():
    with open(CONFIG_PATH, 'r') as f:
        return json.load(f)

def save_config(config):
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=2)

def cleanup_stale_positions():
    """Remove empty or stale open_position entries from config."""
    try:
        with open(CONFIG_PATH, 'r') as f:
            config = json.load(f)
        if isinstance(config, dict) and "open_position" in config:
            pos = config["open_position"]
            # Remove if position is None, empty dict, or all values are None (stale entry)
            if not pos or (isinstance(pos, dict) and all(k is None for k in pos.values())):
                logging.info("🧹 Stale/empty open_position removed (fresh state detected).")
                del config["open_position"]
                save_config(config)
    except Exception as e:
        logging.debug(f"Cleanup skipped: {e}")


# --- EXCHANGE WRAPPERS ---

class KrakenCliPaperExchange:
    """Wrapper for Kraken CLI Paper Trading."""
    def __init__(self):
        self.bin = "kraken"
        self.path_env = os.environ.copy()
        cargo_bin = os.path.expanduser("~/.cargo/bin")
        self.path_env["PATH"] = f"{cargo_bin}:{self.path_env['PATH']}"

    def _run(self, args):
        cmd = [self.bin, "paper"] + args + ["-o", "json"]
        result = subprocess.run(cmd, capture_output=True, text=True, env=self.path_env)
        if result.returncode != 0:
            raise Exception(f"Kraken CLI Error: {result.stderr.strip()}")
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            return result.stdout

    def fetch_balance(self):
        data = self._run(["balance"])
        balances = {}
        if isinstance(data, dict):
            for curr, vals in data.get("balances", {}).items():
                balances[curr] = {"free": vals.get("available", 0.0), "used": vals.get("reserved", 0.0)}
        return balances

    def fetch_ohlcv(self, symbol, timeframe='1m', limit=50):
        public_exchange = ccxt.kraken()
        return public_exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)

    def create_market_buy_order(self, symbol, amount):
        cli_symbol = symbol.replace("/", "").replace("USDT", "USD")
        self._run(["buy", cli_symbol, str(amount), "--type", "market"])
        return {"status": "closed"}

    def create_market_sell_order(self, symbol, amount):
        cli_symbol = symbol.replace("/", "").replace("USDT", "USD")
        self._run(["sell", cli_symbol, str(amount), "--type", "market"])
        return {"status": "closed"}

    def fetch_ticker(self, symbol):
        public_exchange = ccxt.kraken()
        return public_exchange.fetch_ticker(symbol)

class RealKrakenExchange:
    """Wrapper for real Kraken via CCXT."""
    def __init__(self, api_config):
        self.exchange = ccxt.kraken({
            'apiKey': api_config.get('apiKey', ''),
            'secret': api_config.get('secret', ''),
            'enableRateLimit': True,
            'options': {'defaultType': 'spot'}
        })

    def fetch_balance(self):
        return self.exchange.fetch_balance()

    def fetch_ohlcv(self, symbol, timeframe='1m', limit=50):
        return self.exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)

    def create_market_buy_order(self, symbol, amount):
        return self.exchange.create_market_buy_order(symbol, amount)

    def create_market_sell_order(self, symbol, amount):
        return self.exchange.create_market_sell_order(symbol, amount)

    def fetch_ticker(self, symbol):
        return self.exchange.fetch_ticker(symbol)

class GenericCCXTExchange:
    """Generic Wrapper for any CCXT exchange (e.g., Bybit)."""
    def __init__(self, exchange_id):
        try:
            self.exchange = getattr(ccxt, exchange_id)({
                'apiKey': os.getenv(f'{exchange_id.upper()}_API_KEY', ''),
                'secret': os.getenv(f'{exchange_id.upper()}_API_SECRET', ''),
                'enableRateLimit': True
            })
        except AttributeError:
            raise Exception(f"Unsupported exchange: {exchange_id}")

    def fetch_balance(self):
        return self.exchange.fetch_balance()

    def fetch_ohlcv(self, symbol, timeframe='1m', limit=50):
        return self.exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)

    def create_market_buy_order(self, symbol, amount):
        return self.exchange.create_market_buy_order(symbol, amount)

    def create_market_sell_order(self, symbol, amount):
        return self.exchange.create_market_sell_order(symbol, amount)

    def fetch_ticker(self, symbol):
        return self.exchange.fetch_ticker(symbol)


# ============================================
# TRADING ENGINE WITH SELF-IMPROVEMENT BRAIN
# ============================================
class OnlineTrader:
    """
    Trading Engine with Self-Improvement Brain
    
    This class implements the core trading logic for Online Trader-3:
    - Fetches market data via CCXT or Kraken CLI (paper trading mode)
    - Executes RSI-based buy/sell signals
    - Enforces stop-loss protection as Priority #1 risk management
    - Accumulates positions with value-weighted average entry price
    - Self-improves strategy after every N trades (reflection_cadence=3)
    
    Architecture Pattern: Direct Exchange Balance (no virtual sub-account layers)
    Reference: See ARCHITECTURE.md and DECISIONS.md for full design.
    
    Example Usage:
        trader = OnlineTrader()
        while True:
            trader.run_cycle()  # Run one 60-second trading cycle
    """
    
    def __init__(self):
        self.config = load_config()
        
        # Add Phase 2 rollback fields if not present (v2.4 upgrade)
        if "version" not in self.config:
            self.config["version"] = 1
        if "previous_strategies" not in self.config:
            self.config["previous_strategies"] = []
        if "needs_rollback" not in self.config:
            self.config["needs_rollback"] = False
        
        # Cleanup any stale position entries from config
        cleanup_stale_positions()
        
        # Restore open position from config if present (D-020: prevents spurious BUY on restart)
        pos = self.config.get("open_position")
        if pos and pos.get("entry_price"):
            self.current_position = 'long'
            self.entry_price = pos["entry_price"]
            self.entry_rsi = pos.get("entry_rsi")  # B-011 fix: restore entry_rsi for D-032 dynamic threshold
            logging.info(f"🔄 Restored open position from config: {pos.get('amount_btc', 0)} BTC @ ${pos['entry_price']:.2f}")
        else:
            self.current_position = None
            self.entry_price = None
# B-011 fix: ensure None when no position

        # T-029 fix: Restore stop-loss cooldown from config to prevent immediate re-buy after restart
        self.sl_cooldown_until = self.config.get("sl_cooldown_until", 0)
        # after restart (B-003 fix). If no open_position, defaults to 0.0.
        if pos and pos.get("entry_price") and pos.get("amount_btc"):
            self.last_trade_usd_amount = pos["amount_btc"] * pos["entry_price"]
            logging.info(f"🔄 Restored last_trade_usd_amount: ${self.last_trade_usd_amount:.2f}")
        else:
            self.last_trade_usd_amount = 0.0
         
        exchange_name = self.config.get("exchange", {}).get("type", "kraken").lower()
        # Kraken has no sandbox - always use CLI paper trading for Kraken (unless live trading)
        # For other exchanges, check sandbox_mode setting
        is_kraken = exchange_name == "kraken"
        live_enabled = LIVE_TRADING_ENABLED
        use_paper_trading = is_kraken and not live_enabled
        
        if use_paper_trading:
            logging.info("🚀 RUNNING IN KRAKEN PAPER MODE (Kraken CLI)")
            self.exchange = KrakenCliPaperExchange()
        else:
            # Real trading mode - use CCXT for Kraken API keys or CCXT exchange
            api_config = self.config.get("exchange", {}) if is_kraken else {}
            if is_kraken and api_config:
                logging.info("🔥 Using Real Kraken API")
                self.exchange = RealKrakenExchange(api_config)
            else:
                logging.info(f"🚀 USING CCXT MODE FOR {exchange_name.upper()}")
                self.exchange = GenericCCXTExchange(exchange_name)

        # Verify Balance
        try:
            balance = self.exchange.fetch_balance()
            usdt_free = balance.get('USDT', {}).get('free', 0) or balance.get('USD', {}).get('free', 0)
            logging.info(f"💰 Exchange Balance: ${usdt_free:.2f}")
        except Exception as e:
            logging.error(f"❌ Failed to fetch balance: {e}")

    def int_as_bool(self, val):
        if isinstance(val, bool): return val
        return str(val).lower() == "true"

    def calculate_rsi(self, prices, period=14):
        if len(prices) < period + 1: return 50.0
        df = pd.DataFrame(prices, columns=['close'])
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100.0 - (100.0 / (1.0 + rs))
        return rsi.iloc[-1]

    def _estimate_rsi_change_for_price_change(self, price_change_pct, lookback=20):
        """
        Estimate what RSI change would correspond to a given price change percentage
        based on recent price and RSI history.
        
        Args:
            price_change_pct: Target price change percentage (e.g., 0.0052 for 0.52%)
            lookback: Number of periods to look back for correlation calculation
            
        Returns:
            Estimated RSI change needed to achieve the price change
        """
        if len(self.config.get("trade_history", [])) < lookback:
            # Not enough history, return a conservative estimate
            # Based on typical RSI range (0-100) and typical price volatility
            return abs(price_change_pct) * 100  # Rough approximation
        
        # Get recent price data to calculate price-RSI correlation
        try:
            ohlcv = self.exchange.fetch_ohlcv(self.config["target_asset"], timeframe='1m', limit=lookback)
            df = pd.DataFrame(ohlcv, columns=['ts', 'o', 'h', 'l', 'c', 'v'])
            
            # Calculate price changes
            price_changes = df['c'].pct_change().dropna()
            
            # Calculate RSI values for the same periods
            rsi_values = []
            for i in range(len(df)):
                if i >= 14:  # Need enough data for RSI calculation
                    rsi_val = self.calculate_rsi(df['c'].iloc[:i+1].values, 14)
                    rsi_values.append(rsi_val)
                else:
                    rsi_values.append(50.0)  # Neutral RSI for insufficient data
            
            # Align the arrays (both start from index 14)
            price_changes_aligned = price_changes.iloc[14:].values
            rsi_values_aligned = np.array(rsi_values[14:])
            
            # Calculate RSI changes
            rsi_changes = np.diff(rsi_values_aligned)
            price_changes_final = price_changes_aligned[1:]  # Align with rsi_changes
            
            # Calculate correlation-based estimate
            if len(price_changes_final) > 5 and np.std(price_changes_final) > 0:
                # Linear regression: rsi_change = slope * price_change
                slope = np.cov(rsi_changes, price_changes_final)[0,1] / np.var(price_changes_final)
                estimated_rsi_change = slope * price_change_pct
                return estimated_rsi_change
            else:
                # Fallback to simple ratio based on typical ranges
                # Typical RSI range: 0-100 (100 points)
                # Typical daily price change: ~0.02 (2%) 
                # So ~50 RSI points per 1 price change point
                return price_change_pct * 50
        except Exception:
            # If anything goes wrong, return a reasonable default
            return abs(price_change_pct) * 30  # Conservative estimate


# ============================================
# SELF-IMPROVEMENT BRAIN (D-006 from DECISIONS.md)
# ============================================
# This method evaluates trading performance after every N trades
# and adjusts strategy parameters using "scientific control":
# 1. Calculate average return, max drawdown, Sharpe ratio
# 2. Compare against targets in performance_targets config section  
# 3. If performance fails, randomly select ONE parameter to adjust:
#    • indicator_threshold (RSI buy/sell signal)
#    • stop_loss_pct (risk tolerance)
#    • position_size_pct (capital allocation per trade)
# 4. Log hypothesis with metrics in hypothesis_ledger
# Reference: See ARCHITECTURE.md section "4. Self-Improvement Brain Pattern"
# ============================================
    def _tag_regime(self, df):
        """Tag market regime using 20-day rolling return classifier (PRIMARY GOAL spec)."""
        if len(df) < 21:
            return "INSUFFICIENT_DATA"
        
        df['rolling_20_pct'] = df['c'].pct_change(periods=20).dropna()
        
        recent_returns = df['rolling_20_pct'].tail(10)
        avg_rolling_return = recent_returns.mean() if not recent_returns.empty else 0
        
        # Classification thresholds scaled for 20-day crypto macro shifts (±10%)
        if avg_rolling_return > 0.10:
            regime = "BULL"
            regime_confidence = min(0.9, 0.5 + abs(avg_rolling_return) * 2)
        elif avg_rolling_return < -0.10:
            regime = "BEAR"
            regime_confidence = min(0.9, 0.5 + abs(avg_rolling_return) * 2)
        else:
            regime = "SIDEWAYS"
            regime_confidence = max(0.5, 0.8 - abs(avg_rolling_return) * 3)
        
        logging.debug(f"🏷️ Regime: {regime} (confidence: {regime_confidence:.2f})")
        return regime
    
    def self_improve_strategies(self):
        trades = self.config.get("trade_history", [])
        
        # CRITICAL: Exclude emergency trades from reflection pool (D-025)
        # Emergency sells (stop-loss triggered or manual close) should NOT influence
        # strategy tuning because they are reactive, not signal-based decisions.
        # Include only STRATEGIC trades (RSI buy + RSI sell signals).
        strategic_trades = []
        emergency_count = 0
        
        for t in trades[-25:]:  # Load last 25 outcomes (PRIMARY GOAL spec requirement)
            # Check for stop-loss triggered or emergency markers
            if t.get("stop_loss_triggered", False):
                emergency_count += 1
                continue
            
            if t.get("note") and "Emergency" in t["note"]:
                emergency_count += 1
                continue
            
            strategic_trades.append(t)
        
        logging.info(f"📊 Filtered trades for reflection: {len(strategic_trades)} strategic / {emergency_count} emergency excluded (D-025)")
        
        # D-025/Cadence gate: Only proceed if we have enough STRATEGIC trades
        # Reflection should NEVER fire based on emergency trades alone
        reflection_cadence = self.config.get("reflection_cadence", 3)
        evaluation_window_size = self.config.get("evaluation_window_size", 20)
        
        if len(strategic_trades) < reflection_cadence:
            logging.info(f"⏳ Not enough strategic trades ({len(strategic_trades)}/{reflection_cadence}) - skipping reflection")
            return
        
        # Statistical Window Fix: Decouple cadence trigger from evaluation window
        # Use broader window (default 20) for stable metric calculation
        evaluation_slice = min(evaluation_window_size, len(strategic_trades))
        evaluation_trades = strategic_trades[-evaluation_slice:]
        
        # CRITICAL: Use net PnL for fee-aware evaluation (v2.5+ upgrade)
        returns = []
        for t in evaluation_trades:
            pnl_pct = t.get('pnl_pct', 0)
            gross_pnl_usd = t.get('gross_pnl_usd', 0)
            net_pnl_usd = t.get('net_pnl_usd', None)
            
            if net_pnl_usd is not None and net_pnl_usd != 0:
                # Fee-inclusive PnL (PRIMARY GOAL: "trades must take fees into account")
                pnl_pct_fee_adjusted = net_pnl_usd / gross_pnl_usd if gross_pnl_usd != 0 else pnl_pct
            else:
                # Fallback to raw pnl_pct if fee data not available
                pnl_pct_fee_adjusted = pnl_pct
            
            returns.append(pnl_pct_fee_adjusted)
        
        if not returns: return
        
        # Calculate performance metrics using fee-adjusted returns
        avg_return = np.mean(returns)
        max_drawdown = self._calculate_max_drawdown(evaluation_trades)
        sharpe = self._calculate_sharpe(returns)

        target_ret = self.config["target_daily_return"]
        target_dd = self.config["max_daily_drawdown"]
        target_sharpe = self.config["min_sharpe_ratio"]

        performance_ok = (avg_return >= target_ret and max_drawdown <= target_dd and sharpe >= target_sharpe)

        # Tag regime BEFORE hypothesis generation (PRIMARY GOAL: "ask what market regime we're in")
        # Multi-timeframe regime: fetch dedicated daily macro data for 20-day rolling return analysis
        try:
            daily_ohlcv = self.exchange.fetch_ohlcv(self.config["target_asset"], timeframe='1d', limit=30)
            daily_df = pd.DataFrame(daily_ohlcv, columns=['ts', 'o', 'h', 'l', 'c', 'v'])
            current_regime = self._tag_regime(daily_df)
            logging.info(f"📊 Market Regime (20-day macro): {current_regime}")
        except Exception as e:
            logging.warning(f"⚠️ Could not fetch daily OHLCV for regime tagging: {e}, using INSUFFICIENT_DATA")
            current_regime = "INSUFFICIENT_DATA"

        if performance_ok:
            logging.info(f"✅ Performance OK (Ret:{avg_return:.4%}, DD:{max_drawdown:.4%}, Sharpe:{sharpe:.2f})")
        else:
            logging.warning(f"❌ Performance Alert! Ret: {avg_return:.4%}, DD: {max_drawdown:.4%}, Sharpe: {sharpe:.2f}")
            
            # VERSION TRACKING + ROLLBACK (Phase 2 implementation)
            version = self.config.get("version", 1)
            previous_strategies = self.config.get("previous_strategies", [])
            
            # Save current strategy as backup before applying change
            current_strategy_snapshot = dict(self.config["current_strategy"])
            backup_entry = {
                "timestamp": datetime.now().isoformat(),
                "version": version,
                "strategy": current_strategy_snapshot
            }
            # Avoid duplicate snapshot if strategy unchanged since last backup
            if previous_strategies and current_strategy_snapshot == previous_strategies[-1]["strategy"]:
                logging.debug(f"📋 Strategy unchanged since v{version}, skipping duplicate backup")
            else:
                previous_strategies.append(backup_entry)
                self.config["previous_strategies"] = previous_strategies
                logging.info(f"💾 Saved strategy backup v{version} for rollback capability")
            

            # Generate hypotheses with regime-aware reasoning + pre-commit backtest validation (PRIMARY GOAL spec)
            # Returns version increment flag based on whether hypothesis was actually applied
            hypothesis_applied = self._generate_and_apply_hypotheses(current_regime=current_regime, avg_ret=avg_return, max_dd=max_drawdown, sharpe=sharpe)
            
            # Only increment version if hypothesis was actually applied and saved
            if hypothesis_applied:
                # B-013/D-048 fix: Track rollback condition for verification after next trade
                if sharpe < 0:
                    self.config["needs_rollback"] = True
                    logging.info(f"⚠️ Performance failing (Sharpe: {sharpe:.2f}) - will verify after next trade")
                else:
                    self.config["needs_rollback"] = False
                
                version += 1
                self.config["version"] = version
                logging.info(f"⬆️ Version incremented from {version-1} → {version}")
                save_config(self.config)
            
    def restore_strategy(self, target_version=None):
        """Restore to a specific strategy version (PRIMARY GOAL: rollback capability).
        
        Args:
            target_version: Restore to this version number. If None, restores to latest backup.
        
        Returns:
            dict: Information about the restored strategy, or None if no backups available.
        """
        previous_strategies = self.config.get("previous_strategies", [])
        current_version = self.config.get("version", 1)

        # If target_version is None, restore to latest backup
        if target_version is None:
            if not previous_strategies:
                logging.warning("⚠️ No strategy backups available for rollback.")
                return None
            target_version = previous_strategies[-1]["version"]
        else:
            # Validate version exists in backups
            available_versions = [s["version"] for s in previous_strategies]
            if target_version not in available_versions:
                logging.error(f"⚠️ Version {target_version} not found. Available versions: {available_versions}")
                return None

        # Find and restore the backup
        for backup in previous_strategies:
            if backup["version"] == target_version:
                logging.info(f"🔄 Restoring strategy to version {target_version}")
                
                # Restore strategy parameters
                self.config["current_strategy"] = dict(backup["strategy"])
                
                # Record the rollback in ledger
                rollback_record = {
                    "timestamp": datetime.now().isoformat(),
                    "action": "restore",
                    "restored_to_version": target_version,
                    "metrics_before_restore": {
                        # B-005 fix: these locals belong to self_improve_strategies(), not here.
                        # Rollback is called externally so metrics context is unavailable — record None.
                        "version": current_version,
                        "return": None,
                        "drawdown": None,
                        "sharpe": None
                    }
                }
                self.config["hypothesis_ledger"].append(rollback_record)
                
                # Save and increment version to track rollback as an event
                self.config["version"] = target_version + 1  # Next available version after rollback
                save_config(self.config)
                
                logging.info(f"✅ Strategy restored to v{target_version}, now at v{self.config['version']}")
                return {
                    "status": "success",
                    "restored_version": target_version,
                    "current_version": self.config["version"],
                    "strategy": self.config["current_strategy"]
                }

        logging.warning("⚠️ Restore operation completed but no strategy found to restore.")
        return None

    def _calculate_max_drawdown(self, trades):
        if not trades: return 0
        cumulative = 1.0
        peak = 1.0
        max_dd = 0
        for t in trades:
            pnl = t.get('pnl_pct', 0)
            cumulative *= (1 + pnl)
            if cumulative > peak: peak = cumulative
            dd = (peak - cumulative) / peak
            if dd > max_dd: max_dd = dd
        return max_dd

    def _calculate_sharpe(self, returns):
        if len(returns) < 2 or np.std(returns) == 0: return 0
        return np.mean(returns) / np.std(returns)

    def _run_local_backtest(self, ohlcv_data, strategy_dict):
        """Simulate strategy performance on historical OHLCV data (look-before-you-leap safety gate)."""
        if len(ohlcv_data) < strategy_dict.get("rsi_period", 14) + 20:
            return 0.0
        
        fee_pct = self.config.get("kraken_fee_pct", 0.0026)
        prices = np.array([bar[4] for bar in ohlcv_data])  # Close prices
        rsi_period = strategy_dict.get("rsi_period", 14)
        indicator_threshold = strategy_dict.get("indicator_threshold", 63.0)
        stop_loss_pct = strategy_dict.get("stop_loss_pct", 0.016)
        sell_threshold_base = strategy_dict.get("sell_threshold_base", 10)
        trend_lookback = strategy_dict.get("trend_filter_lookback", 20)
        
        position_btc = 0.0
        entry_price = 0.0
        entry_rsi = None
        net_roi = 0.0
        
        for i in range(len(prices)):
            current_price = prices[i]
            
            # Calculate RSI up to current point
            rsi_val = self.calculate_rsi(prices[:i+1], rsi_period)
            
            # Calculate dynamic sell threshold
            if position_btc > 0 and entry_rsi is not None:
                fee_hurdle = 2 * fee_pct
                est_rsi_change = self._estimate_rsi_change_for_price_change(fee_hurdle)
                sell_threshold = max(entry_rsi + est_rsi_change + sell_threshold_base, indicator_threshold + sell_threshold_base)
            else:
                sell_threshold = indicator_threshold + sell_threshold_base * 2
            
            # Stop-loss check (simulated)
            if position_btc > 0 and current_price < entry_price:
                sl_threshold = entry_price * (1 - stop_loss_pct)
                if current_price < sl_threshold:
                    # Simulate stop-loss exit
                    trade_value = position_btc * entry_price
                    pnl_usd = position_btc * current_price * (current_price - entry_price) / entry_price
                    fee_usd = round(trade_value * fee_pct * 2, 6)
                    net_pnl = pnl_usd - fee_usd
                    net_roi += net_pnl / trade_value if trade_value > 0 else 0
                    position_btc = 0.0
                    entry_price = 0.0
                    entry_rsi = None
                    continue
            
            # Buy signal (if no position)
            if position_btc == 0 and rsi_val < indicator_threshold:
                # Trend filter check
                if i >= trend_lookback:
                    if current_price <= prices[i - trend_lookback]:
                        continue  # Skip if declining over lookback period
                # Simulate buy
                position_btc = 0.037  # Normalized position size for backtest
                entry_price = current_price
                entry_rsi = rsi_val
            
            # Sell signal (if in position)
            elif position_btc > 0 and rsi_val > sell_threshold:
                trade_value = position_btc * entry_price
                pnl_usd = position_btc * current_price * (current_price - entry_price) / entry_price
                potential_fee = round(trade_value * fee_pct * 2, 6)
                net_pnl = round(pnl_usd - potential_fee, 6)
                if net_pnl > 0:  # Only count profitable exits
                    net_roi += net_pnl / trade_value
                position_btc = 0.0
                entry_price = 0.0
                entry_rsi = None
        
        return net_roi

    def _generate_and_apply_hypotheses(self, current_regime="NEUTRAL", avg_ret=None, max_dd=None, sharpe=None):
        """Generate 1-3 hypotheses with regime-aware reasoning + pre-commit backtest validation (PRIMARY GOAL spec).
        
        Each hypothesis must:
        - modify exactly ONE variable in strategy
        - predict expected score direction (improve/degrade)
        - pass backtest validation vs baseline strategy
        
        Then apply highest-backtested-return hypothesis only.
        """
        strat = self.config["current_strategy"]
        keys = list(strat.keys())
        
        # Fetch deep historical slice ONCE for backtesting (sequential, rate-limited)
        try:
            backtest_ohlcv = self.exchange.fetch_ohlcv(self.config["target_asset"], timeframe='1m', limit=500)
        except Exception as e:
            logging.warning(f"⚠️ Could not fetch backtest data: {e}, skipping hypothesis generation")
            return False
        
        # Establish baseline performance BEFORE any mutations
        baseline_return = self._run_local_backtest(backtest_ohlcv, strat)
        logging.info(f"📊 Baseline backtest return: {baseline_return:.4%}")
        
        # Generate regime-aware hypotheses for each parameter
        generated_hypotheses = []
        
        regime_tuning_map = {
            "BULL": {
                "indicator_threshold": {"direction": "lower", "new_value_multiplier": 0.9, "reasoning": "Aggressive buying on pullbacks in strong uptrend"},
                "sell_threshold_base": {"direction": "lower", "new_value_multiplier": 0.75, "reasoning": "Tighter sell buffer to capture quick gains in uptrend"},
                "stop_loss_pct": {"direction": "tighter", "new_value_multiplier": 0.9, "reasoning": "Protect aggressive gains in bull market"},
                "position_size_pct": {"direction": "increase", "new_value_multiplier": 1.2, "reasoning": "Take advantage of favorable conditions"},
                "trend_filter_lookback": {"direction": "shorter", "new_value_multiplier": 0.5, "reasoning": "Shorter lookback for quick trend detection in uptrend"},
                "ohlcv_limit": {"direction": "shorter", "new_value_multiplier": 0.75, "reasoning": "Less history for faster signal in uptrend"},
                "ohlcv_timeframe": {"direction": "maintain_current", "new_value_multiplier": 1.0, "reasoning": "Keep 1m for responsive signals in uptrend"}
            },
            "BEAR": {
                "indicator_threshold": {"direction": "higher", "new_value_multiplier": 1.05, "reasoning": "Wait for better confirmation in weak downtrend"},
                "sell_threshold_base": {"direction": "higher", "new_value_multiplier": 1.25, "reasoning": "Wider sell buffer to avoid premature exits in choppy bear market"},
                "stop_loss_pct": {"direction": "wider", "new_value_multiplier": 1.2, "reasoning": "Prevent premature exits during normal bear volatility"},
                "position_size_pct": {"direction": "decrease", "new_value_multiplier": 0.8, "reasoning": "Reduce exposure in unfavorable regime"},
                "rsi_period": {"direction": "longer", "new_value_multiplier": 1.33, "reasoning": "Smoother RSI in choppy bear market"},
                "trend_filter_lookback": {"direction": "longer", "new_value_multiplier": 2.0, "reasoning": "Longer lookback for trend confirmation in bear market"},
                "ohlcv_limit": {"direction": "longer", "new_value_multiplier": 1.5, "reasoning": "More history for stability signal in bear market"},
                "ohlcv_timeframe": {"direction": "longer_tf", "reasoning": "Use 5m for more stable signals in bear market"}
            },
            "SIDEWAYS": {
                "indicator_threshold": {"direction": "stricter", "new_value_multiplier": 0.95, "reasoning": "Require stronger signals to cut through noise"},
                "sell_threshold_base": {"direction": "higher", "new_value_multiplier": 1.2, "reasoning": "Wider sell buffer to avoid whipsaw exits in chop"},
                "stop_loss_pct": {"direction": "wider", "new_value_multiplier": 1.1, "reasoning": "Avoid whipsaws in range-bound market"},
                "position_size_pct": {"direction": "slightly_increase", "new_value_multiplier": 1.05, "reasoning": "Compensate for lower win rate in chop"},
                "rsi_period": {"direction": "longer", "new_value_multiplier": 1.33, "reasoning": "Smoother RSI in choppy sideways market"},
                "sl_cooldown_seconds": {"direction": "longer", "new_value_multiplier": 1.5, "reasoning": "Extended cooldown to avoid chop re-triggers"},
                "trend_filter_lookback": {"direction": "longer", "new_value_multiplier": 1.5, "reasoning": "Longer lookback for trend confirmation in choppy sideways"},
                "ohlcv_limit": {"direction": "longer", "new_value_multiplier": 1.5, "reasoning": "More history for better regime detection in chop"},
                "ohlcv_timeframe": {"direction": "longer_tf", "reasoning": "Use 5m for smoother signals in choppy market"}
            },
            "NEUTRAL": {
                "indicator_threshold": {"direction": "adjust_toward_optimal", "new_value_multiplier": None, "reasoning": "Fine-tune based on signal frequency"},
                "sell_threshold_base": {"direction": "maintain_current", "new_value_multiplier": 1.0, "reasoning": "Stable buffer for neutral conditions"},
                "stop_loss_pct": {"direction": "maintain_current", "new_value_multiplier": 1.0, "reasoning": "Risk already calibrated"},
                "position_size_pct": {"direction": "fine_tune", "new_value_multiplier": None, "reasoning": "Adjust based on risk/reward ratio"},
                "rsi_period": {"direction": "maintain_current", "new_value_multiplier": 1.0, "reasoning": "14-period standard; extend in choppy BEAR, shorten in trending BULL"},
                "sl_cooldown_seconds": {"direction": "maintain_current", "new_value_multiplier": 1.2, "reasoning": "Slight extension in neutral conditions"},
                "trend_filter_lookback": {"direction": "maintain_current", "new_value_multiplier": 1.0, "reasoning": "Standard 20-period lookback"},
                "ohlcv_limit": {"direction": "maintain_current", "new_value_multiplier": 1.0, "reasoning": "Standard 50-period OHLCV"}
            },
        }
        
        regime_recs = regime_tuning_map.get(current_regime, regime_tuning_map["NEUTRAL"])
        
        for key in keys:
            old_val = strat[key]
            new_val_multiplier = regime_recs[key]["new_value_multiplier"]
            
            if new_val_multiplier is None:
                continue
            
            if key == "indicator_threshold":
                new_val = round(old_val * new_val_multiplier, 2)
            elif key == "sell_threshold_base":
                new_val = int(max(5, min(20, round(old_val * new_val_multiplier))))
            elif key == "stop_loss_pct":
                new_val = round(strat[key] * new_val_multiplier, 4)
            elif key == "position_size_pct":
                new_val = round(old_val * new_val_multiplier, 3)
            elif key == "rsi_period":
                new_val = int(max(5, min(30, round(old_val * new_val_multiplier))))
            elif key == "sl_cooldown_seconds":
                new_val = int(max(60, min(600, round(old_val * new_val_multiplier))))
            elif key == "trend_filter_lookback":
                new_val = int(max(5, min(50, round(old_val * new_val_multiplier))))
            elif key == "ohlcv_limit":
                new_val = int(max(20, min(100, round(old_val * new_val_multiplier))))
            elif key == "ohlcv_timeframe":
                if new_val_multiplier == 1.0 or "longer_tf" not in regime_recs[key]["direction"]:
                    new_val = old_val
                elif old_val == "1m":
                    new_val = "5m"
                else:
                    new_val = "1m"
            
            expected_direction = "improve" if avg_ret < 0 or max_dd > 0.01 else "stabilize"
            
            regime_confidence_boost = 0.2 if current_regime in ["BULL", "BEAR"] else 0.0
            confidence = round(max(0.5, min(0.9, regime_confidence_boost)), 2)
            
            # Create temporary strategy for backtest
            test_strat = dict(strat)
            test_strat[key] = new_val
            test_strat["ohlcv_limit"] = 500  # Use full backtest data
            
            # Run backtest for this proposed change
            backtest_return = self._run_local_backtest(backtest_ohlcv, test_strat)
            
            hypothesis_entry = {
                "timestamp": datetime.now().isoformat(),
                "description": f"Adjusting {key} from {old_val} to {new_val:.4f}",
                "metrics_at_failure": {"return": avg_ret, "drawdown": max_dd, "sharpe": sharpe},
                "regime_tag": current_regime,
                "expected_score_direction": expected_direction,
                "confidence": confidence,
                "confidence_reasoning": f"{current_regime} market + {'performance degraded' if avg_ret < 0 else 'optimization mode'} → {new_val_multiplier*100:.0f}% {'increase' if new_val_multiplier > 1 else 'decrease' if new_val_multiplier < 1 else 'adjust'} to {regime_recs[key]['reasoning']}",
                "simulated_backtest_return": backtest_return,
                "baseline_backtest_return": baseline_return
            }
            generated_hypotheses.append(hypothesis_entry)
        
        if not generated_hypotheses:
            logging.info("No hypotheses generated for current regime and performance context.")
            return False
        
        # GATING CRITERIA: Select hypothesis with highest backtest return that beats baseline
        best_hyp = max(generated_hypotheses, key=lambda h: h["simulated_backtest_return"])
        
        if best_hyp["simulated_backtest_return"] <= baseline_return:
            logging.info(f"⚠️ Hypothesis backtest failed validation: best return ({best_hyp['simulated_backtest_return']:.4%}) did not beat baseline ({baseline_return:.4%}). No strategy change this cycle.")
            return False
        
        # Apply the selected hypothesis (ONE variable change — PRIMARY GOAL hard constraint)
        import re
        param_match = re.search(r'Adjusting (\w+) from ([^ ]+) to ([^%\s]+)', best_hyp["description"])
        if not param_match:
            logging.error(f"Could not parse hypothesis description: {best_hyp['description']}.")
            return
        
        param_name = param_match.group(1)
        new_val_text = param_match.group(3)
        
        old_val = strat[param_name]
        strat[param_name] = float(new_val_text)
        
        if strat[param_name] == old_val:
            logging.error(f"⚠️ Hypothesis application FAILED: {param_name} didn't change ({old_val} → {strat[param_name]})")
            return False
        
        logging.info(f"✅ Applied hypothesis: {param_name} changed from {old_val:.4f} to {strat[param_name]:.4f} (backtest: {best_hyp['simulated_backtest_return']:.4%} > baseline: {baseline_return:.4%})")
        
        # Log and record hypothesis in ledger (PRIMARY GOAL: append-only history)
        hypothesis_record = {
            "timestamp": datetime.now().isoformat(),
            "description": best_hyp["description"],
            "metrics_at_failure": best_hyp.get("metrics_at_failure", {}),
            "regime_tag": current_regime,
            "regime": current_regime,
            "parameter": param_name,
            "old_value": old_val,
            "new_value": strat[param_name],
            "expected_score_direction": best_hyp.get("expected_score_direction"),
            "direction": best_hyp.get("expected_score_direction"),
            "confidence_reasoning": best_hyp.get("confidence_reasoning"),
            "simulated_backtest_return": best_hyp.get("simulated_backtest_return"),
            "baseline_backtest_return": best_hyp.get("baseline_backtest_return")
        }
        self.config["hypothesis_ledger"].append(hypothesis_record)
        
        logging.info(f"🛠️ APPLYING HYPOTHESIS ({current_regime}): {best_hyp['description']} (backtest: {best_hyp['simulated_backtest_return']:.4%})")
        
        save_config(self.config)
        return True

    def _is_uptrend(self, prices, lookback=20):
        """Check if price is in uptrend (simple moving average comparison)."""
        if len(prices) < lookback:
            return True  # Assume uptrend if insufficient data
        current = prices[-1]
        past = prices[-lookback]
        return current > past  # Uptrend if current price > price 'lookback' periods ago

    def _position_age_hours(self):
        """Return hours since position was opened, or 0 if no position."""
        pos = self.config.get("open_position")
        if not pos or not pos.get("timestamp"):
            return 0
        try:
            opened = datetime.fromisoformat(pos["timestamp"])
            return (datetime.now() - opened).total_seconds() / 3600
        except Exception:
            return 0

    def run_cycle(self):
        # Reload config from disk each cycle to pick up external writes
        # (e.g. EMERGENCY_STOP set by emergency_stop_trader.py, manual edits) — B-007 fix.
        self.config = load_config()
        # Restore cooldown state after config reload
        self.sl_cooldown_until = self.config.get("sl_cooldown_until", 0)
        symbol = self.config["target_asset"]
        rsi_period = self.config["current_strategy"].get("rsi_period", 14)  # D-062: tunable RSI period
        # Emergency STOP check – if active, log and skip this cycle
        if self.config.get("system_status") == "EMERGENCY_STOP":
            logging.warning("🚨 EMERGENCY STOP ACTIVE – skipping all trading logic this cycle")
            return
        
        # Clean expired cooldown
        if self.sl_cooldown_until and time.time() >= self.sl_cooldown_until:
            self.sl_cooldown_until = 0
            if "sl_cooldown_until" in self.config:
                del self.config["sl_cooldown_until"]
                save_config(self.config)
            logging.info("🧹 Stop-loss cooldown expired - cleared from config")
        
        # Get current ticker price for real-time price monitoring (for stop-loss)
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            current_price = float(ticker['last'])
        except Exception as e:
            logging.warning(f"⚠️ Could not fetch ticker: {e}")
            current_price = None  # Will use OHLCV close if ticker fails
        
        try:
            ohlcv_limit = self.config['current_strategy'].get('ohlcv_limit', 50)
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe='1m', limit=ohlcv_limit)
            df = pd.DataFrame(ohlcv, columns=['ts', 'o', 'h', 'l', 'c', 'v'])
            prices = df['c'].values

            # Use ticker price if available, otherwise fallback to OHLCV close
            if current_price is None:
                current_price = float(prices[-1])
            
            rsi_val = self.calculate_rsi(prices, rsi_period)
            threshold = self.config["current_strategy"]["indicator_threshold"]
            buy_threshold = threshold
            
            # Calculate dynamic sell threshold based on fee requirements when in position
            if self.current_position == 'long' and self.entry_rsi is not None:
                # Calculate price change needed to cover fees (round trip)
                kraken_fee_pct = self.config.get("kraken_fee_pct", 0.0026)
                fee_hurdle_pct = 2 * kraken_fee_pct  # Entry + exit fees
                
                # Estimate what RSI change corresponds to overcoming the fee hurdle
                estimated_rsi_change_needed = self._estimate_rsi_change_for_price_change(fee_hurdle_pct)
                
                # Dynamic sell threshold: entry RSI + estimated change needed + configurable buffer
                sell_threshold_base = self.config["current_strategy"].get("sell_threshold_base", 10)
                estimated_rsi_change_needed = round(self._estimate_rsi_change_for_price_change(fee_hurdle_pct), 2)
                dynamic_sell_threshold = self.entry_rsi + estimated_rsi_change_needed + sell_threshold_base
                sell_threshold = round(max(dynamic_sell_threshold, threshold + sell_threshold_base), 2)  # Ensure minimum threshold, rounded to 2 decimals
                logging.debug(f"📊 Dynamic sell threshold: {sell_threshold:.2f} (entry RSI: {self.entry_rsi:.2f}, fee hurdle: {fee_hurdle_pct:.4%}, est RSI change: {estimated_rsi_change_needed:.2f})")
            else:
                # Default fixed threshold when no position or entry RSI not tracked
                sell_threshold_base = self.config["current_strategy"].get("sell_threshold_base", 10)
                sell_threshold = round(threshold + sell_threshold_base * 2)  # Double buffer when no position context
            
            logging.info(f"📊 {symbol} | RSI: {rsi_val:.2f} | Threshold: {threshold}")

            # ===== STOP-LOSS CHECK (Priority #1 - Risk Management) =====
            # Execute immediate exit if price dropped more than stop_loss_pct below entry
            open_position = self.config.get("open_position")
            if open_position and current_price < open_position["entry_price"]:
                entry_price = open_position["entry_price"]
                stop_loss_threshold = entry_price * (1 - self.config["current_strategy"]["stop_loss_pct"])
                if current_price < stop_loss_threshold:
                    logging.warning(f"🚨 STOP-LOSS TRIGGERED! Price ${current_price:.2f} < SL threshold ${stop_loss_threshold:.2f}")
                    try:
                        balance = self.exchange.fetch_balance()
                        btc_free = balance.get('BTC', {}).get('free', 0) or open_position.get("amount_btc", 0)
                        if btc_free > 0:
                            # Use current_price already resolved at top of cycle (OHLCV fallback safe).
                            # Do NOT re-access ticker['last'] here — ticker may be unbound if fetch failed (B-001 fix).
                            cli_sym = symbol.replace("/", "").replace("USDT", "USD")
                            logging.info(f"🚨 Executing Emergency SELL Order via Stop-Loss: {btc_free:.6f} {symbol} @ ${current_price:.2f}")
                            self.exchange.create_market_sell_order(cli_sym, btc_free)
                            
                            pnl_pct = (current_price - entry_price) / entry_price
                            trade_value_sl = open_position["amount_btc"] * entry_price
                            pnl_usd = open_position["amount_btc"] * current_price * pnl_pct
                            # Fee-aware fields (stop-loss path)
                            kraken_fee_pct = self.config.get("kraken_fee_pct", 0.0026)
                            fee_usd = round(trade_value_sl * kraken_fee_pct * 2, 6)  # fee on entry + exit legs
                            gross_pnl_usd = round(pnl_usd, 6)
                            net_pnl_usd = round(pnl_usd - fee_usd, 6)
                            trade_record = {
                                "timestamp": datetime.now().isoformat(),
                                "entry": entry_price, "exit": current_price,
                                "pnl_pct": pnl_pct, "symbol": symbol,
                                "pnl_usd": pnl_usd,
                                "gross_pnl_usd": gross_pnl_usd,
                                "fee_usd": fee_usd,
                                "net_pnl_usd": net_pnl_usd,
                                "stop_loss_triggered": True
                            }
                            if "open_position" in self.config:
                                del self.config["open_position"]
                            self.config["trade_history"].append(trade_record)
                            self.config["sl_cooldown_until"] = time.time() + DEFAULT_SL_COOLDOWN
                            save_config(self.config)
                            self.current_position = None
                            self.entry_price = None
                            self.entry_rsi = None
                            self.sl_cooldown_until = time.time() + DEFAULT_SL_COOLDOWN
                            logging.info(f"💰 TRADE CLOSED: PnL: {pnl_pct:.4%} (${pnl_usd:.2f}) | Gross: ${gross_pnl_usd:.4f} | Fee: ${fee_usd:.4f} | Net: ${net_pnl_usd:.4f}")
                            logging.info(f"⏳ Stop-loss cooldown activated for {DEFAULT_SL_COOLDOWN}s")
                            return
                        else:
                            logging.warning("⚠️ No BTC available to close on stop-loss.")
                    except Exception as e:
                        logging.error(f"❌ Stop-Loss Sell Order Failed: {e}")
                        self.current_position = None
                        self.entry_price = None
                        self.entry_rsi = None
                        return
                    # ===============================
            # ===============================

            # ===== TREND FILTER / COOLDOWN CHECK (T-018 / T-029) =====            # Don't buy if price is in sustained downtrend - reduces consecutive stop-loss risk
            # T-029: Check stop-loss cooldown before allowing BUY (must run when no position)
            if self.sl_cooldown_until and time.time() < self.sl_cooldown_until:
                remaining = int(self.sl_cooldown_until - time.time())
                logging.info(f"⏳ In stop-loss cooldown ({remaining}s remaining) - skipping BUY signal")
                return

            # ===== BUY BRANCH: RSI below threshold, no open position =====
            if rsi_val < buy_threshold and self.current_position is None:
                if not self._is_uptrend(prices):
                    logging.info(f"📉 Skipping BUY - trend filter signals DOWNTREND (price declining over 20m)")
                    return

                try:
                    balance = self.exchange.fetch_balance()
                    usdt_free = balance.get('USDT', {}).get('free', 0) or balance.get('USD', {}).get('free', 0)

                    amount_to_spend = usdt_free * self.config['current_strategy']['position_size_pct']

                    if amount_to_spend > 1:
                        current_price = prices[-1]
                        cli_sym = symbol.replace("/", "").replace("USDT", "USD")
                        btc_amount = amount_to_spend / current_price

                        logging.info(f"🛒 Executing BUY Order: {btc_amount:.6f} {symbol} @ ~{current_price:.2f}")
                        self.exchange.create_market_buy_order(cli_sym, btc_amount)

                        self.last_trade_usd_amount = amount_to_spend
                        self.current_position = 'long'
                        self.entry_rsi = rsi_val  # Track RSI at entry for dynamic sell threshold

                        # Track open position with timestamp for persistence
                        # Accumulate BTC amount and weighted average entry price if position exists
                        existing_pos = self.config.get("open_position", {})
                        accumulated_btc = existing_pos.get("amount_btc", 0) + btc_amount

                        # Calculate weighted average entry price using value-weighted formula
                        # Formula: (value1 + value2) / total_amount
                        existing_value = existing_pos.get("amount_btc", 0) * existing_pos.get("entry_price", current_price)
                        new_value = btc_amount * current_price
                        total_value = existing_value + new_value

                        avg_price = round(total_value / accumulated_btc, 2) if accumulated_btc > 0 else current_price

                        self.config["open_position"] = {
                            "timestamp": datetime.now().isoformat(),
                            "symbol": symbol,
                            "entry_price": avg_price,
                            "entry_rsi": self.entry_rsi,
                            "amount_btc": accumulated_btc
                        }

                        # Update instance variable with weighted average entry price for PnL calculations
                        self.entry_price = avg_price

                        # Persist immediately after position open
                        save_config(self.config)
                        logging.info(f"📝 Open Position Updated: {accumulated_btc:.6f} BTC @ ${avg_price:.2f} (weighted avg)")
                        logging.info(f"✅ BUY Order Placed. Entry Price: {current_price:.2f}")

                except Exception as e:
                    logging.error(f"❌ Buy Order Failed: {e}")

            # ===== SELL BRANCH: RSI above threshold, position open =====
            elif rsi_val > sell_threshold and self.current_position == 'long':
                try:
                    # Calculate potential profit/loss after fees before selling
                    current_price = prices[-1]
                    potential_pnl_pct = (current_price - self.entry_price) / self.entry_price
                    potential_pnl_usd = self.last_trade_usd_amount * potential_pnl_pct
                    kraken_fee_pct = self.config.get("kraken_fee_pct", 0.0026)
                    trade_value = self.last_trade_usd_amount
                    potential_fee_usd = round(trade_value * kraken_fee_pct * 2, 6)  # fee on entry + exit legs
                    potential_net_pnl_usd = round(potential_pnl_usd - potential_fee_usd, 6)
                    
                    # Only sell if net profit after fees is positive (avoid fee trap)
                    if potential_net_pnl_usd <= 0:
                        logging.info(f"💡 Holding position: Selling would result in net loss after fees (Net: ${potential_net_pnl_usd:.4f}). Waiting for better price.")
                        return
                    
                    balance = self.exchange.fetch_balance()
                    btc_free = balance.get('BTC', {}).get('free', 0)
                    if btc_free > 0:
                        cli_sym = symbol.replace("/", "").replace("USDT", "USD")
                        logging.info(f"🛒 Executing SELL Order: {btc_free:.6f} {symbol} @ ~{current_price:.2f}")
                        self.exchange.create_market_sell_order(cli_sym, btc_free)
                        
                        # Removed: No longer crediting virtual sub-account with PnL (shadow accounting deprecated)
                        pnl_pct = potential_pnl_pct
                        pnl_usd = potential_pnl_usd
                        fee_usd = potential_fee_usd
                        gross_pnl_usd = round(pnl_usd, 6)
                        net_pnl_usd = potential_net_pnl_usd

                        trade_record = {
                            "timestamp": datetime.now().isoformat(),
                            "entry": self.entry_price, "exit": current_price,
                            "pnl_pct": pnl_pct, "symbol": symbol, "pnl_usd": pnl_usd,
                            "gross_pnl_usd": gross_pnl_usd,
                            "fee_usd": fee_usd,
                            "net_pnl_usd": net_pnl_usd
                        }
                        
                        # Remove open_position when trade closes
                        if "open_position" in self.config:
                            del self.config["open_position"]
                        self.config["trade_history"].append(trade_record)
                        logging.info(f"💰 TRADE CLOSED (RSI Signal): PnL: {pnl_pct:.4%} (${pnl_usd:.2f})")
                        save_config(self.config)
                        self.current_position = None
                        self.entry_price = None
                        self.entry_rsi = None  # Reset entry RSI tracking
                        
                        # Self-improvement check after every trade completes
                        self.self_improve_strategies()
                    else:
                        # No BTC available to sell after trade closed - this is normal, no warning needed
                        # Clear position data when cannot close
                        self.current_position = None
                        self.entry_price = None
                except Exception as e:
                     logging.error(f"❌ Sell Order Failed: {e}")
                     # Reset state on failure
                     self.current_position = None
                     self.entry_price = None
                     self.entry_rsi = None  # Reset entry RSI tracking
            
            else:
                # Explain why we're waiting for more clarity in logs
                if self.current_position is None:
                    # We don't have a position - waiting for BUY signal
                    waiting_reason = f"Waiting for RSI to drop below {buy_threshold} to buy"
                else:
                    # We have a position - waiting for SELL signal  
                    waiting_reason = f"Waiting for RSI to rise above {sell_threshold} to sell"
                logging.info(f"💤 {waiting_reason} (RSI {rsi_val:.2f}, buy {buy_threshold}, sell {sell_threshold})")

            # ===== POSITION TIMEOUT CHECK (T-018 / L-004) =====
            # Warn if position open >24h without close signal (runs every cycle, independent of BUY/SELL)
            if self.current_position == 'long':
                pos_age = self._position_age_hours()
                if pos_age > 24:
                    logging.warning(f"⚠️ POSITION TIMEOUT: Open for {pos_age:.1f}h - consider manual review")

        except Exception as e:
            logging.error(f"❌ Cycle Error: {str(e)}")


def LIVE_TRADING_CRITICAL_CHECK(enabled):
    return enabled

if __name__ == "__main__":
    logging.info("🤖 Online Trader-3 starting... (Check trader.log)")
    trader = OnlineTrader()
    while True:
        try:
            trader.run_cycle()
            time.sleep(60)
        except KeyboardInterrupt:
            logging.info("🛑 Shutdown requested.")
            break
        except Exception as e:
            logging.error(f"Critical Loop Error: {e}")
            time.sleep(30)
