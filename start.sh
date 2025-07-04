#!/bin/bash
# Start Telegram bot
python3 bot.py &

# Start Flask server
cd web && python3 app.py
