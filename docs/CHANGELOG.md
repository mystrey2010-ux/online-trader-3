# CHANGELOG — Online Trader-3

## v2.15 (2026-06-02)
- B-017: Fixed `NameError: target_ret not defined` in `_generate_and_apply_hypotheses()` — self-improvement brain was completely broken; hypotheses could never be generated or logged (D-043)
- B-018: Fixed hypothesis ledger entries storing wrong key names — `summarize_performance.py` reads `parameter/old_value/new_value/regime/direction` but engine wrote `regime_tag/expected_score_direction` only; all fields showed `?` in dashboard (D-044)
- B-019: Fixed stop-loss triggering immediate re-buy in same cycle — after stop-loss sell, `current_position` cleared to None so buy branch fired immediately (RSI still low at trigger point); added `return` after stop-loss execution (D-045)

## v2.14 (2026-05-31)
- B-003: Restored last_trade_usd_amount from config on startup — PnL/fees now correct after restart (D-034)
- B-001: Removed unbound ticker['last'] re-fetch in stop-loss path — uses resolved current_price (D-035)
- B-002: Clear entry_rsi in stop-loss success and failure paths (D-036)
- B-004: Hypothesis selection now uses numeric confidence float not string sort (D-037)
- B-007: Config reloaded from disk at top of run_cycle() — EMERGENCY_STOP picked up without restart (D-038)
- B-005: restore_strategy() rollback metrics set to None directly — locals() scope bug fixed (D-039)
- B-006: RSI sell log label corrected from "(Stop-Loss)" to "(RSI Signal)" (D-040)
- B-009: Removed dead-code init guard in self_improve_strategies() else branch (D-041)
- B-008: emergency_stop_trader.py — del open_position instead of set to None (D-042)
- B-010: Fixed SELL PnL calculation to use weighted average entry price from open_position instead of individual buy price (T-022)

## v2.13 (2026-05-29 / 2026-05-31)
- Emergency stop interface redesigned (emergency_only, emergency_sell, off)
- Help display when no arguments passed
- Renamed legacy commands: `close` → `emergency_sell`, `clear` → `off`, flag_only → `emergency_only`
- Emergency stop trade schema: added gross_pnl_usd, fee_usd, net_pnl_usd fields (D-029)
- RSI signal log accuracy: fixed misleading "is between" message (D-030)
- Fee trap prevention: added profitability check before sell orders to avoid losses from trading fees (D-031)
- Dynamic RSI threshold: implemented adaptive sell threshold based on entry RSI and fee requirements (D-032)
- main.py indentation fix: stop-loss try/except and sell path trade record block off by 1 space — corrected (backup main.py.310526-225026)

## v2.12 (2026-05-29)
- Emergency trades excluded from self-improvement brain reflection pool (D-025)
- Added stop_loss_triggered and note fields to emergency trade records
- Filter logic excludes trades with stop_loss_triggered=true OR note="Emergency stop trade"

## v2.11 (2026-05-29)
- Emergency stop clear command added: emergency_stop_trader.py clear (D-024)
- Legacy main() removed, consolidated to if __name__ block

## v2.10 (2026-05-29)
- Emergency stop system: guard in run_cycle() (D-023), emergency_stop_trader.py script
- main.py corrupted & restored from backup; D-020 + D-023 re-applied
- Config cleaned: duplicate trades removed, null open_position removed

## v2.9 (2026-05-29)
- D-020: Position restoration on startup — prevents spurious BUY after restart

## v2.8 (2026-05-29)
- D-019: summarize_performance.py rewrite — 8 bugs fixed, 7-section dashboard, live BTC price

## v2.7+ (2026-05-29)
- D-017: Sell threshold docs corrected (83, not 90)
- D-018: Fee fields added to both sell paths
- D-016: PAPER/SANDBOX mode detection from CLI output
- D-013: format_dollar() replaces broken f-string comma patterns
- Dashboard consolidated to single file

## v2.6 (2026-05)
- L-018: Brain hypothesis regex fixed
- Per-trade performance table with fee-aware win/loss

## v2.5 (2026-05)
- Regime-aware tuning: _tag_regime() classifier, version tracking, strategy rollback
- Fee-aware evaluation in self-improvement brain
- Full trade history display

---
**Last Updated:** 2026-06-02 15:41 | Engineer: J.A.R.V.I.S.

## Git Repository Usage

This project uses a Git repository for version control, backup, and restore. Commit changes regularly; use branches for experimentation; and push to remote for backup. See .gitignore for files excluded from version control.
