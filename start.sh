#!/bin/bash
echo "🚀 Starting PlaySpotify bot and Flask server..."

# Start Telegram bot
python3 bot.py &

# Start Flask app
cd web && python3 app.py
