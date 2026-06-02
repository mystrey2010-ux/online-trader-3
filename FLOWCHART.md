# FLOWCHART — Online Trader-3 run_cycle()

```mermaid
flowchart TD
    A[Start run_cycle] --> B{EMERGENCY_STOP?}
    B -->|yes| B1[log warning → return]
    B -->|no| C[sl_cooldown expired?]
    C -->|yes| D[clear cooldown from config]
    C -->|no| E[fetch ticker price]
    E --> F[fetch OHLCV 50×1m]
    F --> G[calculate RSI-14]
    G --> H{price < entry × (1-stop_loss%)?}
    H -->|yes| I[STOP-LOSS: emergency sell<br/>record trade<br/>set sl_cooldown→return]
    H -->|no| J{sl_cooldown active?}
    J -->|yes| J1[log cooldown active → return]
    J -->|no| K{RSI < buy_threshold<br/>AND no position?}
    K -->|yes| L{uptrend over 20 periods?}
    L -->|no| L1[log downtrend skip → return]
    L -->|yes| M[BUY: market order<br/>accumulate position<br/>save open_position<br/>record entry_rsi]
    K -->|no| N{RSI > sell_threshold<br/>AND position open?}
    N -->|yes| O{net PnL after fees > 0?}
    O -->|no| O1[log fee trap hold → return]
    O -->|yes| P[SELL: market order<br/>record trade<br/>clear open_position<br/>self_improve_strategies]
    N -->|no| Q[log waiting for signal]
    M --> R{position open > 24h?}
    P --> R
    Q --> R
    R -->|yes| S[log timeout warning]
    R -->|no| T[End cycle]
```

## Decision Points Explained

| Node | Condition | Source |
|------|-----------|--------|
| EMERGENCY_STOP | `system_status == "EMERGENCY_STOP"` | config.json field set by emergency_stop_trader.py |
| sl_cooldown | `time.time() < self.sl_cooldown_until` | 300s lock after stop-loss (D-049) |
| STOP-LOSS | `current_price < entry_price × (1 - stop_loss_pct)` | Priority #1 risk management (D-045) |
| BUY | `rsi_val < indicator_threshold AND current_position is None` | RSI oversold entry signal |
| uptrend | `prices[-1] > prices[-20]` | T-018 trend filter |
| SELL | `rsi_val > sell_threshold AND current_position == 'long'` | RSI overbought exit signal |
| fee trap | `potential_net_pnl_usd <= 0` | D-031 prevents unprofitable exits |

## Self-Improvement Brain (self_improve_strategies)

```mermaid
flowchart TD
    A[Start self_improve] --> B[Load last 25 trades]
    B --> C[Filter emergency trades<br/>(stop_loss_triggered, note)]
    C --> D{strategic_trades<br/>>= reflection_cadence?}
    D -->|no| D1[log skip → return]
    D -->|yes| E[Calculate fee-aware<br/>avg_return, max_dd, sharpe]
    E --> F[Fetch OHLCV 1h×60<br/>Tag market regime]
    F --> G{performance OK?}
    G -->|yes| G1[log OK → return]
    G -->|no| H[backup current_strategy to previous_strategies]
    H --> I[Generate regime-aware hypotheses<br/>for each param]
    I --> J[Select best (improve dir → max confidence)]
    J --> K[Apply hypothesis<br/>update indicator_threshold/<br/>stop_loss_pct/position_size_pct]
    K --> L[Increment version]
    L --> M[Save config]
```

## Key Implementation Details

- **Exchange**: `KrakenCliPaperExchange` (paper mode) or CCXT (live)  
- **Config persistence**: Written after every order (BUY/SELL/SL) + rollback snapshots  
- **Fee-aware**: All PnL calculations use `kraken_fee_pct × 2` (round-trip)  
- **Dynamic sell threshold**: `entry_rsi + fee_hurdle_rsi + 5`, minimum `threshold + 10` (D-032)  
- **Position accumulation**: Value-weighted average entry price across multiple BUYs  
- **Cooldown**: 300s after stop-loss prevents re-buy into continuing downtrend (T-029/D-049)