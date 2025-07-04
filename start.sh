#!/bin/bash

echo "🚀 Starting Playspotify bot..."

# Start the Flask auth server in background
python3 auth_server.py &

# Start the Telegram bot
python3 bot.py
