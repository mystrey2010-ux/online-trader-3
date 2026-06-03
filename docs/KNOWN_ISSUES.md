# KNOWN ISSUES — Online Trader-3 v2.17

## ACTIVE (Resolving)
| ID | Issue | Severity | Resolution Status |
|----|-------|----------|-------------------|
| L-003 | hypothesis_ledger empty until 3 strategic trades complete after B-017 fix | Low | Requires restart + 3 strategic trades to trigger first reflection |
| L-004 | No position timeout mechanism | Low (deferred) | Re-evaluate if open >24h without SELL/SL signal (T-018) |
| N-002 | CryptoPanic RSS feed returns 502/malformed XML - news sentiment broken | Medium | External service; add timeout + error handling in v2.19 |

## BUGS — Confirmed, Pending Fix
| ID | File | Line(s) | Description | Severity |
|----|------|---------|-------------|----------|
| None | — | — | All known bugs resolved in v2.17 | — |

## WATCH (Monitor)
| ID | Issue | Severity | Mitigation/Notes |
|----|-------|----------|------------------|
| L-005 | emergency_stop_trader.py emergency_sell without open position creates synthetic trade record | Medium | Only use `emergency_sell` when position exists |
| L-006 | Trade history loss during emergency stop resolution violates D-009/D-020 invariants | Medium | Regular config backups; T-016 (git) will resolve permanently |
| L-007 | Editor auto-indent can corrupt main.py indentation (happened twice) | Low | Verify with py_compile after every edit session |
| L-008 | Dynamic sell threshold falls back to `threshold+20` after restart — B-011 root cause | Low | Monitor after B-011 fixed |
| L-009 | sell path `last_trade_usd_amount` not reset to 0 after sell — next BUY overwrites it and on restart with no position it defaults to 0.0 | Info | No action needed unless buy/sell logic changes |
| L-010 | Repeated stop-losses at declining prices (BTC falling trend): bot re-buys immediately after SL and takes another SL loss next cycle. Pattern visible in trade history (trades 2–4, 7, 9–10). B-019 fixes same-cycle re-buy; underlying trend-following risk remains. | Medium | Consider trend filter or cooldown period post-SL (T-029) |

## RESOLVED
| ID | Issue | Severity | Resolution |
| B-024 [RESOLVED] | Undefined `SL_COOLDOWN_SECONDS` variable in stop-loss path caused NameError on cooldown activation | High | Fixed: Changed to `DEFAULT_SL_COOLDOWN` (line 29) - cooldown now correctly enforces 300s after stop-loss |
| B-020 [RESOLVED] | BUY execution block nested under `if self.current_position == 'long'` — fired every cycle while holding, draining USD to near-zero via 64+ unintended consecutive buys | Critical | B-020/D-060 (v2.17) — moved buy block inside correct `if rsi_val < buy_threshold and self.current_position is None` branch |
| B-021 [RESOLVED] | Dashboard section [3] hardcoded sell threshold as `threshold+20` regardless of D-032 dynamic value | Low | B-021/D-061 (v2.17) — replicates engine D-032 formula using entry_rsi from open_position |
| B-022 [RESOLVED] | Stale `# ===== TREND FILTER CHECK` comment at column 0 in main.py (outside run_cycle indentation) | Low | B-022 (v2.17) — fixed indentation to 12 spaces inside method |
| B-023 [RESOLVED] | config.json missing `exchange` and `kraken_fee_pct` top-level keys per schema | Low | B-023 (v2.17) — added both keys with correct defaults |
| B-017 [RESOLVED] | `NameError: target_ret not defined` in `_generate_and_apply_hypotheses()` — self-improvement brain completely broken, hypotheses never generated | Critical | D-043 (v2.15) |
| B-018 [RESOLVED] | Hypothesis ledger entries used wrong key names — dashboard showed `?` for all fields | Medium | D-044 (v2.15) |
| B-019 [RESOLVED] | Stop-loss triggered immediate re-buy in same cycle | Medium | D-045 (v2.15) |
| B-011 [RESOLVED] | entry_rsi lost on restart — D-032 dynamic threshold bypassed | Medium | D-046 (v2.16) |
| B-012 [RESOLVED] | Reflection cadence fires on emergency trades (D-025 intent violated) | Medium | D-047 (v2.16) |
| B-013 [RESOLVED] | restore_strategy() never called — rollback dead code | Medium | D-048 (v2.16) |
| T-029 [RESOLVED] | Post-SL cooldown prevents immediate re-buy after stop-loss | Medium | D-049 (v2.16) |
| B-001 [RESOLVED] | ticker unbound in stop-loss if initial fetch failed | High | D-035 |
| B-002 [RESOLVED] | entry_rsi not cleared after stop-loss | Medium | D-036 |
| B-003 [RESOLVED] | last_trade_usd_amount=0 after restart | High | D-034 |
| B-004 [RESOLVED] | Hypothesis selected by string sort | Medium | D-037 |
| B-005 [RESOLVED] | restore_strategy() locals() scope | Low | D-039 |
| B-006 [RESOLVED] | RSI sell log said "(Stop-Loss)" | Low | D-040 |
| B-007 [RESOLVED] | config not reloaded each cycle | Low | D-038 |
| B-008 [RESOLVED] | emergency_stop_trader set open_position=None | Medium | D-042 |
| B-009 [RESOLVED] | Dead-code init guard in self_improve_strategies() | Low | D-041 |
| B-010 [RESOLVED] | SELL PnL uses self.entry_price (individual buy) not weighted avg | High | T-022 |
| B-014 [RESOLVED] | manage_trader.sh fragile pgrep pattern | Low | Fixed in v2.16 - all patterns use pgrep -f "main.py" |
| B-015 [RESOLVED] | manage_trader.sh stale version string | Low | Fixed in v2.16 - updated to Version 2.16 |
| B-016 [RESOLVED] | clean command sets open_position={} not deletes key | Low | Fixed in v2.16 - uses d.pop('open_position', None) |
| B-EMERGENCY [RESOLVED] | EMERGENCY_STOP flag blocked trading logic | High | D-024/D-026 |
| DASHBOARD-ENGINE-DETECTION [RESOLVED] | pgrep -a python3 missed venv process | Low | pgrep -f "main.py" |

---
**Last Updated:** 2026-06-03 23:55 | Engineer: opencode
