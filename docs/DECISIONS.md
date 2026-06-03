# DECISIONS — Online Trader-3

Key design decisions, one line each. Code location noted for traceability.

| ID | Decision | Where | Version |
|----|----------|-------|---------|
| D-006 | Self-improvement brain: regime-aware hypothesis generation after N trades | main.py self_improve_strategies() | v2.5 |
| D-009 | Position persists in config.json across restarts; restored on init | main.py __init__ | v2.5 |
| D-013 | format_dollar() / f"${val:.2f}" exclusively; NEVER comma specifier in f-strings | summarize_performance.py | v2.7+ |
| D-016 | PAPER/SANDBOX mode detected from Kraken CLI output, not config key | summarize_performance.py | v2.7+ |
| D-017 | Sell threshold = indicator_threshold + 20 (hardcoded). NOT a config field. NOT 90. | main.py run_cycle() | v2.7+ |
| D-018 | Both sell paths write gross_pnl_usd / fee_usd / net_pnl_usd at close | main.py run_cycle() | v2.7+ |
| D-019 | summarize_performance.py single-file rewrite: 8 bugs fixed, 7-section dashboard | summarize_performance.py | v2.8 |
| D-020 | Startup position restoration from config["open_position"] prevents spurious BUY | main.py __init__ | v2.9 |
| D-023 | EMERGENCY_STOP guard at top of run_cycle(): skips all logic when flag set | main.py run_cycle() | v2.10 |
| D-024 | Emergency stop cleared via emergency_stop_trader.py clear command, not manual key deletion | emergency_stop_trader.py | v2.11 |
| D-025 | Emergency trades (stop-loss/manual) excluded from self-improvement brain reflection pool | main.py self_improve_strategies() | v2.12 |
| D-026 | Emergency stop_trader.py interface: emergency_only, emergency_sell, off commands; show help when no args | emergency_stop_trader.py | v2.13 |
| D-027 | Clean restart preferred over restoring stale trade history after emergency stop resolution | config.json cleanup | v2.13+ |
| D-028 | Avoid duplicate strategy snapshots in previous_strategies when strategy unchanged | main.py self_improve_strategies() | v2.14 |
| D-029 | Emergency stop trades must include gross_pnl_usd, fee_usd, net_pnl_usd fields (consistent with D-018) | emergency_stop_trader.py | v2.13+ |
| D-030 | RSI signal waiting log must accurately reflect thresholds, not claim "is between" when RSI outside range | main.py run_cycle() | v2.13+ |
| D-031 | Fee trap prevention: check profitability after fees before executing sell orders to avoid losses | main.py run_cycle() | v2.13+ |
| D-032 | Dynamic RSI threshold: adaptive sell threshold based on entry RSI and fee requirements instead of fixed offset | main.py run_cycle() | v2.13+ |
| D-033 | main.py indentation fix: stop-loss try/except + sell path trade record block corrected (off by 1 space) — no logic change | main.py run_cycle() | v2.13+ |
| D-034 | B-003 fix: restore last_trade_usd_amount from open_position on startup so PnL/fee correct on first sell after restart | main.py __init__ | v2.14 |
| D-035 | B-001 fix: stop-loss path uses existing current_price (already resolved) — never re-access ticker['last'] which may be unbound | main.py run_cycle() | v2.14 |
| D-036 | B-002 fix: clear entry_rsi in stop-loss success AND failure paths alongside current_position/entry_price | main.py run_cycle() | v2.14 |
| D-037 | B-004 fix: hypothesis_entry includes numeric confidence float; max() selects by h["confidence"] not string h["confidence_reasoning"] | main.py _generate_and_apply_hypotheses() | v2.14 |
| D-038 | B-007 fix: reload config from disk at top of run_cycle() to pick up external writes without restart | main.py run_cycle() | v2.14 |
| D-039 | B-005 fix: restore_strategy() rollback metrics set to None directly — locals() from self_improve_strategies() are out of scope | main.py restore_strategy() | v2.14 |
| D-040 | B-006 fix: RSI sell log corrected to "TRADE CLOSED (RSI Signal)" | main.py run_cycle() | v2.14 |
| D-041 | B-009 fix: removed dead-code version/previous_strategies init guard inside self_improve_strategies() else branch | main.py self_improve_strategies() | v2.14 |
| D-042 | B-008 fix: emergency_stop_trader.py uses del cfg["open_position"] instead of = None (D-009/D-020 compliance) | emergency_stop_trader.py | v2.14 |
| D-043 | B-017 fix: `_generate_and_apply_hypotheses()` reads `target_daily_return`/`max_daily_drawdown` from `self.config` directly — they are not in scope from `self_improve_strategies()` | main.py _generate_and_apply_hypotheses() | v2.15 |
| D-044 | B-018 fix: hypothesis ledger record now includes `parameter`, `old_value`, `new_value`, `regime`, `direction` alias keys alongside existing keys for `summarize_performance.py` display compatibility | main.py _generate_and_apply_hypotheses() | v2.15 |
| D-045 | B-019 fix: `return` added after stop-loss sell execution so buy branch cannot fire in same cycle immediately after stop-loss clears `current_position` | main.py run_cycle() | v2.15 |
| D-046 | B-011 fix: `entry_rsi` persisted in open_position config + restored on startup for D-032 dynamic threshold | main.py __init__, run_cycle() | v2.16 |
| D-047 | B-012 fix: Cadence check uses strategic_trades.length, not trades.length (D-025 compliance) | main.py self_improve_strategies() | v2.16 |
| D-048 | B-013 fix: restore_strategy() called when Sharpe < 0 after hypothesis tuning | main.py self_improve_strategies() | v2.16 |
| D-049 | T-029 fix: 300s cooldown after stop-loss prevents immediate re-buy | main.py run_cycle() | v2.16 |
| D-055 | T-018 fix: Trend filter skips BUY when price declining over 20 periods prevents buying into downtrend | main.py run_cycle() | v2.16 |
| D-060 | Trade-level analytics: Rolling Sharpe, TWR, Consecutive SL Count added to dashboard | summarize_performance.py | v2.16 |
| D-061 | position_size_pct default: 3.7% of balance per trade — conservative risk exposure for paper trading; tunable via brain | config.json | v2.5 |
| D-062 | rsi_period tunable via brain: BEAR→21, BULL→maintain, NEUTRAL→unchanged (14 default) | main.py run_cycle(), _generate_and_apply_hypotheses() | v2.17 |
| D-063 | sl_cooldown_seconds tunable via brain: BEAR→480s (1.6x), BULL→150s (0.5x), SIDEWAYS→600s (extended) | main.py run_cycle(), _generate_and_apply_hypotheses() | v2.17 |
| D-064 | trend_filter_lookback tunable via brain: BEAR→40, BULL→10, SIDEWAYS→30 periods | main.py run_cycle(), _generate_and_apply_hypotheses() | v2.17 |
| D-065 | ohlcv_limit tunable via brain: BEULL→38, SIDEWAYS→75, BULL→38 bars | main.py run_cycle(), _generate_and_apply_hypotheses() | v2.17 |
| D-066 | ohlcv_timeframe tunable via brain: BEAR→5m, BULL→maintain, NEUTRAL→unchanged (1m) | main.py run_cycle(), _generate_and_apply_hypotheses() | v2.17 |
| D-068 | Multi-timeframe regime sync: Dedicated 1d OHLCV fetch (30 bars) for 20-day macro trend in self_improve_strategies(); isolated from 1m execution signals | main.py self_improve_strategies(), _tag_regime() | v2.17 |
| D-069 | Pre-commit backtest safety gate: _run_local_backtest() validates hypotheses against historical 500-bar data before live application; gating requires strictly positive backtest improvement | main.py _generate_and_apply_hypotheses(), _run_local_backtest() | v2.17

---
**Last Updated:** 2026-06-02 23:15 | Engineer: J.A.R.V.I.S.

## Git Repository Usage

This project uses a Git repository for version control, backup, and restore. Commit changes regularly; use branches for experimentation; and push to remote for backup. See .gitignore for files excluded from version control.
