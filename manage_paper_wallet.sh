#!/bin/bash
# Kraken Paper Sub-Account Management Script
# Usage: ./manage_paper_wallet.sh [command] [args...]
# Commands:
#   summary           - Show account status, orders, and history summary
#   balance           - Check current paper account balance
#   reset <amount>    - Reset sub-account to specified balance (e.g., 1000)

KRAKEN_CMD="$HOME/.cargo/bin/kraken"

case "${1:-}" in
  summary)
    echo "Kraken Paper Trading Account Summary"
    echo "======================================"
    echo ""
    
    # 1. Paper Status (Account Info)
    echo "--- ACCOUNT STATUS ---"
    echo "Your paper trading account settings and configuration."
    echo "Shows your API access level, trade limits, and account type."
    echo "This is safe for learning - no real money at risk!"
    echo ""
    $KRAKEN_CMD paper status 2>/dev/null || echo "Account settings unavailable"
    echo ""
    
    # 2. Paper Orders (Active/Filled/Cancelled)
    echo "--- ORDERS ---"
    echo "All your buy and sell orders - both active and completed."
    echo "Active orders: Instructions waiting to execute at market price"
    echo "Filled orders: Completed trades that executed successfully"
    echo "Cancelled orders: Instructions you cancelled before execution"
    echo "Use this to see your trading activity timeline!"
    echo ""
    $KRAKEN_CMD paper orders 2>/dev/null | head -30 || echo "No orders yet or unavailable"
    echo ""
    
    # 3. Paper History (Trade History)
    echo "--- HISTORY ---"
    echo "Your complete trade history from this paper trading session."
    echo "Each entry shows: entry price, exit price, PnL (profit/loss), and timestamp."
    echo "Green profits (+PnL) and red losses (-PnL) help you track performance."
    echo "This is how you learn from real market movements!"
    echo ""
    $KRAKEN_CMD paper history 2>/dev/null | head -30 || echo "No trades yet or unavailable"
    echo ""
    
    # 4. Account Balance (Current Paper Money)
    echo "--- ACCOUNT BALANCE ---"
    echo "Your current available paper money to trade with."
    echo "This is your starting capital minus any trading losses or gains."
    echo "In paper mode, you can't lose real money - practice safely!"
    echo "Monitor this closely to understand how trades affect your portfolio."
    echo ""
    $KRAKEN_CMD paper balance 2>/dev/null || echo "Balance unavailable"
    echo ""
    
    # Helpful Tips for New Traders
    echo "--- LEARNING TIPS ---"
    echo "New traders: Watch how PnL changes after each trade."
    echo "Experienced: Compare current orders vs completed history."
    echo "Regularly use 'summary' to track your learning progress!"
    echo ""
    
    echo "======================================"
    ;;
  balance)
    echo "📊 Current Paper Account Balance:"
    $KRAKEN_CMD paper balance
    ;;
  reset)
    BALANCE=${2:-1000}
    if [ -z "$BALANCE" ] || ! [[ "$BALANCE" =~ ^[0-9]+(\.[0-9]+)?$ ]]; then
      echo "❌ Usage: $0 reset <balance>"
      echo "   Example: $0 reset 1000"
      exit 1
    fi
    echo "🔁 Resetting paper wallet to $BALANCE USD..."
    $KRAKEN_CMD paper reset --balance "$BALANCE"
    ;;
  *)
    echo "❌ Kraken Paper Wallet Manager"
    echo ""
    echo "Usage: $0 [command] [args]"
    echo ""
    echo "Commands:"
    echo "  summary           - Show account status, orders, and history summary"
    echo "  balance           - Check current paper account balance"
    echo "  reset <amount>    - Reset wallet to specified balance (USD)"
    echo ""
    echo "Examples:"
    echo "  $0 summary              # Full summary with status, orders, history"
    echo "  $0 balance              # Check balance only"
    echo "  $0 reset 1000           # Reset to \$1,000"
    exit 1
    ;;
esac
