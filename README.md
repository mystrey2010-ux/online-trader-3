# Online Trader-3

A self-improving cryptocurrency trading bot for BTC/USDT using RSI signals with automatic stop-loss protection and paper trading capabilities.

## Overview

Online Trader-3 is a Python-based trading bot that:
- Trades BTC/USDT on Kraken (paper trading via Kraken CLI or live trading via CCXT)
- Uses RSI-14 for buy/sell signals with dynamic thresholds
- Implements automatic stop-loss protection as Priority #1 risk management
- Self-improves strategy parameters after every 3 trades using a scientific control method
- Tracks trade history, hypothesis ledger, and strategy versions for rollback capability
- Provides a performance dashboard via `summarize_performance.py`

## Features

- 🧠 **Self-Improvement Brain**: Adjusts strategy parameters (RSI threshold, stop-loss, position size) based on performance
- 🛡️ **Stop-Loss Protection**: Automatic exit on -1.6% price drop (configurable)
- 📊 **Paper Trading Mode**: Risk-free testing via Kraken CLI
- 🔁 **Position Accumulation**: Value-weighted average entry price across multiple buys
- 📈 **Performance Tracking**: Detailed trade history with fee-aware PnL calculations
- 🔄 **Strategy Rollback**: Ability to restore previous strategy versions
- 🚨 **Emergency Stop**: External control to halt trading or close positions

## Security Note

⚠️ **Important**: Exchange API keys are stored in `.env` (not in the committed `config.json`) for security. The `.env` file is listed in `.gitignore` to prevent accidental commits.

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/online-trader-3.git
   cd online-trader-3
   ```

2. **Set up the environment**:
   - Install Python 3.8+
   - Install required packages: `pip install pandas numpy ccxt`
   - Install Kraken CLI: `cargo install kraken_cli` (for paper trading)
   - Set up environment variables in `.env`:
     ```env
     EXCHANGE_TYPE=kraken
     EXCHANGE_API_KEY=your_api_key_here
     EXCHANGE_SECRET=your_secret_here
     ```

3. **Configuration**:
   - Review `config.json` for non-exchange settings (trading parameters, targets, etc.)
   - Exchange type and API keys are read from `.env`

## Usage

### Starting the Bot

```bash
# For paper trading (default):
LIVE_TRADING_ENABLED=false python main.py

# For live trading (use with extreme caution):
LIVE_TRADING_ENABLED=true python main.py
```

### Emergency Stop

The bot respects an emergency stop system via `emergency_stop_trader.py`:

```bash
# Set emergency stop flag (engine skips trading logic):
python emergency_stop_trader.py emergency_only

# Set flag AND close open position:
python emergency_stop_trader.py emergency_sell

# Clear emergency stop and resume trading:
python emergency_stop_trader.py off
```

### Performance Dashboard

View real-time statistics:

```bash
python summarize_performance.py
```

### Logs

Trading activity is logged to `trader.log`.

## Configuration

### Environment Variables (`.env`)

| Variable | Description | Default |
|----------|-------------|---------|
| `EXCHANGE_TYPE` | Exchange type (kraken, bybit, etc.) | `kraken` |
| `EXCHANGE_API_KEY` | API key for live trading | (required for live) |
| `EXCHANGE_SECRET` | API secret for live trading | (required for live) |
| `LIVE_TRADING_ENABLED` | Set to `true` for live trading | `false` |

### config.json

Non-exchange configuration parameters:
- `target_asset`: Trading pair (default: `BTC/USDT`)
- `target_daily_return`: Daily return goal for self-improvement (default: 0.002 = 0.2%)
- `max_daily_drawdown`: Maximum allowed drawdown (default: 0.01 = 1%)
- `min_sharpe_ratio`: Minimum Sharpe ratio for strategy acceptance (default: 2.0)
- `reflection_cadence`: Number of trades before self-improvement check (default: 3)
- `kraken_fee_pct`: Maker/taker fee percentage (default: 0.0026 = 0.26%)
- `current_strategy`: Active trading parameters
  - `indicator_threshold`: RSI buy threshold (default: 63.0)
  - `stop_loss_pct`: Stop-loss percentage (default: 0.016 = 1.6%)
  - `position_size_pct`: Percentage of balance to use per trade (default: 0.037 = 3.7%)

## Disclaimer

⚠️ **Trading cryptocurrencies involves significant risk and can result in the loss of your entire investment.** This bot is for educational and paper trading purposes by default. Live trading should only be attempted with funds you can afford to lose, and only after thorough testing in paper mode. The authors are not responsible for any financial losses incurred.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Kraken CLI for paper trading functionality
- CCXT library for cryptocurrency exchange connectivity
- Pandas and NumPy for data analysis

---
**Last Updated**: 2026-06-02