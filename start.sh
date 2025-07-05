#!/bin/bash

echo "✅ Starting Flask Auth Server on port 8000..."
python3 auth_server.py &

echo "🎧 Starting Telegram Bot..."
python3 bot.py
