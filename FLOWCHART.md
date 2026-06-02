# How the Trading Bot Works (Simple Flow)

This flowchart shows what happens every minute when the bot runs.

## Main Trading Loop (Every Minute)

```mermaid
flowchart TD
    Start([Start - One Cycle]) --> Stop{Is trading stopped?}
    Stop -->|Yes| StopLog[Log: trading is stopped]
    Stop -->|No| Cooldown{Just had a stop-loss?}
    Cooldown -->|Yes - 5 min wait| WaitLog[Log: waiting 5 minutes<br/>Then stop cycle]
    Cooldown -->|No| Price[Get current BTC price]
    Price --> RSI[Calculate RSI from price history]
    
    RSI --> BuyCheck{Looking for buy?<br/>RSI is LOW now?}
    BuyCheck -->|Yes - RSI low| TrendCheck{Price going UP lately?}
    TrendCheck -->|No - falling| SkipBuy[Log: price falling,<br/>skip buying]
    TrendCheck -->|Yes - rising| Buy[BUY BTC with 3.7% of USD]
    
    BuyCheck -->|No - RSI not low| SellCheck{Looking for sell?<br/>RSI is HIGH now?}
    SellCheck -->|Yes - RSI high| ProfitCheck{Will I make money after fees?}
    ProfitCheck -->|No| Hold[Log: keep holding]
    ProfitCheck -->|Yes| Sell[SELL all BTC]
    
    SellCheck -->|No - RSI not high| Waiting[Log: waiting for right moment]
    
    Buy --> End[Cycle finished]
    Sell --> End
    Waiting --> End
    Hold --> End
    SkipBuy --> End
    WaitLog --> End
    StopLog --> End
```

## What Does "RSI" Mean?

- **RSI = Relative Strength Index** (0 to 100)
- **LOW RSI (< 66)** means price is "oversold" → **BUY signal**
- **HIGH RSI (> 76)** means price is "overbought" → **SELL signal**

The bot uses a **dynamic sell threshold** that changes based on:
- What RSI was when you bought
- The fees you will pay

## Self-Improvement Brain (After Every 3 Successful Trades)

When you complete 3 winning or losing trades, the bot asks itself:

```mermaid
flowchart TD
    BrainStart([Start Brain Check]) --> LoadTrades[Look at last 25 trades]
    LoadTrades --> Filter[Remove stop-loss trades<br/>Keep only normal trades]
    Filter --> Enough{At least 3 normal trades?}
    Enough -->|No| TooFew[Wait for more trades]
    Enough -->|Yes| Calculate[Calculate profit,<br/>drawdown, sharpe]
    Calculate --> Regime[Check: bull/sideways/bear market]
    
    Regime --> Good{Performance good?}
    Good -->|Yes| AllGood[Keep current settings]
    Good -->|No| Change[Change ONE setting:<br/>• Buy threshold<br/>• Stop-loss %<br/>• Position size]
    
    Change --> Save[Save old settings for undo option]
    Save --> Apply[Apply the change]
    Apply --> NewVersion[Update version number]
```

## Key Rules

| Rule | What It Does |
|------|--------------|
| **Stop-loss** | If price drops 1.6% below buy price → sell immediately to limit loss |
| **5-minute cooldown** | After stop-loss, wait before buying again |
| **Trend filter** | Don't buy if price has been falling for 20 minutes |
| **24-hour warning** | Alert if holding a position for more than 1 day |
| **Fee protection** | Don't sell if you'd lose money to trading fees |

## Config Settings (in config.json)

```json
{
  "indicator_threshold": 66.15,   // RSI level to buy at
  "stop_loss_pct": 0.016,         // 1.6% stop-loss
  "position_size_pct": 0.037,     // 3.7% of balance per trade
  "reflection_cadence": 3,        // Think after every 3 trades
  "target_asset": "BTC/USDT"      // Trading pair
}
```