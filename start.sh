#!/bin/bash

# Start the auth server in background
python3 auth_server.py &

# Start the Telegram bot
python3 bot.py

chmod +x start.sh

