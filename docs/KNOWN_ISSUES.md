# KNOWN ISSUES — Online Trader-3 v2.15

## ACTIVE (Resolving)
| ID | Issue | Severity | Resolution Status |
|----|-------|----------|-------------------|
| L-003 | hypothesis_ledger empty until 3 strategic trades complete after B-017 fix | Low | Expected — requires 3 strategic trades post-restart to trigger first reflection |
| L-004 | No position timeout mechanism | Low (deferred) | Re-evaluate if open >24h without SELL/SL signal (T-018) |

## BUGS — Confirmed, Pending Fix
| ID | File | Line(s) | Description | Severity |
|----|------|---------|-------------|----------|
| B-011 | main.py | 232, 726 | `self.entry_rsi` never saved to `open_position` in config, never restored on startup. On restart with open position, dynamic sell threshold never activates — always falls back to `threshold+20` (D-032 silently bypassed). | Medium |
| B-012 | main.py | 376 | `self_improve_strategies()` cadence check uses `len(trades)` (all trades) not `len(strategic_trades)`. 3 emergency stop-losses alone can trigger reflection with zero strategic trades (violates D-025 intent). | Medium |
| B-013 | main.py | 478 | `restore_strategy()` is dead code — defined but never called. Brain can never roll back a bad hypothesis. Rollback capability (PRIMARY GOAL) is non-functional. | Medium |
| B-014 | manage_trader.sh | 23, 50, 62, 85 | Uses `pgrep -a "python" \| grep "/.*main\.py"` — fragile pattern that fails in virtualenvs where interpreter is just `python`. Should use `pgrep -f "main.py"` (same fix already applied to summarize_performance.py per D-016). | Low |
| B-015 | manage_trader.sh | 106 | Hardcoded version string stale — needs updating to 2.15. | Low |
| B-016 | manage_trader.sh | 210–212 | `clean` command sets `open_position={}` (empty dict) instead of deleting the key. Violates D-009/D-020 — cleanup_stale_positions() on next startup handles it but creates a stale null entry. | Low |

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
|----|-------|----------|------------|
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
| B-EMERGENCY [RESOLVED] | EMERGENCY_STOP flag blocked trading logic | High | D-024/D-026 |
| DASHBOARD-ENGINE-DETECTION [RESOLVED] | pgrep -a python3 missed venv process | Low | pgrep -f "main.py" |

---
**Last Updated:** 2026-06-02 15:41 | Engineer: J.A.R.V.I.S.
