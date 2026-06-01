# KNOWN ISSUES — Online Trader-3 v2.14

## ACTIVE (Resolving)
| ID | Issue | Severity | Resolution Status |
|----|-------|----------|-------------------|
| L-003 | hypothesis_ledger empty until 3 strategic trades | Low | Expected — requires 3 trades to trigger self-improvement (D-006) |
| L-004 | No position timeout mechanism | Low (deferred) | Re-evaluate if open >24h without SELL/SL signal (T-018) |

## BUGS — Confirmed, Pending Fix (v2.14 analysis — 2026-05-31)
| ID | File | Line(s) | Description | Severity |
|----|------|---------|-------------|----------|
| B-010 | main.py | 820, 857 | Multi-buy `self.entry_price` stores individual buy price, not weighted avg. `config["open_position"]["entry_price"]` correctly stores avg_price but SELL PnL calc at L857 uses `self.entry_price` → wrong PnL on any 2nd+ buy. | High |
| B-011 | main.py | 232, 726 | `self.entry_rsi` never saved to `open_position` in config, never restored on startup. On restart with open position, dynamic sell threshold never activates — always falls back to `threshold+20` (D-032 silently bypassed). | Medium |
| B-012 | main.py | 376 | `self_improve_strategies()` cadence check uses `len(trades)` (all trades) not `len(strategic_trades)`. 3 emergency stop-losses alone can trigger reflection with zero strategic trades (violates D-025 intent). | Medium |
| B-013 | main.py | 478 | `restore_strategy()` is dead code — defined but never called. Brain can never roll back a bad hypothesis. Rollback capability (PRIMARY GOAL) is non-functional. | Medium |
| B-014 | manage_trader.sh | 23, 50, 62, 85 | Uses `pgrep -a "python" \| grep "/.*main\.py"` — fragile pattern that fails in virtualenvs where interpreter is just `python`. Should use `pgrep -f "main.py"` (same fix already applied to summarize_performance.py per D-016). | Low |
| B-015 | manage_trader.sh | 106 | Hardcoded version string `"Version 2.13"` — stale, now at v2.14. | Low |
| B-016 | manage_trader.sh | 210–212 | `clean` command sets `open_position={}` (empty dict) instead of deleting the key. Violates D-009/D-020 — cleanup_stale_positions() on next startup handles it but creates a stale null entry. | Low |

## WATCH (Monitor)
| ID | Issue | Severity | Mitigation/Notes |
|----|-------|----------|------------------|
| L-005 | emergency_stop_trader.py emergency_sell without open position creates synthetic trade record | Medium | Only use `emergency_sell` when position exists |
| L-006 | Trade history loss during emergency stop resolution violates D-009/D-020 invariants | Medium | Regular config backups; T-016 (git) will resolve permanently |
| L-007 | Editor auto-indent can corrupt main.py indentation (happened twice) | Low | Verify with py_compile after every edit session |
| L-008 | Dynamic sell threshold falls back to `threshold+20` after restart — B-011 root cause | Low | Monitor after B-011 fixed |
| L-009 | sell path `last_trade_usd_amount` not reset to 0 after sell — but next BUY overwrites it, and on restart with no position it defaults to 0.0. No active bug but worth watching if logic changes. | Info | No action needed unless buy/sell logic changes |

## RESOLVED
| ID | Issue | Severity | Resolution |
|----|-------|----------|------------|
| B-001 [RESOLVED] | ticker unbound in stop-loss if initial fetch failed | High | D-035 |
| B-002 [RESOLVED] | entry_rsi not cleared after stop-loss | Medium | D-036 |
| B-003 [RESOLVED] | last_trade_usd_amount=0 after restart | High | D-034 |
| B-004 [RESOLVED] | Hypothesis selected by string sort | Medium | D-037 |
| B-005 [RESOLVED] | restore_strategy() locals() scope | Low | D-039 |
| B-006 [RESOLVED] | RSI sell log said "(Stop-Loss)" | Low | D-040 |
| B-007 [RESOLVED] | config not reloaded each cycle | Low | D-038 |
| B-008 [RESOLVED] | emergency_stop_trader set open_position=None | Medium | D-042 |
| B-009 [RESOLVED] | Dead-code init guard in self_improve_strategies() | Low | D-041 |
| B-EMERGENCY [RESOLVED] | EMERGENCY_STOP flag blocked trading logic | High | D-024/D-026 |
| DASHBOARD-ENGINE-DETECTION [RESOLVED] | pgrep -a python3 missed venv process | Low | pgrep -f "main.py" |

---
**Last Updated:** 2026-05-31 23:15 | Engineer: J.A.R.V.I.S.

## Git Repository Usage

This project uses a Git repository for version control, backup, and restore. Commit changes regularly; use branches for experimentation; and push to remote for backup. See .gitignore for files excluded from version control.
