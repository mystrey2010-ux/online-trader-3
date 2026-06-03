# PROJECT STATE — Online Trader-3 v2.18

**Status:** PAPER/SANDBOX | EMERGENCY_STOP: CLEARED | Engine: READY | Trade Progress: 0 completed | 1 open position

## Open Tasks
| ID | Description | Priority | Dependencies | Status |
|----|-------------|----------|--------------|--------|
| T-021 | Add sell_threshold to cycle log output | Low | None | COMPLETED |
| N-002 | Fix CryptoPanic RSS feed parsing (502/malformed XML) | Medium | None | OPEN |

## Bug Status
### Active
| ID | Description | Severity | Notes |
|----|-------------|----------|-------|
| L-003 | hypothesis_ledger waits 3 strategic trades after restart | Low | B-017 fix active, accumulating trades |

### Resolved (v2.18)
| ID | Severity | Resolution |
|----|----------|------------|
| B-020 | Critical | Cascade accumulation bug fixed, position sizing now controlled |
| N-001 | New | RSS-based news sentiment integration (free, no API token) |

### Resolved (v2.17)
| ID | Severity | Resolution |
|----|----------|------------|
| B-011 | Medium | D-046 — entry_rsi persisted in open_position config |
| B-012 | Medium | D-047 — Cadence check on strategic_trades count |
| B-013 | Medium | D-048 — restore_strategy() rollback trigger |
| T-029 | Medium | D-049 — Post-SL cooldown period |
| B-024 | High | Fixed undefined `SL_COOLDOWN_SECONDS` → `DEFAULT_SL_COOLDOWN` |

### Resolved (v2.15-2.16)
| ID | Severity | Resolution |
|----|----------|------------|
| B-017 | Critical | D-043 — NameError in `_generate_and_apply_hypotheses()` blocked hypothesis generation |
| B-018 | Medium | D-044 — Hypothesis ledger key schema mismatch with dashboard |
| B-019 | Medium | D-045 — Stop-loss triggered immediate re-buy in same cycle |

## Verification Status
| Item | Verified | Notes |
|------|----------|-------|
| main.py syntax (v2.18) | ✓ | py_compile clean |
| main.py syntax (v2.18 + T-021) | ✓ | py_compile clean |
| News sentiment (RSS) | ✗ | CryptoPanic RSS returns 502, malformed XML (N-002) |
| Position sizing (10%) | ✓ | Updated in config.json, validated against Kraken balance |
| Cascade bug fix | ✓ | Trade #13 position accumulation resolved |
| Stop-loss helper (T-020) | ✓ | _execute_stop_loss() extracted, syntax verified |
| Sell threshold log (T-021) | ✓ | Added sell_threshold to cycle log output |

## Performance Observations
- Active position: ~0.00015 BTC @ $65,559 (validated against Kraken paper account)
- Position sizing: 10% (user-adjusted from 3% to 0.1)
- News sentiment: Temporarily unavailable (N-002 - CryptoPanic RSS 502 error)

## Deferred Items (Q - Quality of Service)
| ID | Item | Notes |
|----|------|-------|
| Q-003 | Multi-symbol support | Architecture supports, not implemented |
| Q-004 | Native stop-loss orders (Kraken API) | Currently price-check based |

---
**Last Updated:** 2026-06-03 23:55 | Engineer: opencode