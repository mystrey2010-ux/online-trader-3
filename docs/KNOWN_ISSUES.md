# KNOWN_ISSUES — Online Trader-3 v2.19

## Active
| ID | Issue | Severity | Mitigation |
|----|-------|----------|------------|
| (none) | No active issues | - | - |

## Resolved
| ID | Version | Resolution |
|----|---------|------------|
| L-005 | v2.19 | emergency_sell now exits gracefully without synthetic trade |
| L-006 | v2.19 | Added missing strategy keys to all regime tuning maps |
| B-017 | v2.15 | NameError in _generate_and_apply_hypotheses() fixed |

## Verification Status
| ID | Status | Notes |
|----|--------|---------|
| D-074 | ✅ Confirmed working | Daily loss limit implemented and verified |
| D-077/D-078 | ✅ Confirmed working | daily_start_balance_usd stored per day, _calculate_daily_pnl() returns USD |

---
**Last Updated:** 2026-06-07