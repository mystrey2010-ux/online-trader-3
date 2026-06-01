# PROJECT STATE — Online Trader-3 v2.14

**Status:** PAPER/SANDBOX | EMERGENCY_STOP: CLEARED | Engine: STOPPED (restart required) | Trade Progress: 0/3 strategic trades (0 completed, 1 open position)

## Open Tasks
| ID | Description | Priority | Dependencies | Status |
|----|-------------|----------|--------------|--------|
| T-003 | Confirm hypothesis_ledger populated at trade #3 | Medium | Requires 3 strategic trades (0/3 completed) | PENDING |
| T-016 | Add git version control (git init + baseline commit) | High | None | PENDING |
| T-018 | Position timeout: warn if open >24h (L-004) | Medium | None | PENDING |
| T-019 | hypothesis_ledger dashboard display (D-HYP-003) | Medium | T-003 | PENDING |
| T-020 | Consolidate stop-loss into helper function | Low | None | PENDING |
| T-021 | Add sell_threshold to cycle log output | Low | None | PENDING |
| T-022 | Fix B-010: self.entry_price = avg_price on BUY (not individual price) | High | main.py 820 | PENDING |
| T-023 | Fix B-011: save/restore entry_rsi in open_position config | Medium | main.py 232, 841 | PENDING |
| T-024 | Fix B-012: cadence check on strategic_trades count not all trades | Medium | main.py 376 | PENDING |
| T-025 | Fix B-013: wire restore_strategy() into brain loop or CLI | Medium | main.py 478 | PENDING |
| T-026 | Fix B-014: pgrep -f "main.py" in manage_trader.sh | Low | manage_trader.sh | PENDING |
| T-027 | Fix B-015: update version string in manage_trader.sh to 2.14 | Low | manage_trader.sh 106 | PENDING |
| T-028 | Fix B-016: del open_position in clean command | Low | manage_trader.sh 210 | PENDING |

## Bug Status (second structural analysis 2026-05-31)
| ID | Description | Severity | Task |
|----|-------------|----------|------|
| B-010 | SELL PnL uses self.entry_price (individual buy) not weighted avg | High | T-022 |
| B-011 | entry_rsi lost on restart — D-032 dynamic threshold bypassed | Medium | T-023 |
| B-012 | Reflection cadence fires on emergency trades (D-025 intent violated) | Medium | T-024 |
| B-013 | restore_strategy() never called — rollback dead code | Medium | T-025 |
| B-014 | manage_trader.sh fragile pgrep pattern | Low | T-026 |
| B-015 | manage_trader.sh stale version string | Low | T-027 |
| B-016 | manage_trader.sh clean sets open_position={} not deletes | Low | T-028 |

## Resolved Bug Status (v2.14)
| ID | Severity | Resolution |
|----|----------|------------|
| B-001 | High | D-035 |
| B-002 | Medium | D-036 |
| B-003 | High | D-034 |
| B-004 | Medium | D-037 |
| B-005 | Low | D-039 |
| B-006 | Low | D-040 |
| B-007 | Low | D-038 |
| B-008 | Medium | D-042 |
| B-009 | Low | D-041 |

## Verification Status
| Item | Verified | Notes |
|------|----------|-------|
| main.py syntax (v2.14) | ✓ | py_compile clean |
| emergency_stop_trader.py syntax (v2.14) | ✓ | py_compile clean |
| B-001–B-009 all fixed | ✓ | D-034 through D-042 applied |
| Fee fields in both sell paths | ✓ | D-018 |
| Fee trap prevention | ✓ | D-031 — confirmed holding at RSI 84-87 in live session |
| Dynamic RSI threshold | ✓ | D-032 — NOTE: bypassed after restart until B-011 fixed |
| Position restoration on startup | ✓ | D-020 |
| Config reloaded each cycle | ✓ | D-038 |
| EMERGENCY_STOP guard | ✓ | D-023 |
| Emergency trades excluded from brain | ✓ | D-025 — NOTE: cadence check still uses all trades (B-012) |
| Hypothesis numeric confidence | ✓ | D-037 |
| RSI signal log accuracy | ✓ | D-030/D-040 |
| Python interpreter standardized | ✓ | Shebang/detection updated |
| Deduplication of previous_strategies | ✓ | D-028 |

## Deferred Items (Q - Quality of Service)
| ID | Item | Notes |
|----|------|-------|
| Q-003 | Multi-symbol support | Architecture supports, not implemented |
| Q-004 | Native stop-loss orders (Kraken API) | Currently price-check based |
| D-HYP-003 | hypothesis_ledger display on dashboard | T-019 |

## Documentation Gaps
| Priority | Issue | Recommended Action |
|----------|-------|-------------------|
| High | Position timeout undocumented | T-018 |
| Medium | Rollback trigger conditions undocumented | Clarify when restore_strategy() should fire (T-025) |
| Medium | Emergency stop duplicate trade risk | Clarify L-005 mitigation |

## Recent Documentation Updates
| File | Status | Backup |
|------|--------|--------|
| KNOWN_ISSUES.md | Added B-010 through B-016 | *.310526-230915 |
| TASKS.md | Added T-022 through T-028 + completed tasks table | *.310526-230915 |
| PROJECT_STATE.md | Updated to second analysis pass, all bugs tracked | *.310526-230915 |
| ARCHITECTURE.md | Bug table updated to B-010–B-016 | *.310526-230915 |

## Backup Reference
- Docs backups: `/docs/backups/`
- Latest code backup: `*.310526-230101`
- Latest docs backup batch: `*.310526-230915`
- Convention: `*.ddmmyy-hhmmss` prefix

---
**Last Updated:** 2026-05-31 23:15 | Engineer: J.A.R.V.I.S.

## Git Repository Usage

This project uses a Git repository for version control, backup, and restore. Commit changes regularly; use branches for experimentation; and push to remote for backup. See .gitignore for files excluded from version control.
