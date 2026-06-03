# PROJECT STATE — Online Trader-3 v2.17

**Status:** PAPER/SANDBOX | EMERGENCY_STOP: CLEARED | Engine: RUNNING | Trade Progress: 16 completed (8 strategic wins, 8 stop-losses) | 1 open position

## Open Tasks
| ID | Description | Priority | Dependencies | Status |
|----|-------------|----------|--------------|--------|
| T-020 | Consolidate stop-loss into helper function | Low | None | PENDING |
| T-021 | Add sell_threshold to cycle log output | Low | None | PENDING |

## Bug Status
### Active
| ID | Description | Severity | Notes |
|----|-------------|----------|-------|
| L-003 | hypothesis_ledger waits 3 strategic trades after restart | Low | B-017 fix active, accumulating trades |
| L-004 | No position timeout mechanism | Low (deferred) | Per T-018: warn if open >24h |

### Resolved (v2.17)
| ID | Severity | Resolution |
|----|----------|------------|
| B-020 | Critical | D-060 — BUY block restructured to correct condition |
| B-021 | Low | D-061 — Dashboard dynamic sell threshold |
| B-022 | Low | B-022 — TREND FILTER comment indentation fix |
| B-023 | Low | B-023 — Added exchange/kraken_fee_pct keys |
| B-024 | High | Fixed undefined `SL_COOLDOWN_SECONDS` → `DEFAULT_SL_COOLDOWN` (300s cooldown now functional) |
| STAT-WINDOW | Medium | D-070 — evaluation_window_size (20) decoupled from cadence, cold-start fallback implemented |

### Resolved (v2.16)
| ID | Severity | Resolution |
|----|----------|------------|
| B-011 | Medium | D-046 — entry_rsi persisted in open_position config |
| B-012 | Medium | D-047 — Cadence check on strategic_trades count |
| B-013 | Medium | D-048 — restore_strategy() rollback trigger |
| T-029 | Medium | D-049 — Post-SL cooldown period |

### Resolved (v2.15)
| ID | Severity | Resolution |
|----|----------|------------|
| B-017 | Critical | D-043 — NameError in `_generate_and_apply_hypotheses()` blocked hypothesis generation |
| B-018 | Medium | D-044 — Hypothesis ledger key schema mismatch with dashboard |
| B-019 | Medium | D-045 — Stop-loss triggered immediate re-buy in same cycle |

## Verification Status
| Item | Verified | Notes |
|------|----------|-------|
| main.py syntax (v2.17) | ✓ | py_compile clean
| BACKTEST-GATE implementation | ✓ | D-069 - _run_local_backtest() active, gating logic verified
| STAT-WINDOW fix | ✓ | D-070 - evaluation_window_size (default 20) decoupled from cadence, cold-start fallback tested
| B-011/B-012/B-013/T-029 implementation | ✓ | Gap fixes applied and verified 2026-06-02 |
| B-017–B-019 fixed | ✓ | D-043/D-044/D-045 applied; engine restart needed |
| B-020/B-021/B-022/B-023 fixed | ✓ | v2.17 fixes applied (BUY block, sell threshold, TREND comment, config keys) |
| T-REGIME regime sync | ✓ | D-068 - 1d OHLCV for macro trend validated |
| Fee fields in both sell paths | ✓ | D-018 |
| Stop-loss cooldown | ✓ | D-049/B-024 — 300s cooldown after stop-loss (DEFAULT_SL_COOLDOWN constant used) |
| B-024 (undefined variable) | ✓ | SL_COOLDOWN_SECONDS → DEFAULT_SL_COOLDOWN fixed, py_compile clean |
| Trend filter active | ✓ | D-055 — skips BUY when price declining over 20 periods |

## Performance Observations (2026-05-31 to 2026-06-02)
- 12 completed trades: 5 wins (+$0.159 total net), 7 stop-losses (-$5.701 total net)
- Net PnL: approximately -$5.542 (pre-B-020 fix)
- Dominant pattern: BTC in extended downtrend (~$74k → ~$67k), stop-losses firing repeatedly
- B-017 (brain NameError) meant zero self-improvement occurred across trades 1-11 — first hypothesis logged at trade 12
- B-019 (same-cycle re-buy) contributed to consecutive SL chains (trade 2→3, 8→9)
- B-020 fix (v2.17) prevents spurious BUY while holding position

## Deferred Items (Q - Quality of Service)
| ID | Item | Notes |
|----|------|-------|
| Q-003 | Multi-symbol support | Architecture supports, not implemented |
| Q-004 | Native stop-loss orders (Kraken API) | Currently price-check based |

## Documentation Gaps
| Priority | Issue | Action |
|----------|-------|--------|
| Medium | Rollback trigger conditions | D-048: Sharpe < 0 after tuning triggers rollback |
| Medium | Emergency stop duplicate trade risk | L-005: Only use emergency_sell when position exists |

---
**Last Updated:** 2026-06-03 09:00 | Engineer: J.A.R.V.I.S.
