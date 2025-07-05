#!/bin/bash

set -e

echo "🚀 Starting Flask Auth Server..."
python backend/auth_server.py &

sleep 3

echo "🤖 Starting Telegram Bot..."
python bot/bot.py
