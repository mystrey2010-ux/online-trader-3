# PROJECT STATE — Online Trader-3 v2.16

**Status:** PAPER/SANDBOX | EMERGENCY_STOP: CLEARED | Engine: RUNNING | Trade Progress: 12 completed (5 strategic wins, 7 stop-losses) | 1 open position

## Open Tasks
| ID | Description | Priority | Dependencies | Status |
|----|-------------|----------|--------------|--------|
| T-003 | Confirm hypothesis_ledger populated after first reflection post-B-017 fix | Medium | Requires restart + 3 strategic trades | DONE |
| T-016 | Add git version control (git init + baseline commit) | High | None | DONE |
| T-018 | Position timeout: warn if open >24h (L-004) | Medium | None | DONE |
| T-019 | Verify hypothesis_ledger dashboard display works with new key schema (D-044) | Medium | T-003 | PENDING |
| T-020 | Consolidate stop-loss into helper function | Low | None | PENDING |
| T-021 | Add sell_threshold to cycle log output | Low | None | PENDING |
| T-023 | Fix B-011: Save/restore entry_rsi in open_position config | Medium | main.py | DONE |
| T-024 | Fix B-012: Cadence check on strategic_trades count not all trades | Medium | main.py 376 | DONE |
| T-025 | Fix B-013: Wire restore_strategy() into brain loop or CLI | Medium | main.py 478 | DONE |
| T-029 | Post-SL cooldown period to prevent immediate re-buy after stop-loss (L-010) | Medium | main.py | DONE |
| T-TREND | Trend filter to prevent buying in sustained downtrend | Medium | main.py | DONE |

## Bug Status
### Active (v2.15)
| ID | Description | Severity | Task |
|----|-------------|----------|------|
| B-014 | manage_trader.sh fragile pgrep pattern | Low | T-026 |
| B-015 | manage_trader.sh stale version string | Low | T-027 |
| B-016 | manage_trader.sh clean sets open_position={} not deletes | Low | T-028 |

### Resolved (v2.15 — 2026-06-02)
| ID | Severity | Resolution |
|----|----------|------------|
| B-017 | Critical | D-043 — NameError in `_generate_and_apply_hypotheses()` blocked all hypothesis generation |
| B-018 | Medium | D-044 — Hypothesis ledger key schema mismatch with dashboard |
| B-019 | Medium | D-045 — Stop-loss triggered immediate re-buy in same cycle |

### Resolved (v2.16 — 2026-06-02)
| ID | Severity | Resolution |
|----|----------|------------|
| B-011 | Medium | D-046 — entry_rsi persisted in open_position config |
| B-012 | Medium | D-047 — Cadence check on strategic_trades count |
| B-013 | Medium | D-048 — restore_strategy() rollback trigger |
| T-029 | Medium | D-049 — Post-SL cooldown period |

### Resolved (v2.14
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
| B-010 | High | T-022 (self.entry_price = avg_price on BUY) |

## Verification Status
| Item | Verified | Notes |
|------|----------|-------|
| main.py syntax (v2.16) | ✓ | py_compile clean |
| B-011/B-012/B-013/T-029 implementation | ✓ | Gap fixes applied and verified 2026-06-02 |
| B-017–B-019 fixed | ✓ | D-043/D-044/D-045 applied; engine restart needed |
| B-001–B-010 all fixed | ✓ | D-034 through D-042 / T-022 applied |
| Fee fields in both sell paths | ✓ | D-018 |
| Fee trap prevention | ✓ | D-031 — confirmed holding at RSI 84-87+ in live session |
| Dynamic RSI threshold | ✓ | D-032 — B-011 fix ensures threshold survives restart |
| Position restoration on startup | ✓ | D-020 |
| Config reloaded each cycle | ✓ | D-038 |
| EMERGENCY_STOP guard | ✓ | D-023 |
| Emergency trades excluded from brain | ✓ | D-025 — B-012 fix ensures correct count-based filtering |
| Hypothesis numeric confidence | ✓ | D-037 |
| Hypothesis ledger key schema | ✓ | D-044 — now includes display alias keys |
| Stop-loss no same-cycle re-buy | ✓ | D-045 |
| Stop-loss cooldown | ✓ | D-049 — 300s cooldown after stop-loss |
| RSI signal log accuracy | ✓ | D-030/D-040 |
| Python interpreter standardized | ✓ | Shebang/detection updated |
| Deduplication of previous_strategies | ✓ | D-028 |

## Performance Observations (2026-05-31 to 2026-06-02)
- 12 completed trades: 5 wins (+$0.159 total net), 7 stop-losses (-$5.701 total net)
- Net PnL: approximately -$5.542
- Dominant pattern: BTC in extended downtrend (~$74k → ~$67k), stop-losses firing repeatedly
- B-017 (brain NameError) meant zero self-improvement occurred across trades 1-11 — first hypothesis logged at trade 12
- B-019 (same-cycle re-buy) contributed to consecutive SL chains (trade 2→3, 8→9)
- After B-017 fix + restart: 1 hypothesis logged after trade 12 (indicator_threshold: 63.0 → 66.15)

## Deferred Items (Q - Quality of Service)
| ID | Item | Notes |
|----|------|-------|
| Q-003 | Multi-symbol support | Architecture supports, not implemented |
| Q-004 | Native stop-loss orders (Kraken API) | Currently price-check based |
| D-HYP-003 | hypothesis_ledger display on dashboard | Verify via T-019 post-B-018 fix |

## Documentation Gaps
| Priority | Issue | Recommended Action |
|----------|-------|-------------------|
| Medium | Rollback trigger conditions documented | D-048: Sharpe < 0 after tuning triggers rollback |
| Medium | Emergency stop duplicate trade risk | Clarify L-005 mitigation |

## Recent Documentation Updates (2026-06-02)
| File | Changes |
|------|---------|
| NOW.md | Added entry_rsi persistence confirmation |
| CHANGELOG.md | Deduplicated v2.16 entries |
| ARCHITECTURE.md | Fixed B-011 entry_rsi documentation contradiction |
| config.json | Added entry_rsi to open_position for D-032 compatibility |

---
**Last Updated:** 2026-06-02 16:00 | Engineer: J.A.R.V.I.S.
