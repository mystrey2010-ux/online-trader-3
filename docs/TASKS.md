# TASKS — Online Trader-3 v2.15

## Open Tasks
| ID | Description | Priority | Dependencies | Status |
|----|-------------|----------|--------------|--------|
| T-003 | Confirm hypothesis_ledger populated after first reflection post-B-017 fix | Medium | Requires restart + 3 strategic trades | PENDING |
| T-016 | Add git version control (git init + baseline commit) | High | None | PENDING |
| T-018 | Position timeout: warn if open >24h (L-004) | Medium | None | PENDING |
| T-019 | Verify hypothesis_ledger dashboard display works with new key schema (D-044) | Medium | T-003, B-018 fix | PENDING |
| T-020 | Consolidate stop-loss into helper function | Low | None | PENDING |
| T-021 | Add sell_threshold to cycle log output | Low | None | PENDING |
| T-029 | Post-SL cooldown: prevent re-buy for N minutes after a stop-loss fires (L-010) | Medium | None | PENDING |

## Bug Fix Tasks (from structural analysis 2026-05-31 v2.14)
| ID | Description | Priority | File | Lines | Status |
|----|-------------|----------|------|-------|--------|
| T-023 | Fix B-011: Save `entry_rsi` into `open_position` in config on BUY and restore it in `__init__` alongside `entry_price`. Enables D-032 dynamic threshold to survive restarts. | Medium | main.py | 232, 820–841 | PENDING |
| T-024 | Fix B-012: Change cadence check to use `len(strategic_trades)` not `len(trades)`. Filter emergency trades BEFORE the cadence gate so 3 emergency trades cannot trigger reflection. | Medium | main.py | 374–376 | PENDING |
| T-025 | Fix B-013: Wire `restore_strategy()` into `self_improve_strategies()` — call it when strategy performs worse after 2+ consecutive reflection cycles. Or expose via manage_trader.sh `rollback` command. | Medium | main.py | 478 | PENDING |
| T-026 | Fix B-014: Replace `pgrep -a "python" \| grep "/.*main\.py"` with `pgrep -f "main.py"` throughout manage_trader.sh (start, stop, restart, status, clean blocks). | Low | manage_trader.sh | 23, 50, 62, 85, 160 | PENDING |
| T-027 | Fix B-015: Update hardcoded version string in manage_trader.sh status output to `"Version 2.15"`. | Low | manage_trader.sh | 106 | PENDING |
| T-028 | Fix B-016: Change `clean` command to `del d["open_position"]` (with existence check) instead of `d["open_position"]={}`. D-009/D-020 compliance. | Low | manage_trader.sh | 210–212 | PENDING |

## Completed Tasks
| ID | Description | Bug/Decision | Status |
|----|-------------|--------------|--------|
| T-029b | Fix B-017: `target_ret` NameError in `_generate_and_apply_hypotheses()` | B-017/D-043 | COMPLETED |
| T-030 | Fix B-018: Hypothesis ledger key schema mismatch with dashboard display | B-018/D-044 | COMPLETED |
| T-031 | Fix B-019: Stop-loss triggers immediate re-buy in same cycle | B-019/D-045 | COMPLETED |
| T-005 | Verify emergency trades excluded from reflection pool | D-025 | COMPLETED |
| T-007 | Verify help display shows all commands | D-026 | COMPLETED |
| T-008 | Restore last_trade_usd_amount on startup | B-003/D-034 | COMPLETED |
| T-009 | Guard ticker['last'] in stop-loss path | B-001/D-035 | COMPLETED |
| T-010 | Clear entry_rsi in stop-loss paths | B-002/D-036 | COMPLETED |
| T-011 | del open_position in emergency_stop_trader | B-008/D-042 | COMPLETED |
| T-012 | Numeric confidence for hypothesis sort | B-004/D-037 | COMPLETED |
| T-013 | Correct RSI sell log label | B-006/D-040 | COMPLETED |
| T-014 | Remove locals() in restore_strategy() | B-005/D-039 | COMPLETED |
| T-015 | Remove dead-code init guard | B-009/D-041 | COMPLETED |
| T-017 | Reload config from disk each run_cycle() | B-007/D-038 | COMPLETED |
| T-022 | Fix B-010: `self.entry_price` tracks weighted avg price on BUY. SELL PnL calc uses correct base. | B-010 | COMPLETED |

## Task Dependencies
```
T-022 (B-010 entry_price)  → correct PnL data → reliable brain learning
T-023 (B-011 entry_rsi)    → D-032 dynamic threshold survives restart
T-024 (B-012 cadence gate) → brain only fires on strategic trades (D-025 intent)
T-025 (B-013 rollback)     → PRIMARY GOAL rollback capability becomes functional
T-022 + T-023 + T-024      → T-025 (rollback meaningful only with correct data)
T-016 (git)                → safe baseline before T-022–T-025 changes
T-026 + T-027 + T-028      → manage_trader.sh fully consistent with D-016/D-009
T-003                      → T-019 (verify hypothesis_ledger dashboard display)
T-029                      → reduce stop-loss chain loss events (L-010)
```

---
**See PROJECT_STATE.md for verification status, deferred items, and documentation gaps.**
**Last Updated:** 2026-06-02 15:41 | Engineer: J.A.R.V.I.S.
