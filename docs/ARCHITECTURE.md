# ARCHITECTURE — Online Trader-3 v2.13

## System Overview
- **Engine:** Single-process Python (main.py), 60s cycle, paper trading via Kraken CLI
- **Dashboard:** Read-only summarize_performance.py (reads config.json + Kraken CLI)
- **Config State:** Persisted in config.json (trade_history, open_position, hypothesis_ledger, strategy)

## Exchange Adapters
| Adapter | When Active | Location |
|---------|-------------|----------|
| KrakenCliPaperExchange | exchange=kraken, sandbox_mode=true (**active**) | main.py + ~/.cargo/bin/kraken |
| RealKrakenExchange | CCXT with live API keys (inactive) | emergency_stop_trader.py only |
| GenericCCXTExchange | Any CCXT exchange (inactive) | Future multi-symbol support |

## Trading Loop (run_cycle, 60s)
```
0. EMERGENCY_STOP? → log "EMERGENCY STOP ACTIVE", return (D-023 guard)
1. Fetch ticker (for stop-loss price check)
2. Fetch OHLCV (50 x 1m bars)
3. Calculate RSI-14
4. STOP-LOSS: price < entry × (1-stop_loss_pct) → emergency sell
5. BUY: RSI < indicator_threshold (63.0), no position → buy position_size_pct of balance
6. SELL: RSI > dynamic_threshold (based on entry RSI + fee requirements), position open → sell all BTC
```

**Sell threshold = dynamic threshold based on entry RSI and fee requirements (D-032). NOT a fixed offset.**

## Self-Improvement Brain (D-006 / D-025)
```
Trigger: Every 3 completed STRATEGIC trades (excluding emergency)
Strategic trade = RSI buy signal (RSI<63.0) → RSI sell signal (RSI>83.0)
Emergency trades excluded if: stop_loss_triggered=true OR note contains "Emergency"
Action:
  1. Load last 25 trades, filter out emergency trades
  2. Calculate fee-aware metrics (net_pnl_usd)
  3. Tag market regime via 20-period rolling return
  4. If underperforming: backup strategy → generate regime-aware hypotheses → apply best
  5. Tunes: indicator_threshold, stop_loss_pct, position_size_pct
  6. Rollback: previous_strategies[] → restore_strategy() if needed
```

**hypothesis_ledger populated only after trade #3 triggers reflection (D-006).**

## Position Management
- Multi-buy accumulation, value-weighted average entry price
- open_position persists in config.json until close; restored on startup (D-020)
- Single symbol: BTC/USDT (Q-003 deferred: multi-symbol support)

## Trade Record Schema (v2.12)
```json
{
  "timestamp": "ISO8601",
  "entry": 73671.60,
  "exit": 73850.30,
  "pnl_pct": 0.00243,
  "symbol": "BTC/USDT",
  "pnl_usd": 0.08975,
  "gross_pnl_usd": 0.089748,
  "fee_usd": 0.192,
  "net_pnl_usd": -0.102,
  "stop_loss_triggered": true/false,
  "note": null
}
```

**Fee:** `trade_value × kraken_fee_pct × 2` (both legs). Default 0.26% per leg (0.52% round-trip).

## Config Schema (v2.13)
```json
{
  "exchange": {"type":"kraken","apiKey":"...","secret":"..."},
  "target_asset": "BTC/USDT",
  "target_daily_return": 0.002,
  "max_daily_drawdown": 0.01,
  "min_sharpe_ratio": 2.0,
  "reflection_cadence": 3,
  "kraken_fee_pct": 0.0026,
  "current_strategy": {
    "indicator_threshold": 63.0,
    "stop_loss_pct": 0.016,
    "position_size_pct": 0.037
  },
  "trade_history": [],
  "hypothesis_ledger": [],
  "version": 1,
  "previous_strategies": [],
  "open_position": {},
  "system_status": null
}
```

## Dashboard (summarize_performance.py)
7 sections: Account → Position → Strategy → Orders → Trades → Brain → System  
Read-only; uses Kraken CLI for real-time data.

## Operations
### Engine Management (manage_trader.sh)
- `start` → python main.py
- `stop` → pkill -9 -f main.py (quiet kill)
- `restart` → stop + start
- `status` → pgrep -a "python" | grep "/.*main\\.py"
- `clean` → DESTRUCTIVE: engine stopped + SANDBOX cleared

### Emergency Stop (emergency_stop_trader.py)
- `emergency_only` → sets EMERGENCY_STOP flag (D-023)
- `emergency_sell` → flag + market-sell position (⚠ only when position exists, L-005)
- `off` → clears EMERGENCY_STOP, resumes trading (D-024/D-025)
- Help: run without arguments

### Data Preservation
- STOP/RESTART: Non-destructive to all persistent state (D-020/D-009)
- CLEAN command only: Destructive (engine stopped + sandbox cleared)
- Config.json fields NEVER touched by normal operations: version, exchange credentials

## Logging
- **Format:** `[YYYY-MM-DD HH:MM:SS,ms] [LEVEL] msg`
- **File:** trader.log (append mode)
- **Engine Detection:** `pgrep -a "python" | grep "/.*main\\.py"` (no PID file)

## Design Decisions (See DECISIONS.md for full list)
Key invariants:
- D-013: format_dollar() / f"${val:.2f}" exclusively; NEVER comma specifier
- D-016: PAPER/SANDBOX mode detected from CLI output, not config key
- D-018: Both sell paths write gross_pnl_usd/fee_usd/net_pnl_usd at close
- D-023: EMERGENCY_STOP guard at top of run_cycle()
- D-025: Emergency trades excluded from self-improvement brain reflection pool

## Known Bugs & Architectural Risks
| ID | File | Lines | Risk | Severity |
|----|------|-------|------|----------|
| B-010 | main.py | 820, 857 | SELL PnL uses `self.entry_price` (individual buy) not weighted avg — wrong PnL on multi-buy | High |
| B-011 | main.py | 232, 726 | `entry_rsi` never saved to config / restored on startup — D-032 dynamic threshold silently bypassed after restart | Medium |
| B-012 | main.py | 376 | Cadence check uses all trades including emergency ones — 3 stop-losses can trigger reflection (D-025 violation) | Medium |
| B-013 | main.py | 478 | `restore_strategy()` never called — brain rollback (PRIMARY GOAL) is dead code | Medium |
| B-014 | manage_trader.sh | 23, 50, 62, 85 | `pgrep -a "python" \| grep main.py` fragile in venvs — should be `pgrep -f "main.py"` (D-016) | Low |
| B-015 | manage_trader.sh | 106 | Hardcoded `"Version 2.13"` stale (now v2.14) | Low |
| B-016 | manage_trader.sh | 210 | `clean` sets `open_position={}` not deletes key (D-009/D-020 violation) | Low |
**Full details and fix tasks: see KNOWN_ISSUES.md (B-010–B-016) and TASKS.md (T-022–T-028).**

## Deferred Items
| ID | Item | Notes |
|----|------|-------|
| Q-003 | Multi-symbol support | Architecture supports, not implemented |
| Q-004 | Native stop-loss orders (Kraken API) | Currently price-check based |
| D-HYP-003 | hypothesis_ledger display on dashboard | Dashboard needs view implementation (T-019) |

## Backup Convention
- No git version control yet — T-016 priority task
- Local backups: `*.ddmmyy-hhmmss` prefix before major changes
- Project backups: `/backups/`
- Docs backups: `/docs/backups/`

---
**Last Updated:** 2026-05-31 23:15 | Engineer: J.A.R.V.I.S.
