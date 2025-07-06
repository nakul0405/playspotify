from telegram.ext import ApplicationBuilder
from bot_handlers import setup_handlers
from telegram import Bot
from spotify_utils import fetch_friend_activity, detect_changes
import json, time, threading

BOT_TOKEN = "your_bot_token_here"  # Replace with your actual bot token

def start_polling(bot_token):
    bot = Bot(token=bot_token)

    def loop():
        while True:
            try:
                with open("cookies.json", "r") as f:
                    cookies = json.load(f)
            except:
                cookies = {}

            for user_id, sp_dc in cookies.items():
                friends = fetch_friend_activity(sp_dc)
                changes = detect_changes(user_id, friends)

                for c in changes:
                    msg = f"🎧 {c['name']} is now listening to:\n🎵 *{c['track']}* by *{c['artist']}*"
                    bot.send_message(chat_id=user_id, text=msg, parse_mode="Markdown")

            time.sleep(60)

    threading.Thread(target=loop, daemon=True).start()

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    setup_handlers(app)
    start_polling(BOT_TOKEN)
    app.run_polling()
