# DECISIONS — Online Trader-3 (Key Design Decisions)

| ID | Decision | Where | Ver |
|----|----------|-----|-----|
| D-006 | Self-improvement brain after N strategic trades | main.py self_improve_strategies() | v2.5 |
| D-009 | Position persists in config.json across restarts | main.py __init__ | v2.5 |
| D-013 | f"${val:.2f}" format only; no comma specifier | summarize_performance.py | v2.7+ |
| D-016 | PAPER/SANDBOX mode detected from CLI output | summarize_performance.py | v2.7+ |
| D-017 | Sell threshold = indicator_threshold + 20, NOT config | main.py run_cycle() | v2.7+ |
| D-018 | Both sell paths write gross_pnl_usd/fee_usd/net_pnl_usd | main.py run_cycle() | v2.7+ |
| D-020 | Startup position restoration prevents spurious BUY | main.py __init__ | v2.9 |
| D-023 | EMERGENCY_STOP guard at top of run_cycle() | main.py run_cycle() | v2.10 |
| D-025 | Emergency trades excluded from brain reflection pool | main.py self_improve_strategies() | v2.12 |
| D-031 | Fee trap prevention: only sell if net PnL > 0 | main.py run_cycle() | v2.13+ |
| D-032 | Dynamic sell threshold based on entry RSI + fees | main.py run_cycle() | v2.13+ |
| D-038 | Reload config each cycle for external writes | main.py run_cycle() | v2.14 |
| D-068 | Multi-timeframe regime: 1d OHLCV for 20-day trend | main.py self_improve_strategies() | v2.17 |
| D-069 | Pre-commit backtest gate: 500-bar validation | main.py _generate_and_apply_hypotheses() | v2.17 |
| D-074 | Daily loss limit: EMERGENCY_STOP if daily_net_pnl_usd < -(start_balance × max_daily_loss_pct) | main.py run_cycle() | v2.18 |
| D-077/D-078 | daily_start_balance_usd stored per day, _calculate_daily_pnl() returns USD | main.py _calculate_daily_pnl() | v2.19 |

## Verification Status
| ID | Status | Notes |
|----|--------|---------|
| D-074 | ✅ Confirmed working | Daily loss limit implemented in run_cycle() method |
| D-077/D-078 | ✅ Confirmed working | daily_start_balance_usd stored per day, _calculate_daily_pnl() returns USD |

---
**Last Updated:** 2026-06-05 | See ARCHITECTURE.md for full trading loop diagram