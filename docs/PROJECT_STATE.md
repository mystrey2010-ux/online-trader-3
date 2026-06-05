# PROJECT STATE — Online Trader-3 v2.19

**Status:** PAPER/SANDBOX | EMERGENCY_STOP: CLEARED | Engine: RUNNING | Trade Progress: 5 total (2 strategic)

## Open Tasks
| ID | Description | Priority | Dependencies | Status |
|----|-------------|----------|--------------|--------|

## Bug Status
### Active
| ID | Description | Severity | Notes |
|----|-------------|----------|-------|
| L-005 | emergency_sell without position creates synthetic trade | Medium | Manual caution required - only use when position exists |

### Resolved (v2.19)
| ID | Severity | Resolution |
|----|----------|------------|
| N-004 | Low | Multi-feed news sentiment aggregation - queries 4 RSS feeds |
| D-077 | High | Fixed daily loss calculation - uses exchange balance for limit |

### Resolved (v2.18)
| ID | Severity | Resolution |
|----|----------|------------|
| D-074 | High | Daily loss limit circuit breaker implemented in run_cycle() |

### Resolved (v2.17)
| ID | Severity | Resolution |
|----|----------|------------|
| B-011 | Medium | entry_rsi persisted in open_position config |
| B-012 | Medium | Cadence check on strategic_trades count |
| B-013 | Medium | restore_strategy() rollback trigger |
| T-029 | Medium | Post-SL cooldown period |
| B-024 | High | Fixed undefined SL_COOLDOWN_SECONDS |

### Resolved (v2.15-2.16)
| ID | Severity | Resolution |
|----|----------|------------|
| B-017 | Critical | NameError in _generate_and_apply_hypotheses() fixed |
| B-018 | Medium | Hypothesis ledger key schema mismatch with dashboard |
| B-019 | Medium | Stop-loss triggered immediate re-buy in same cycle |

## Verification Status
| Item | Verified | Notes |
|------|----------|-------|
| main.py syntax (v2.19) | ✓ | py_compile clean |
| Daily loss limit (D-074) | ✓ | Uses daily_start_balance_usd × max_daily_loss_pct |
| News sentiment (RSS) | ✓ | 4 RSS feeds working (Cointelegraph, TradingView, LiveBitcoinNews, CryptoSlate) |
| Dashboard strategic trade count | ✓ | Now correctly shows 5 total (2 strategic) |

## Performance Observations
- Trades: 5 total (2 strategic, 3 stop-loss)
- Strategic: 1 win (+$0.0017), 1 pending
- Net PnL: -$0.40 USD (fee-adjusted)
- Position: 0.00016 BTC @ $61,030.40
- News sentiment: 4/4 feeds succeeded

## Deferred Items (Q - Quality of Service)
| ID | Item | Notes |
|----|------|-------|
| Q-003 | Multi-symbol support | Architecture supports, not implemented |
| Q-004 | Native stop-loss orders (Kraken API) | Currently price-check based |

---
**Last Updated:** 2026-06-05 | Engineer: opencode