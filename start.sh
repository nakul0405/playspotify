#!/bin/bash
echo "🚀 Starting PlaySpotify bot + Flask..."

python3 bot.py &

cd web && python3 app.py
