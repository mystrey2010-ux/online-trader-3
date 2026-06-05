# KNOWN_ISSUES — Online Trader-3 v2.19

## Active
| ID | Issue | Severity | Mitigation |
|----|-------|----------|------------|
| L-005 | emergency_sell without position creates synthetic trade | Medium | Use only when position exists |

## Resolved
| ID | Version | Resolution |
|----|---------|------------|
| B-017 | v2.15 | NameError in _generate_and_apply_hypotheses() fixed |
| B-018 | v2.15 | Hypothesis ledger key schema in dashboard |
| B-019 | v2.15 | Stop-loss same-cycle re-buy prevented |
| B-024 | v2.17 | SL_COOLDOWN_SECONDS variable fixed |
| D-074 | v2.18 | Daily loss limit circuit breaker |
| N-004 | v2.19 | Multi-feed news sentiment aggregation |
| D-077 | v2.19 | Daily PnL calculation uses exchange balance |

---
**Last Updated:** 2026-06-05