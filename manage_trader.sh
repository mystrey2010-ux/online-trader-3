#!/bin/bash

# Configuration
TRADER_DIR="$HOME/online-trader-3"
PYTHON_ENV="/mnt/data/venvs/online-trader-3"
LOG_FILE="$TRADER_DIR/trader.log"
PID_FILE="$TRADER_DIR/trader.pid"

# Ensure we are in the right directory
cd "$TRADER_DIR" || exit 1

case "$1" in
    start)
        if [ -f "$PID_FILE" ]; then
            STORED_PID=$(cat "$PID_FILE")
            if ps -p "$STORED_PID" > /dev/null 2>&1; then
                echo "❌ Trader is already running (PID: $STORED_PID)"
                echo "💡 Use './manage_trader.sh stop' to stop it first, or use 'restart'"
                exit 1
            else
                echo "⚠️ Found stale PID file: $STORED_PID (cleaning up)"
                rm -f "$PID_FILE"
            fi
        fi

        echo "🚀 Starting Online Trader-3 in the background..."

        nohup "$PYTHON_ENV/bin/python" main.py >> "$LOG_FILE" 2>&1 &

        NEW_PID=$!
        echo $NEW_PID > "$PID_FILE"

        echo "✅ Trader started with PID: $NEW_PID"
        echo "📝 Logs being written to: $LOG_FILE"
        ;;
    
    stop)
        # Check if trader is running via PID file
        if [ -f "$PID_FILE" ]; then
            STORED_PID=$(cat "$PID_FILE")
            if ps -p "$STORED_PID" > /dev/null 2>&1; then
                echo ""
                echo "🛑 Stopping process (PID: $STORED_PID)..."
                kill -9 "$STORED_PID" 2>/dev/null
                sleep 1
                rm -f "$PID_FILE"
                echo "✅ Trader stopped permanently."
            else
                echo "🔴 Trader is already stopped."
                rm -f "$PID_FILE"
            fi
        else
            echo "🔴 Trader is already stopped or never started."
        fi
        ;;

restart)
        if [ -f "$PID_FILE" ]; then
            STORED_PID=$(cat "$PID_FILE")
            if ps -p "$STORED_PID" > /dev/null 2>&1; then
                echo ""
                echo "🛑 Stopping process (PID: $STORED_PID)..."
                kill -9 "$STORED_PID" 2>/dev/null
                sleep 1
            fi
            rm -f "$PID_FILE"
        fi

        echo "🔄 Starting trader fresh..."
        
        nohup "$PYTHON_ENV/bin/python" main.py >> "$LOG_FILE" 2>&1 &
        
        NEW_PID=$!
        echo $NEW_PID > "$PID_FILE"
        
        echo "✅ Trader started with PID: $NEW_PID"
        echo "📝 Logs being written to: $LOG_FILE"
        ;;

    status)
        if [ -f "$PID_FILE" ]; then
            STORED_PID=$(cat "$PID_FILE")
            if ps -p "$STORED_PID" > /dev/null 2>&1; then
                echo ""
                echo "🟢 Online Trader-3 (Version 2.16 ⚙️) is RUNNING:"

                echo ""
                ps_output=$(ps -p "$STORED_PID" -o %cpu,%mem,rss,state --no-headers 2>/dev/null)

                cpu=$(echo "$ps_output" | awk '{gsub(/ /, "", $1); print $1}')
                mem=$(echo "$ps_output" | awk '{gsub(/ /, "", $2); print $2}')
                rss_raw=$(echo "$ps_output" | awk '{print $3}' | tr -d ' ')
                state=$(echo "$ps_output" | awk '{gsub(/ /, "", $4); print $4}')

                RSS_MB=$(awk "BEGIN {printf \"%.2f\", $rss_raw/1024}")

                printf "  • PID: %s | CPU: %5.1f%% | MEM: %5.1f%% | RSS: %8.2f MB | State: %s\n" \
                    "$STORED_PID" "$cpu" "$mem" "$RSS_MB" "$state"

                echo ""

                LOG_SIZE=$(du -h "$LOG_FILE" | cut -f1)
                echo "  • Log File Size: $LOG_SIZE"

                echo ""
                echo "------------------------------------------"
                echo "  • Current PID File: $STORED_PID (from trader.pid)"
            else
                echo "🔴 Trader is NOT running."
                echo ""
                echo "------------------------------------------"
                echo "  ⚠️ PID file exists but process is dead: $STORED_PID"
                echo "     (Run './manage_trader.sh start' to restart)"
            fi
        else
            echo "🔴 Trader is NOT running."
        fi
        ;;

    backup)
        BACKUP_DIR="$TRADER_DIR/backups"
        mkdir -p "$BACKUP_DIR"
        TIMESTAMP=$(date +"%d%m%y-%H%M%S")
        BACKUP_PATH="$BACKUP_DIR/config.$TIMESTAMP.json"
        cp "$TRADER_DIR/config.json" "$BACKUP_PATH"
        echo "✅ Config backed up to $BACKUP_PATH"
        ;;

    clean)
        # Check if trader is running via PID file
        if [ -f "$PID_FILE" ]; then
            STORED_PID=$(cat "$PID_FILE")
            if ps -p "$STORED_PID" > /dev/null 2>&1; then
                echo ""
                echo "╔══════════════════════════════════════════════════════════════╗"
                echo "║  ❌ CLEAN CANNOT RUN: Trader is currently ACTIVE              ║"
                echo "╚══════════════════════════════════════════════════════════════╝"
                echo ""
                echo "🛑 The trader process is running:"
                echo "   • PID $STORED_PID"
                echo ""
                echo "💡 Use './manage_trader.sh stop' to stop the trader first,"
                echo "    then run './manage_trader.sh clean' when it's stopped."
                exit 1
            fi
        fi
        
        echo ""
        echo "╔══════════════════════════════════════════════════════════════╗"
        echo "║  🧹 Comprehensive Cleanup: Direct Exchange Balance Pattern    ║"
        echo "╚══════════════════════════════════════════════════════════════╝"
        echo ""
        echo "🧹 COMPREHENSIVE CLEANUP: trader history, logs, AND Kraken reset..."
        echo ""

        # Reset config: trade_history, hypothesis_ledger, open_position (direct exchange balance pattern)
        if [ -f "$TRADER_DIR/config.json" ]; then
            "$PYTHON_ENV/bin/python" -c "import json; p='$TRADER_DIR/config.json'; d=json.load(open(p)); d['trade_history']=[]; d['hypothesis_ledger']=[]; d.pop('open_position', None); json.dump(d, open(p, 'w'), indent=2)" && \
            echo "✅ Config reset: trade_history, hypothesis_ledger, open_position cleared." || \
            (echo "❌ Failed to reset config.json" && "$PYTHON_ENV/bin/python" -c "import json; p='$TRADER_DIR/config.json'; d=json.load(open(p)); d['trade_history']=[]; d['hypothesis_ledger']=[]; d.pop('open_position', None); json.dump(d, open(p, 'w'), indent=2)")
        else
            echo "⚠️  config.json not found. Skipping reset."
        fi

        # Truncate the log file
        if [ -f "$LOG_FILE" ]; then
            : > "$LOG_FILE"
            echo "✅ Log file truncated."
        else
            echo "⚠️  trader.log not found. Skipping truncation."
        fi

        echo ""
        echo "╔══════════════════════════════════════════════════════════════╗"
        echo "║  🔄 Resetting Kraken Paper Account to One Hundred dollars    ║"
        echo "╚══════════════════════════════════════════════════════════════╝"
        echo ""

        # Reset Kraken Paper Account to $100
        CARGO_BIN="$HOME/.cargo/bin/kraken"
        KRANE_RESET_FAILED=false

        if [ -x "$CARGO_BIN/kraken" ]; then
            echo "🔄 Checking Kraken CLI at Cargo binary..." && \
            ("$CARGO_BIN/kraken paper reset --balance 100 >/dev/null 2>&1") >/dev/null || true

            if [ $? -eq 0 ]; then
                echo "✅ Kraken Paper Account reset to $100 (Cargo binary)"
            else
                echo "⚠️ Warning: Kraken CLI failed at Cargo binary. Skipping."
                echo "📝 To reset manually, run: $CARGO_BIN/kraken paper reset --balance 100"
                KRANE_RESET_FAILED=true
            fi
        elif which kraken > /dev/null 2>&1; then
            echo "🔄 Checking Kraken CLI in system PATH..." && \
            (kraken paper reset --balance 100 >/dev/null 2>&1) >/dev/null || true

            if [ $? -eq 0 ]; then
                echo "✅ Kraken Paper Account reset to $100 (system PATH)"
            else
                echo "⚠️ Warning: kraken CLI failed in PATH. Skipping."
                KRANE_RESET_FAILED=true
            fi
        else
            echo "⚠️  Warning: kraken CLI not found anywhere!"
            echo "📝 To install, run: curl -sSL https://kraken.io/kraken.sh | bash"
            KRANE_RESET_FAILED=true
        fi

        if [ "$KRANE_RESET_FAILED" = true ]; then
            echo ""
            echo "------------------------------------------"
            echo "  ⚠️ Kraken account reset failed. Manual intervention may be required."
        fi

        echo ""
        echo "╔══════════════════════════════════════════════════════════════╗"
        echo "║  🧾 Verification (Direct Exchange Balance Pattern)            ║"
        echo "╚══════════════════════════════════════════════════════════════╝"
        echo ""

        # Check that config.json no longer has sub_account fields
        if grep -q '"virtual_sub_account"' "$TRADER_DIR/config.json" 2>/dev/null; then
            echo "❌ WARNING: config.json still contains 'virtual_sub_account' field!"
            echo "📝 Run clean again or manually remove the field."
        else
            echo "✅ Verified: config.json uses DIRECT EXCHANGE BALANCE pattern"
            echo "   (no virtual_sub_account_balance, default_virtual_sub_account fields)"
        fi

        # Show config summary
        echo ""
        echo "📊 Configuration Summary:"
        "$PYTHON_ENV/bin/python" -c "
import json
with open('$TRADER_DIR/config.json') as f:
    cfg = json.load(f)
print(f'   • Target Asset:       {cfg.get(\"target_asset\", \"N/A\")}')
print(f'   • RSI Threshold:      {cfg.get(\"current_strategy\", {}).get(\"indicator_threshold\", \"N/A\")}')
print(f'   • Stop-Loss Pct:      {cfg.get(\"current_strategy\", {}).get(\"stop_loss_pct\", \"N/A\")}')
print(f'   • Position Size Pct:   {cfg.get(\"current_strategy\", {}).get(\"position_size_pct\", \"N/A\")}')
print(f'   • Trades Completed:    {len(cfg.get(\"trade_history\", []))} (cleared)')
" 2>/dev/null

        echo ""
        echo "╔══════════════════════════════════════════════════════════════╗"
        echo "║  ✨ Comprehensive cleanup complete!                          ║"
        echo "╚══════════════════════════════════════════════════════════════╝"
        ;;

    *)
        echo "Usage: $0 {start|stop|status|backup|clean}"
        exit 1
        ;;
esac
