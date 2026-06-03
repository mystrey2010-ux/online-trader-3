# ARCHITECTURE — Online Trader-3 v2.18

## System Overview
- **Engine:** Single-process Python (main.py), 60s cycle, paper trading via Kraken CLI
- **Dashboard:** Read-only summarize_performance.py (reads config.json + Kraken CLI)
- **Config State:** Persisted in config.json (trade_history, open_position, hypothesis_ledger, strategy, news_sentiment)

## Exchange Adapters
| Adapter | When Active | Location |
|---------|-------------|----------|
| KrakenCliPaperExchange | exchange=kraken, LIVE_TRADING_ENABLED=false (**active**) | main.py + ~/.cargo/bin/kraken |
| RealKrakenExchange | CCXT with live API keys (inactive) | main.py (live mode only) |
| GenericCCXTExchange | Any CCXT exchange (inactive) | Future multi-symbol support |

## Trading Loop (run_cycle, 60s)
```
0. EMERGENCY_STOP? → log "EMERGENCY STOP ACTIVE", return (D-023 guard)
1. Fetch ticker (for real-time stop-loss price check)
2. Fetch OHLCV (50 x 1m bars)
3. Calculate RSI-14
4. STOP-LOSS: price < entry × (1-stop_loss_pct) → emergency sell → return (D-045)
5. TREND CHECK: skip BUY if price declining over 20 periods (T-018)
6. POSITION TIMEOUT: warn if open >24h without close signal (T-018)
7. BUY:  RSI < indicator_threshold and uptrend, no position → buy position_size_pct of balance
8. SELL: RSI > sell_threshold AND net PnL after fees > 0 → sell all BTC
```

**Sell threshold** = dynamic, based on `entry_rsi + estimated_rsi_change_for_fee_hurdle + 5` buffer, minimum `indicator_threshold + 10`. Falls back to `indicator_threshold + 20` when no entry RSI is available (D-032).

**Stop-loss exits with `return`** — buy branch cannot fire in same cycle after a stop-loss (D-045).

## Self-Improvement Brain (D-006 / D-025)
```
Trigger: Every 3 completed STRATEGIC trades (excluding emergency)
Strategic trade = RSI buy signal (RSI<threshold) → RSI sell signal (RSI>sell_threshold)
Emergency trades excluded if: stop_loss_triggered=true OR note contains "Emergency"
Action:
   1. Load last 25 trades, filter out emergency trades
   2. Calculate fee-aware metrics (net_pnl_usd)
   3. Tag market regime via 20-period rolling return on 1d OHLCV (D-068)
   4. Fetch news sentiment from CryptoPanic RSS (free, no auth) — N-001
   5. If underperforming: backup strategy → generate regime-aware hypotheses → apply best
   6. Tunes ONE of: indicator_threshold, sell_threshold_base, stop_loss_pct, position_size_pct, rsi_period, sl_cooldown_seconds, trend_filter_lookback, ohlcv_limit, ohlcv_timeframe
   7. Rollback: previous_strategies[] → restore_strategy() — Sharpe < 0 triggers rollback (D-048)
```

**hypothesis_ledger** populated only after reflection fires. Each ledger entry includes: `parameter`, `old_value`, `new_value`, `regime`, `direction`, `regime_tag`, `expected_score_direction`, `metrics_at_failure`, `confidence_reasoning`.

**news_sentiment** (N-001): Free CryptoPanic RSS feed integration; classifies sentiment as positive/neutral/negative based on keyword analysis; stored in config for strategy context.

## Position Management
- Multi-buy accumulation, value-weighted average entry price
- `open_position` persists in config.json until close; restored on startup (D-020)
- `entry_rsi` persisted in open_position config + restored on startup (B-011, D-046)
- Single symbol: BTC/USDT (Q-003 deferred: multi-symbol support)

## Trade Record Schema (v2.15)
```json
{
  "timestamp": "ISO8601",
  "entry": 70228.20,
  "exit": 70595.20,
  "pnl_pct": 0.00523,
  "symbol": "BTC/USDT",
  "pnl_usd": 0.19284,
  "gross_pnl_usd": 0.192845,
  "fee_usd": 0.191892,
  "net_pnl_usd": 0.000953,
  "stop_loss_triggered": false,
  "note": null
}
```

**Fee:** `trade_value × kraken_fee_pct × 2` (both legs). Default 0.26% per leg (0.52% round-trip).

## Config Schema (v2.15)
```json
{
  "target_asset": "BTC/USDT",
  "target_daily_return": 0.002,
  "max_daily_drawdown": 0.01,
  "min_sharpe_ratio": 2.0,
  "reflection_cadence": 3,
  "kraken_fee_pct": 0.0026,
  "current_strategy": {
    "indicator_threshold": 63.0,
    "sell_threshold_base": 10,
    "stop_loss_pct": 0.016,
    "position_size_pct": 0.03,
    "rsi_period": 14,
    "sl_cooldown_seconds": 300,
    "trend_filter_lookback": 20,
    "ohlcv_limit": 50,
    "ohlcv_timeframe": "1m"
  },
  "trade_history": [],
  "hypothesis_ledger": [],
  "version": 1,
  "previous_strategies": [],
  "open_position": {
    "timestamp": "ISO8601",
    "symbol": "BTC/USDT",
    "entry_price": 67752.40,
    "amount_btc": 0.000543
  },
  "system_status": null
}
```

## Dashboard (summarize_performance.py)
7 sections: Account → Position → Strategy → Orders → Trades → Brain → System
Read-only; uses Kraken CLI for real-time data.

Hypothesis log table reads keys: `parameter`, `old_value`, `new_value`, `regime`, `direction` (set by D-044 fix).

## Operations
### Engine Management (manage_trader.sh)
- `start` → python main.py
- `stop` → pkill -9 -f main.py (quiet kill)
- `restart` → stop + start
- `status` → pgrep output (NOTE: fragile pattern — B-014/T-026 pending fix)
- `clean` → DESTRUCTIVE: engine stopped + SANDBOX cleared

### Emergency Stop (emergency_stop_trader.py)
- `emergency_only` → sets EMERGENCY_STOP flag (D-023)
- `emergency_sell` → flag + market-sell position (⚠ only when position exists, L-005)
- `off` → clears EMERGENCY_STOP, resumes trading (D-024/D-026)
- Help: run without arguments

### Data Preservation
- STOP/RESTART: Non-destructive to all persistent state (D-020/D-009)
- CLEAN command only: Destructive (engine stopped + sandbox cleared)
- Config.json fields NEVER touched by normal operations: version, exchange credentials

## Logging
- **Format:** `[YYYY-MM-DD HH:MM:SS,ms] [LEVEL] msg`
- **File:** trader.log (append mode)
- **Engine Detection:** `pgrep -f "main.py"` (summarize_performance.py; manage_trader.sh still uses fragile pattern — B-014)

## Design Decisions (See DECISIONS.md for full list)
Key invariants:
- D-013: f"${val:.2f}" exclusively; NEVER comma specifier
- D-016: PAPER/SANDBOX mode detected from CLI output, not config key
- D-018: Both sell paths write gross_pnl_usd/fee_usd/net_pnl_usd at close
- D-023: EMERGENCY_STOP guard at top of run_cycle()
- D-025: Emergency trades excluded from self-improvement brain reflection pool
- D-031: Sell only if net PnL after fees > 0 (fee trap prevention)
- D-032: Dynamic sell threshold based on entry RSI + fee hurdle
- D-044: Hypothesis ledger entries include display alias keys for dashboard
- D-045: Stop-loss exits with `return` — no same-cycle re-buy
- D-055: Trend filter skips BUY when price declining over 20 periods (T-018)

## Known Bugs & Architectural Risks
| ID | File | Lines | Description | Severity |
|----|------|-------|-------------|----------|
All bugs resolved in v2.17 — see KNOWN_ISSUES.md

**Full details and fix tasks: see KNOWN_ISSUES.md and TASKS.md.**

## Deferred Items
| ID | Item | Notes |
|----|------|-------|
| Q-003 | Multi-symbol support | Architecture supports, not implemented |
| Q-004 | Native stop-loss orders (Kraken API) | Currently price-check based |

## Backup Convention
- Git repository in use for version control
- Local backups: `*.ddmmyy-hhmmss` prefix before major changes
- Project backups: `/backups/`
- Docs backups: `/docs/backups/`

---
**Last Updated:** 2026-06-02 23:05 | Engineer: J.A.R.V.I.S.
