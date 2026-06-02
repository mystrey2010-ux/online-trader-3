#!/mnt/data/venvs/online-trader-3/bin/python
"""
Online Trader-3 Performance Dashboard v2.8

Sources of truth:
  - config.json            : strategy state, trade_history, hypothesis_ledger, open_position
  - kraken paper balance   : live USD + BTC balances (paper wallet)
  - kraken paper status    : portfolio value, unrealized PnL, fee_rate, total_trades
  - kraken paper history   : every filled order (buy/sell) with cost, fee, price, volume
  - kraken paper orders    : any open limit orders
  - kraken ticker XBTUSD   : live BTC spot price for current valuation

Engine running: detected via pgrep, NOT from Kraken CLI (kraken status = server health only).
PAPER mode: detected from kraken paper status JSON field "mode"=="paper".
"""

import json
import subprocess
import os
import sys
from datetime import datetime


CONFIG_PATH = "config.json"
KRAKEN_BIN = os.path.expanduser("~/.cargo/bin/kraken")
SEPARATOR_WIDE = "=" * 76
SEPARATOR_MID  = "-" * 50
SEPARATOR_THIN = "-" * 40


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

def _kraken_env():
    env = os.environ.copy()
    env["PATH"] = f"{os.path.expanduser('~/.cargo/bin')}:{env['PATH']}"
    return env


def run_kraken(args):
    """
    Run 'kraken <args>' with -o json.
    Returns parsed dict/list on success, None on failure.
    Prints a single install-hint line if binary not found.
    """
    try:
        cmd = [KRAKEN_BIN] + args.split() + ["-o", "json"]
        r = subprocess.run(cmd, capture_output=True, text=True, env=_kraken_env(), timeout=10)
        if r.returncode == 0 and r.stdout.strip():
            return json.loads(r.stdout)
        return None
    except FileNotFoundError:
        print(f"  [!] Kraken CLI not found: {KRAKEN_BIN}")
        print("      Install: cargo install kraken_cli")
        return None
    except (json.JSONDecodeError, subprocess.TimeoutExpired):
        return None


def load_config():
    try:
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"ERROR: cannot load {CONFIG_PATH}: {e}")
        sys.exit(1)


def fmt_usd(amount):
    """Dollar amount, always 2dp, no forced +/- sign. e.g. $73870.20"""
    try:
        return f"${float(amount):.2f}"
    except (TypeError, ValueError):
        return "N/A"


def fmt_pnl(amount):
    """Signed dollar PnL. e.g. +$1.23 or -$0.50"""
    try:
        v = float(amount)
        sign = "+" if v >= 0 else ""
        return f"{sign}${v:.4f}"
    except (TypeError, ValueError):
        return "N/A"


def fmt_pct(value, decimals=2):
    """Percentage. e.g. 0.0026 → 0.26%"""
    try:
        return f"{float(value) * 100:.{decimals}f}%"
    except (TypeError, ValueError):
        return "N/A"


def fmt_pct_signed(value, decimals=4):
    """Signed percentage. e.g. 0.00242 → +0.2426%"""
    try:
        v = float(value) * 100
        sign = "+" if v >= 0 else ""
        return f"{sign}{v:.{decimals}f}%"
    except (TypeError, ValueError):
        return "N/A"


def engine_running():
    """True if main.py process is live. Uses pgrep -f main.py."""
    try:
        r = subprocess.run(
            ["pgrep", "-f", "main.py"], capture_output=True, text=True
        )
        return r.returncode == 0
    except Exception:
        return False

def get_regime_stability(config, current_regime):
    """Calculate regime stability metric from hypothesis ledger.
    Returns percentage of recent hypotheses in same regime.
    """
    ledger = config.get("hypothesis_ledger", [])
    if not ledger:
        return "N/A"
    recent = ledger[-10:]  # Last 10 hypotheses
    matches = sum(1 for h in recent if h.get("regime") == current_regime)
    pct = (matches / len(recent)) * 100
    return f"{pct:.0f}%"


def btc_spot_price():
    """
    Fetch live BTC/USD spot price from Kraken ticker.
    Returns float or None.
    Ticker key is XXBTZUSD; last price is in c[0].
    """
    data = run_kraken("ticker XBTUSD")
    if data and "XXBTZUSD" in data:
        try:
            return float(data["XXBTZUSD"]["c"][0])
        except (KeyError, IndexError, ValueError):
            pass
    return None


# ─────────────────────────────────────────────
# Section 1 — Header
# ─────────────────────────────────────────────

def print_header():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    running = engine_running()
    engine_tag = "[ENGINE: RUNNING]" if running else "[ENGINE: STOPPED]"
    print()
    print(SEPARATOR_WIDE)
    print("  ONLINE TRADER-3  |  PERFORMANCE DASHBOARD v2.8".center(76))
    print(f"  {now}  |  {engine_tag}".center(76))
    print(SEPARATOR_WIDE)
    print()


# ─────────────────────────────────────────────
# Section 2 — Account Status
# ─────────────────────────────────────────────

def print_account_status(spot_price):
    """
    Data: kraken paper balance + kraken paper status + live spot price.
    Shows: trading mode, USD/BTC balances, portfolio value, unrealised PnL vs start.
    """
    print("[1] ACCOUNT STATUS")
    print(SEPARATOR_MID)

    status = run_kraken("paper status")
    balance = run_kraken("paper balance")

    # Trading mode — from paper status JSON field, not config
    mode = "PAPER/SANDBOX"
    fee_rate = 0.0026
    if status:
        raw_mode = status.get("mode", "").upper()
        if raw_mode == "PAPER":
            mode = "PAPER/SANDBOX (Kraken CLI)"
        elif raw_mode == "LIVE":
            mode = "LIVE TRADING  (Kraken CLI)"
        fee_rate = float(status.get("fee_rate", 0.0026))

    print(f"  Trading Mode     : {mode}")
    print(f"  Fee Rate         : {fmt_pct(fee_rate)} per leg (x2 round-trip)")

    # Balances
    usd_avail = usd_reserved = btc_avail = btc_reserved = 0.0
    if balance and "balances" in balance:
        for ccy, vals in balance["balances"].items():
            avail = float(vals.get("available", 0))
            resv  = float(vals.get("reserved", 0))
            if "USD" in ccy:
                usd_avail += avail
                usd_reserved += resv
            elif "BTC" in ccy or "XBT" in ccy:
                btc_avail += avail
                btc_reserved += resv

    btc_total = btc_avail + btc_reserved
    usd_total = usd_avail + usd_reserved
    btc_usd_value = btc_total * spot_price if spot_price else None

    print()
    print("  Balances (Kraken paper wallet):")
    print(f"    USD available    : {fmt_usd(usd_avail)}")
    print(f"    USD reserved     : {fmt_usd(usd_reserved)}")
    print(f"    BTC total        : {btc_total:.8f} BTC")
    if btc_usd_value is not None:
        print(f"    BTC value @ spot : {fmt_usd(btc_usd_value)}  (spot {fmt_usd(spot_price)})")
    else:
        print(f"    BTC value        : N/A (spot price unavailable)")

    # Portfolio summary from paper status
    if status:
        start_bal  = float(status.get("starting_balance", 0))
        curr_val   = float(status.get("current_value", 0))
        unr_pnl    = float(status.get("unrealized_pnl", 0))
        unr_pct_raw= float(status.get("unrealized_pnl_pct", 0))
        # unrealized_pnl_pct from Kraken is already a % (e.g. -0.035 = -3.5%), not a fraction
        unr_pct_display = f"{unr_pct_raw:+.4f}%"
        total_tr   = int(status.get("total_trades", 0))
        print()
        print("  Portfolio Summary (from Kraken paper status):")
        print(f"    Starting Balance : {fmt_usd(start_bal)}")
        print(f"    Current Value    : {fmt_usd(curr_val)}")
        print(f"    Unrealised PnL   : {fmt_pnl(unr_pnl)}  ({unr_pct_display})")
        print(f"    Total Orders     : {total_tr}  (filled buy + sell legs)")
    else:
        print("  [!] kraken paper status unavailable")

    print(SEPARATOR_MID)


# ─────────────────────────────────────────────
# Section 3 — Open Position
# ─────────────────────────────────────────────

def print_open_position(config, spot_price):
    """
    Data: config.json open_position + live spot price.
    Shows: entry, size, current value, unrealised PnL, stop-loss trigger price.
    """
    print("[2] OPEN POSITION")
    print(SEPARATOR_MID)

    pos = config.get("open_position")
    if not pos or not isinstance(pos, dict):
        print("  No open position (engine in standby)")
        print(SEPARATOR_MID)
        return

    symbol     = pos.get("symbol", "BTC/USDT")
    entry      = float(pos.get("entry_price", 0))
    amt_btc    = float(pos.get("amount_btc", 0))
    opened_at  = pos.get("timestamp", "N/A")
    strat      = config.get("current_strategy", {})
    sl_pct     = float(strat.get("stop_loss_pct", 0.016))

    entry_value = entry * amt_btc
    sl_price    = entry * (1 - sl_pct)

    print(f"  Symbol           : {symbol}")
    print(f"  Entry Price      : {fmt_usd(entry)}")
    print(f"  Size             : {amt_btc:.8f} BTC")
    print(f"  Entry Value      : {fmt_usd(entry_value)}")
    print(f"  Opened           : {opened_at[:19] if len(opened_at) > 10 else opened_at}")
    print()
    print(f"  Stop-Loss Trigger: {fmt_usd(sl_price)}  (entry - {fmt_pct(sl_pct)})")

    if spot_price:
        curr_value  = amt_btc * spot_price
        unr_pnl     = curr_value - entry_value
        unr_pct     = (spot_price - entry) / entry
        dist_sl     = (spot_price - sl_price) / sl_price
        sl_status   = "SAFE" if spot_price > sl_price else "!!! STOP-LOSS BREACH !!!"
        print(f"  Current Price    : {fmt_usd(spot_price)}")
        print(f"  Current Value    : {fmt_usd(curr_value)}")
        print(f"  Unrealised PnL   : {fmt_pnl(unr_pnl)}  ({fmt_pct_signed(unr_pct)})")
        print(f"  Distance to SL   : {fmt_pct(dist_sl)}  [{sl_status}]")
    else:
        print("  Current Price    : N/A (spot unavailable)")

    print(SEPARATOR_MID)


# ─────────────────────────────────────────────
# Section 4 — Strategy Parameters
# ─────────────────────────────────────────────

def print_strategy(config):
    """
    Data: config.json current_strategy + performance targets.
    Note: sell threshold = indicator_threshold + 20 (hardcoded offset in engine, NOT a config field).
    """
    print("[3] CURRENT STRATEGY")
    print(SEPARATOR_MID)

    strat   = config.get("current_strategy", {})
    thresh  = float(strat.get("indicator_threshold", 0))
    sl_pct  = float(strat.get("stop_loss_pct", 0))
    ps_pct  = float(strat.get("position_size_pct", 0))
    version = int(config.get("version", 1))
    n_snaps = len(config.get("previous_strategies", []))

    sell_thresh = thresh + 20.0  # hardcoded +20 offset in engine run_cycle

    print(f"  RSI BUY signal   : RSI < {thresh:.1f}")
    print(f"  RSI SELL signal  : RSI > {sell_thresh:.1f}  (buy_threshold + 20, not a config field)")
    print(f"  Stop-Loss        : -{fmt_pct(sl_pct)}  below entry price")
    print(f"  Position Size    : {fmt_pct(ps_pct)}  of available USD balance")
    print(f"  Strategy Version : v{version}  ({n_snaps} rollback snapshot(s))")

    print()
    print("  Performance Targets (self-improvement thresholds):")
    print(f"    Daily Return    : >= {fmt_pct(config.get('target_daily_return', 0))}")
    print(f"    Max Drawdown    : <= {fmt_pct(config.get('max_daily_drawdown', 0))}")
    print(f"    Min Sharpe      : >= {config.get('min_sharpe_ratio', 0):.2f}")
    print(f"    Reflection      : every {config.get('reflection_cadence', 3)} completed trades")
    print(f"    Fee Rate (cfg)  : {fmt_pct(config.get('kraken_fee_pct', 0.0026))} per leg (default if absent)")

    print(SEPARATOR_MID)


# ─────────────────────────────────────────────
# Section 5 — Kraken Paper Order History
# ─────────────────────────────────────────────

def print_order_history():
    """
    Data: kraken paper history (all filled buy/sell orders).
    Shows every order row: side, pair, price, volume, cost, fee, time.
    kraken paper orders: any open limit orders (usually 0 for market orders).
    """
    print("[4] KRAKEN PAPER ORDER HISTORY")
    print(SEPARATOR_MID)

    history = run_kraken("paper history")
    if history is None:
        print("  [!] kraken paper history unavailable")
        print(SEPARATOR_MID)
        return

    trades     = history.get("trades", [])
    filled     = int(history.get("filled_count", len(trades)))
    cancelled  = int(history.get("cancelled_count", 0))

    print(f"  Filled Orders    : {filled}")
    print(f"  Cancelled Orders : {cancelled}")
    print(f"  Mode             : {history.get('mode', '?').upper()}")

    if not trades:
        print("  No filled orders yet.")
        print(SEPARATOR_MID)
        return

    print()
    # Header row
    print(f"  {'#':<4} {'Side':<5} {'Pair':<8} {'Price':>10} {'Volume':>14} {'Cost':>8} {'Fee':>7} {'Time'}")
    print(f"  {'-'*4} {'-'*5} {'-'*8} {'-'*10} {'-'*14} {'-'*8} {'-'*7} {'-'*19}")

    buy_cost = sell_cost = total_fees = 0.0
    for i, t in enumerate(trades, 1):
        side   = t.get("side", "?").upper()
        pair   = t.get("pair", "?")
        price  = float(t.get("price", 0))
        vol    = float(t.get("volume", 0))
        cost   = float(t.get("cost", 0))
        fee    = float(t.get("fee", 0))
        ts_raw = t.get("time", "")[:19].replace("T", " ")  # trim to seconds
        order_id = t.get("id", "?")

        total_fees += fee
        if side == "BUY":
            buy_cost += cost
        else:
            sell_cost += cost

        side_tag = "BUY " if side == "BUY" else "SELL"
        print(f"  {i:<4} {side_tag:<5} {pair:<8} {price:>10.2f} {vol:>14.8f} {cost:>8.4f} {fee:>7.5f} {ts_raw}")

    print()
    print(f"  Total Fees Paid  : ${total_fees:.5f}")
    print(f"  Total Buy Cost   : ${buy_cost:.4f}")
    print(f"  Total Sell Value : ${sell_cost:.4f}")

    # Open limit orders
    print()
    open_orders = run_kraken("paper orders")
    if open_orders is not None:
        count = int(open_orders.get("count", len(open_orders.get("open_orders", []))))
        if count == 0:
            print("  Open Limit Orders: None")
        else:
            print(f"  Open Limit Orders: {count}")
            for o in open_orders.get("open_orders", []):
                print(f"    {o}")
    else:
        print("  Open Limit Orders: unavailable")

    print(SEPARATOR_MID)


# ─────────────────────────────────────────────
# Section 6 — Completed Trades (config.json)
# ─────────────────────────────────────────────

def print_trade_history(config):
    """
    Data: config.json trade_history (engine-tracked closed trades, distinct from order rows).
    Each entry = one full trade cycle (buy→sell).
    Shows: entry/exit price, gross PnL, fee, net PnL, WIN/LOSS status.
    Pre-v2.7 records may lack fee fields — shown with fallback label.
    """
    print("[5] COMPLETED TRADE CYCLES  (config.json trade_history)")
    print(SEPARATOR_MID)

    trades = config.get("trade_history", [])
    if not trades:
        print("  No completed trade cycles yet.")
        print(SEPARATOR_MID)
        return

    wins = losses = total_net = total_fees = 0.0

    for i, t in enumerate(trades, 1):
        ts        = t.get("timestamp", "N/A")[:19]
        entry     = float(t.get("entry", 0))
        exit_p    = float(t.get("exit", 0))
        pnl_pct   = float(t.get("pnl_pct", 0))
        pnl_usd   = float(t.get("pnl_usd", 0))
        symbol    = t.get("symbol", "BTC/USDT")
        sl_flag   = t.get("stop_loss_triggered", False)

        has_fees  = "net_pnl_usd" in t
        gross_pnl = float(t.get("gross_pnl_usd", pnl_usd))
        fee_usd   = float(t.get("fee_usd", 0))
        net_pnl   = float(t.get("net_pnl_usd", pnl_usd))

        result    = "✓ WIN " if net_pnl > 0 else "✗ LOSS"
        close_tag = " [SL]" if sl_flag else ""
        fee_label = "" if has_fees else " [est, pre-v2.7]"

        if net_pnl > 0:
            wins += 1
        else:
            losses += 1
        total_net   += net_pnl
        total_fees  += fee_usd

        print()
        print(f"  Trade #{i}  {result}{close_tag}  {ts}")
        print(f"    {symbol:<10}  Entry {fmt_usd(entry)}  ->  Exit {fmt_usd(exit_p)}")
        print(f"    Raw PnL    : {fmt_pct_signed(pnl_pct)}  ({fmt_pnl(pnl_usd)})")
        if has_fees:
            print(f"    Fees       : ${fee_usd:.5f}{fee_label}")
            print(f"    Net PnL    : {fmt_pnl(net_pnl)}  (fee-adjusted)")
        else:
            print(f"    Net PnL    : {fmt_pnl(net_pnl)}  (fee fields absent — pre-v2.7 record)")

    total = int(wins + losses)
    wins  = int(wins)
    losses = int(losses)
    win_rate = (wins / total * 100) if total > 0 else 0.0

    print()
    print(SEPARATOR_THIN)
    print(f"  Total Cycles     : {total}  ({wins} wins / {losses} losses)")
    print(f"  Win Rate         : {win_rate:.1f}%")
    print(f"  Total Net PnL    : {fmt_pnl(total_net)}")
    print(f"  Total Fees Paid  : ${total_fees:.5f}  (config estimates)")
    print(SEPARATOR_MID)


# ─────────────────────────────────────────────
# Section 7 — Self-Improvement Brain
# ─────────────────────────────────────────────

def print_brain_status(config):
    """
    Data: config.json hypothesis_ledger, previous_strategies, version, reflection_cadence.
    Shows: reflection progress, all hypotheses with regime/param/direction, rollback snapshots.
    """
    print("[6] SELF-IMPROVEMENT BRAIN")
    print(SEPARATOR_MID)

    ledger      = config.get("hypothesis_ledger", [])
    prev_strats = config.get("previous_strategies", [])
    version     = int(config.get("version", 1))
    cadence     = int(config.get("reflection_cadence", 3))
    trades      = config.get("trade_history", [])
    n_trades    = len(trades)

    trades_since = n_trades % cadence if cadence > 0 else 0
    trades_to_go = cadence - trades_since if trades_since > 0 else cadence if n_trades == 0 else 0

    print(f"  Strategy Version : v{version}")
    print(f"  Completed Cycles : {n_trades}  |  Reflection every {cadence} trades")

    if n_trades == 0:
        print(f"  Next Reflection  : {cadence} more trade(s) needed")
    elif trades_to_go == 0:
        print(f"  Next Reflection  : due NOW (cadence reached)")
    else:
        print(f"  Next Reflection  : {trades_to_go} more trade(s) needed  ({trades_since}/{cadence})")

    print(f"  Hypotheses Logged: {len(ledger)}")
    print(f"  Rollback Backups : {len(prev_strats)}")

    # Hypothesis ledger — show all entries
    if ledger:
        print()
        print("  Hypothesis Log:")
        print(f"  {'#':<3} {'Timestamp':<20} {'Regime':<10} {'Parameter':<22} {'Change':<20} {'Direction'}")
        print(f"  {'-'*3} {'-'*20} {'-'*10} {'-'*22} {'-'*20} {'-'*10}")
        for i, h in enumerate(ledger, 1):
            ts_h   = str(h.get("timestamp", ""))[:19]
            regime = str(h.get("regime", h.get("market_regime", "?")))[:10]
            param  = str(h.get("parameter", h.get("param_adjusted", "?")))[:22]
            old_v  = h.get("old_value", h.get("previous_value", "?"))
            new_v  = h.get("new_value", h.get("applied_value", "?"))
            dirn   = str(h.get("expected_score_direction", h.get("direction", "?")))
            try:
                change = f"{float(old_v):.4f} -> {float(new_v):.4f}"
            except (TypeError, ValueError):
                change = f"{old_v} -> {new_v}"
            print(f"  {i:<3} {ts_h:<20} {regime:<10} {param:<22} {change:<20} {dirn}")
    else:
        n_to_first = cadence - n_trades if n_trades < cadence else 0
        if n_to_first > 0:
            print(f"\n  Brain is in observation mode. Needs {n_to_first} more trade(s) before first reflection.")
        else:
            print("\n  No hypotheses logged yet. Performance may be meeting targets (no tuning needed).")

    # Rollback snapshots
    if prev_strats:
        print()
        print("  Strategy Rollback Snapshots:")
        for snap in prev_strats[-5:]:   # show last 5
            snap_ts  = str(snap.get("timestamp", ""))[:19]
            snap_ver = snap.get("version", "?")
            strat_s  = snap.get("strategy", {})
            thr      = strat_s.get("indicator_threshold", "?")
            sl       = strat_s.get("stop_loss_pct", "?")
            ps       = strat_s.get("position_size_pct", "?")
            try:
                snap_line = f"v{snap_ver}  thr={float(thr):.1f}  sl={float(sl)*100:.2f}%  ps={float(ps)*100:.3f}%"
            except (TypeError, ValueError):
                snap_line = f"v{snap_ver}  {strat_s}"
            print(f"    {snap_ts}  {snap_line}")

    # Regime stability metric (last 10 hypotheses)
    if ledger:
        current_regime = ledger[-1].get("regime", "NEUTRAL") if ledger else "NEUTRAL"
        stability = get_regime_stability(config, current_regime)
        print()
        print(f"  Regime Stability: {stability} of last 10 hypotheses in '{current_regime}' regime")

    print(SEPARATOR_MID)


# ─────────────────────────────────────────────
# Section 8 — System Info
# ─────────────────────────────────────────────

def print_system_info(config):
    """
    Engine run state (pgrep), log tail, config path, asset, key config fields.
    """
    print("[7] SYSTEM INFO")
    print(SEPARATOR_MID)

    running = engine_running()
    status_str = "RUNNING (PID detected)" if running else "STOPPED (no main.py process found)"
    print(f"  Engine           : {status_str}")
    print(f"  Config Path      : {os.path.abspath(CONFIG_PATH)}")
    print(f"  Target Asset     : {config.get('target_asset', 'N/A')}")
    print(f"  Exchange         : {config.get('exchange', {}).get('type', 'N/A').upper()}")

    # Last 5 log lines (non-empty)
    log_path = "trader.log"
    if os.path.exists(log_path):
        try:
            r = subprocess.run(
                ["tail", "-n", "20", log_path],
                capture_output=True, text=True
            )
            lines = [l.rstrip() for l in r.stdout.splitlines() if l.strip()][-5:]
            if lines:
                print()
                print("  Recent Log (last 5 non-empty lines):")
                for ln in lines:
                    print(f"    {ln[:120]}")
        except Exception:
            pass
    else:
        print(f"  Log              : {log_path} not found")

    print()
    print("  Shutdown tip: pkill -9 -f main.py  (manage_trader.sh stop auto-restarts)")
    print(SEPARATOR_MID)


# ─────────────────────────────────────────────
# Section 9 — Footer
# ─────────────────────────────────────────────

def print_footer():
    print("[END OF REPORT]")
    print(f"  Generated : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(SEPARATOR_WIDE)
    print()


# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────

def main():
    config = load_config()

    # Fetch spot price once — shared across sections that need it
    spot = btc_spot_price()

    print_header()
    print_account_status(spot)
    print_open_position(config, spot)
    print_strategy(config)
    print_order_history()
    print_trade_history(config)
    print_brain_status(config)
    print_system_info(config)
    print_footer()


if __name__ == "__main__":
    main()
