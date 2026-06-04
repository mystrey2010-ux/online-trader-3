# KNOWN ISSUES — Online Trader-3 v2.19

## ACTIVE
| ID | Issue | Severity | Resolution Status |
|----|-------|----------|-------------------|

## WATCH (Monitor)
| ID | Issue | Severity | Mitigation/Notes |
|----|-------|----------|------------------|
| L-005 | emergency_stop_trader.py emergency_sell without open position creates synthetic trade record | Medium | Only use `emergency_sell` when position exists |

## RESOLVED (v2.19)
| ID | Issue | Severity | Resolution |
|----|-------|----------|------------|
| D-074 | High | Daily loss limit circuit breaker implemented in run_cycle() |
| N-004 | Low | Multi-feed news sentiment aggregation (4 RSS feeds) wired to config |
| L-010 | Medium | T-029 cooldown + D-074 daily loss limit reduce consecutive stop-loss risk |

## RESOLVED (v2.18)
| ID | Issue | Severity | Resolution |
|----|-------|----------|------------|
| N-002 | Medium | Switched CryptoPanic RSS to CoinTelegraph RSS feed |
| D-071 | Medium | Stop-loss logic extracted into _execute_stop_loss() helper |

## RESOLVED (v2.17)
| ID | Issue | Severity | Resolution |
|----|-------|----------|------------|
| B-011 | Medium | entry_rsi persisted in open_position config |
| B-012 | Medium | Cadence check on strategic_trades count |
| B-013 | Medium | restore_strategy() rollback trigger |
| T-029 | Medium | Post-SL cooldown period |
| B-024 | High | Fixed undefined SL_COOLDOWN_SECONDS variable |

## RESOLVED (v2.15-2.16)
| ID | Issue | Severity | Resolution |
|----|-------|----------|------------|
| B-017 | Critical | NameError in _generate_and_apply_hypotheses() |
| B-018 | Medium | Hypothesis ledger key schema mismatch with dashboard |
| B-019 | Medium | Stop-loss triggered immediate re-buy in same cycle |

---
**Last Updated:** 2026-06-04 | Engineer: opencode