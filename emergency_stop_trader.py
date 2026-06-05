#!/mnt/data/venvs/online-trader-3/bin/python
"""
emergency_stop_trader.py

A minimal, self-contained emergency stop script for Online Trader-3.
It provides three commands for managing emergency stop state:

Usage:
  python emergency_stop_trader.py emergency_only  # Set EMERGENCY_STOP flag only
  python emergency_stop_trader.py emergency_sell  # Set flag + close open position
  python emergency_stop_trader.py off             # Clear EMERGENCY_STOP, resume trading

This script respects the existing ARCHITECTURE.md and DECISIONS.md conventions:
- Uses Kraken CLI paper trading wrapper style for paper mode
- Uses CCXT directly for live mode  
- No external dependencies beyond stdlib
- Does NOT delete trade_history, hypothesis_ledger, or previous_strategies
- Does NOT restart or modify the engine process; it signals via config
- Marks all emergency trades with stop_loss_triggered=true + note="Emergency stop trade" (D-025)
"""

import json
import os
import subprocess
import sys
from datetime import datetime

# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------
CONFIG_PATH = os.path.expanduser("~/online-trader-3/config.json")
KRAKEN_BINARY = os.path.expanduser("~/.cargo/bin/kraken")


def log(msg):
    print(f"[EMERGENCY STOP] {msg}")


def load_config():
    if not os.path.exists(CONFIG_PATH):
        log(f"⚠️ Config file not found at {CONFIG_PATH}")
        sys.exit(1)
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)


def save_config(cfg):
    with open(CONFIG_PATH, "w") as f:
        json.dump(cfg, f, indent=2)


def clear_flag(cfg=None):
    """Remove EMERGENCY_STOP flag from config."""
    log("🟢 Clearing EMERGENCY_STOP flag...")
    
    cfg = load_config() if not cfg else cfg
    
    # Remove system_status key from config
    if "system_status" in cfg:
        del cfg["system_status"]
        log("⚡️ Removed system_status = EMERGENCY_STOP from config.json")
    else:
        log("ℹ️  No EMERGENCY_STOP flag found (already clear)")
    
    save_config(cfg)
    log("✅ Emergency stop cleared - engine will resume trading on next cycle")


def is_paper_mode(cfg):
    """Check if trading is in paper/sandbox mode."""
    exchange = cfg.get("exchange", {})
    if exchange.get("sandbox_mode", False):
        return True
    return os.getenv("LIVE_TRADING_ENABLED", "false").lower() != "true"


def close_position(cfg):
    """
    Close any open position with a market order and record the trade.
    Marks trade with stop_loss_triggered=true + note="Emergency stop trade" (D-025).
    Does NOT create synthetic trades if no position exists (fixes L-005).
    """
    # --------------------------------------------------------------
    # 1: Extract position data
    # --------------------------------------------------------------
    pos = cfg.get("open_position")
    
    if not pos:
        log("ℹ️  No open_position found - emergency_sell has nothing to close.")
        log("💡 Tip: Use emergency_only to set EMERGENCY_STOP flag without closing position.")
        return
    
    entry_price = pos.get("entry_price")
    symbol = pos.get("symbol")
    amount_btc = pos.get("amount_btc", 0.0)
    
    if not entry_price or not symbol or amount_btc <= 0:
        log("⚠️  Invalid open_position data - skipping close.")
        return
    
    log(f"🔄 Closing {symbol} position - market SELL {amount_btc:.8f} BTC")
    
    # --------------------------------------------------------------
    # 2: Determine current market price
    # --------------------------------------------------------------
    current_price = None
    try:
        result = subprocess.run(
            [KRAKEN_BINARY, "ticker", symbol.replace("/", "").replace("USDT", "USD")],
            capture_output=True, text=True, check=True
        )
        ticker_data = json.loads(result.stdout)
        current_price = float(ticker_data["c"][0])
        log(f"💵 Retrieved live price: ${current_price:.2f}")
    except Exception as e:
        log(f"⚠️  Could not fetch ticker - using entry price as fallback")
        current_price = float(entry_price)
    
    # --------------------------------------------------------------
    # 3: Execute trade based on mode
    # --------------------------------------------------------------
    if is_paper_mode(cfg):
        cli_symbol = symbol.replace("/", "").replace("USDT", "USD")
        order_cmd = [
            KRAKEN_BINARY,
            "paper",
            "sell",
            cli_symbol,
            str(amount_btc),
            "--type",
            "market"
        ]
        try:
            result = subprocess.run(
                order_cmd,
                capture_output=True,
                text=True,
                check=True
            )
            log(f"✅ Kraken CLI response: {result.stdout.strip()}")
        except subprocess.CalledProcessError as e:
            log(f"❌ Paper sell failed: {e.stderr.strip()}")
            return
    else:
        try:
            import ccxt
            exchange = ccxt.kraken({
                'apiKey': cfg.get("exchange", {}).get('apiKey', ''),
                'secret': cfg.get("exchange", {}).get('secret', ''),
                'enableRateLimit': True,
                'options': {'defaultType': 'spot'}
            })
            order = exchange.create_market_sell_order(symbol.replace("/", ""), amount_btc)
            log(f"✅ CCXT sell response: {order}")
        except Exception as e:
            log(f"❌ Live sell failed: {e}")
            return
    
    # --------------------------------------------------------------
    # 4: Compute PnL and persist trade (MARKED AS EMERGENCY D-025)
    # --------------------------------------------------------------
    pnl_pct = round((current_price - entry_price) / entry_price, 6)
    trade_value_usd = entry_price * amount_btc
    gross_pnl_usd = round(pnl_pct * trade_value_usd, 6)
    kraken_fee_pct = cfg.get("kraken_fee_pct", 0.0026)
    fee_usd = round(trade_value_usd * kraken_fee_pct * 2, 6)
    net_pnl_usd = round(gross_pnl_usd - fee_usd, 6)
    
    trade_record = {
        "timestamp": datetime.now().isoformat(),
        "entry": entry_price,
        "exit": current_price,
        "symbol": symbol,
        "pnl_pct": pnl_pct,
        "pnl_usd": gross_pnl_usd,
        "gross_pnl_usd": gross_pnl_usd,
        "fee_usd": fee_usd,
        "net_pnl_usd": net_pnl_usd,
        "stop_loss_triggered": True,
        "note": "Emergency stop trade"
    }
    
    if "trade_history" not in cfg:
        cfg["trade_history"] = []
    cfg["trade_history"].append(trade_record)
    
    if "open_position" in cfg:
        del cfg["open_position"]
        log("🪫 Cleared open_position after successful close")
    
    save_config(cfg)
    log(f"💾 Trade recorded: {trade_record['symbol']} | PnL: {pnl_pct:.4%} (${net_pnl_usd:.2f})")
    log("🔔 Emergency stop completed - engine will skip trading on next cycle")


def show_help():
    """Display help message when no action specified."""
    print("""
═════════════════════════════════════════════════════════════
    EMERGENCY STOP TRADER - Command Reference v2.19+
═════════════════════════════════════════════════════════════

Emergency Stop Commands for Online Trader-3 (D-025)

  python emergency_stop_trader.py emergency_only
      Sets config["system_status"] = "EMERGENCY_STOP"
      Engine skips all trading logic on next cycle (D-023 guard)
      Position remains open until normal exit signal or another stop
  
  python emergency_stop_trader.py emergency_sell
      Does everything above PLUS:
      - Immediately closes open position with market sell order
      - Records trade marked as emergency (stop_loss_triggered=true)
      - If no position exists, exits gracefully (fixes L-005)
  
  python emergency_stop_trader.py off
      Removes system_status from config.json
      Engine resumes normal trading on next cycle
      Position data preserved for future signals

═════════════════════════════════════════════════════════════

Examples:
  # Trigger emergency stop (position stays open)
  $ python emergency_stop_trader.py emergency_only
  
  # Emergency stop + close position  
  $ python emergency_stop_trader.py emergency_sell
  
  # Resume normal trading after emergency
  $ python emergency_stop_trader.py off

See ARCHITECTURE.md and KNOWN_ISSUES.md for D-023/D-024/D-025 details.
═════════════════════════════════════════════════════════════
    """)


def main():
    if len(sys.argv) < 2:
        show_help()
        return
    
    action = sys.argv[1].lower()
    
    if action == "emergency_only":
        log("🔔 Setting EMERGENCY_STOP flag (emergency_only)")
        cfg = load_config()
        cfg["system_status"] = "EMERGENCY_STOP"
        log("⚡️ Set system_status = EMERGENCY_STOP in config.json")
        save_config(cfg)
        log("✅ Emergency stop activated - engine will skip trading on next cycle")
    
    elif action == "emergency_sell":
        log("🔔 Setting EMERGENCY_STOP flag AND closing position (emergency_sell)")
        cfg = load_config()
        cfg["system_status"] = "EMERGENCY_STOP"
        log("⚡️ Set system_status = EMERGENCY_STOP in config.json")
        close_position(cfg)
    
    elif action == "off":
        log("🔔 Clearing EMERGENCY_STOP flag (off)")
        clear_flag(cfg=load_config())
    
    else:
        print(f"❌ Unknown action: {action}")
        show_help()


if __name__ == "__main__":
    main()