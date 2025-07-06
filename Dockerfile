FROM python:3.10-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

ENV BOT_TOKEN=your_default_bot_token  # Optional fallback

CMD ["python", "bot.py"]
