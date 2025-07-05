#!/bin/bash

# Start Flask Auth Server in background
echo "🚀 Starting Flask Auth Server..."
cd backend
python3 auth_server.py &

# Wait a bit for server to boot
sleep 5

# Start Telegram bot
echo "🤖 Starting Telegram Bot..."
cd ../bot
python3 bot.py
