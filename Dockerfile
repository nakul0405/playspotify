Dockerfile for PlaySpotify Telegram Bot

FROM python:3.10-slim

Set working directory

WORKDIR /app

Install system dependencies

RUN apt-get update && 
apt-get install -y --no-install-recommends gcc && 
apt-get clean && 
rm -rf /var/lib/apt/lists/*

Copy all files

COPY . .

Install Python dependencies

RUN pip install --no-cache-dir -r requirements.txt

Run the bot

CMD ["python", "bot.py"]

