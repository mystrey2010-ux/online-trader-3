# CHANGELOG — Online Trader-3

## v2.19
- D-077/D-078: Fixed daily loss limit - uses exchange balance, tracked per day
- N-004: Multi-feed news sentiment aggregation (4 RSS feeds)
- Dashboard: Shows strategic trade count (excludes stop-loss trades)
- L-005: emergency_sell exits gracefully without synthetic trade when no position exists

## v2.18
- D-074: Daily loss limit circuit breaker implemented
- D-071: Stop-loss logic extracted to _execute_stop_loss() helper
- N-002: Switched CryptoPanic RSS to CoinTelegraph RSS feed

## v2.17
- B-011/B-012/B-013/T-029/B-024: Critical bug fixes (entry_rsi persistence, cadence, rollback, cooldown, SL variable)
- D-062-D-070: Regime-aware strategy tuning (rsi_period, sl_cooldown, trend_lookback, ohlcv_limit, timeframe)

## v2.15-v2.16
- B-017/B-018/B-019: Brain activation fixes (NameError, ledger keys, same-cycle re-buy)
- D-025: Emergency trades excluded from reflection pool
- D-046: entry_rsi persisted across restarts

---
**Last Updated:** 2026-06-05