import telebot
import os
from flask import Flask, request

from store import get_cookie, save_cookie
from config import BOT_TOKEN

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # e.g., https://your-app.up.railway.app

# ✅ /start
@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(message, "👋 Welcome to PlaySpotify!\nUse /login to connect your Spotify account.")

# ✅ Your existing /login, /setcookie, /mytrack, /friends code goes here
# You can paste your existing handlers below...

# ✅ Webhook receiver
@app.route('/webhook', methods=["POST"])
def webhook():
    json_data = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_data)
    bot.process_new_updates([update])
    return "!", 200

# ✅ Set webhook on startup
@app.route('/setwebhook', methods=["GET"])
def set_webhook():
    result = bot.set_webhook(f"{WEBHOOK_URL}/webhook")
    return f"Webhook set: {result}"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
