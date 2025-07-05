#!/bin/bash

# Exit immediately on error
set -e

# Start Flask Auth Server in background
echo "🚀 Starting Flask Auth Server..."
cd backend
python3 auth_server.py &

# Save backend PID to kill later if needed (optional)
BACKEND_PID=$!

# Wait for Flask server to initialize
sleep 5

# Start Telegram bot
echo "🤖 Starting Telegram Bot..."
cd ../bot
python3 bot.py

# Optional: wait for both processes to end (not required if bot keeps running)
wait $BACKEND_PID
