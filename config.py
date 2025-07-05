import os

# Your Telegram bot token (keep this secret!)
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Your Flask server base URL (Render domain)
AUTH_SERVER_URL = os.getenv("AUTH_SERVER_URL", "https://playspotify.onrender.com")
