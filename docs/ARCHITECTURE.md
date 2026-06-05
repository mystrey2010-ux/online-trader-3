# ARCHITECTURE — Online Trader-3 v2.19

## System Overview
- Engine: Single-process Python (main.py), 60s cycle, PAPER trading via Kraken CLI
- Dashboard: Read-only summarize_performance.py (reads config.json + Kraken CLI)  
- Config State: trade_history, open_position, hypothesis_ledger, current_strategy, news_sentiment, daily_start_balance_usd/date

## Trading Loop (run_cycle, 60s)
```
0. EMERGENCY_STOP? → return (D-023)
1. DAILY LOSS CHECK: daily_net_pnl_usd < -(start_balance × max_daily_loss_pct) → EMERGENCY_STOP (D-074/D-078)
2. Fetch ticker → OHLCV (50 x 1m) → RSI-14
3. STOP-LOSS: price < entry × (1-stop_loss_pct) → sell → return (D-045)
4. TREND CHECK: skip BUY if price declining over lookback (T-018)
5. BUY: RSI < threshold + no position + uptrend → buy position_size_pct
6. SELL: RSI > dynamic_threshold + net_pnl_usd > 0 → sell all
```

## Key Schemas
**Current Strategy:** indicator_threshold, sell_threshold_base, stop_loss_pct, position_size_pct, rsi_period, sl_cooldown_seconds, trend_filter_lookback, ohlcv_limit, ohlcv_timeframe

**Trade Record:** timestamp, entry, exit, pnl_pct, pnl_usd, gross_pnl_usd, fee_usd, net_pnl_usd, stop_loss_triggered, note

**News Sentiment (N-004):** sentiment(positive/neutral/negative), confidence, count, feeds_queried(4), feeds_succeeded

## Operations
- `manage_trader.sh {start|stop|status|backup|clean}` - Engine lifecycle
- `emergency_stop_trader.py {emergency_only|emergency_sell|off}` - Emergency controls
- STOP/RESTART: Non-destructive to persistent state

## Deferred
| ID | Item | Notes |
|----|------|-------|
| Q-003 | Multi-symbol support | Architecture ready, not implemented |
| Q-004 | Native stop-loss orders | Currently price-check based |

---
**Last Updated:** 2026-06-05 | Full decisions: DECISIONS.md | Issues: KNOWN_ISSUES.md