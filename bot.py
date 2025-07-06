import os
import json
import time
import threading
from telegram import Bot, Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from spotify_utils import fetch_friend_activity, detect_changes

BOT_TOKEN = os.environ["BOT_TOKEN"]  # Loaded securely from Railway ENV

cookies_file = "cookies.json"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = str(update.effective_user.id)

    if text.startswith("/start setcookie_spdc="):
        # Extract cookie value from start payload
        cookie = text.split("setcookie_spdc=")[-1]

        # Load existing cookies
        try:
            with open(cookies_file, "r") as f:
                cookies = json.load(f)
        except:
            cookies = {}

        # Save new cookie
        cookies[user_id] = cookie
        with open(cookies_file, "w") as f:
            json.dump(cookies, f, indent=2)

        await update.message.reply_text("✅ Login successful! Spotify tracking is now active.")
    else:
        await update.message.reply_text("👋 Welcome! Use /login to connect your Spotify account.")


async def login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔐 Login to Spotify:\nhttps://nakul0405.github.io/playspotify/helper.html\n\nLogin in your browser, and the cookie will be auto-sent to the bot!"
    )


async def friends(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)

    try:
        with open(cookies_file, "r") as f:
            cookies = json.load(f)
        sp_dc = cookies.get(user_id)
        if not sp_dc:
            await update.message.reply_text("⚠️ Cookie not found. Use /login to set it first.")
            return

        friends = fetch_friend_activity(sp_dc)
        msg = "🎧 Your friends are listening to:\n\n"
        for f in friends:
            msg += f"• *{f['name']}* → _{f['track']}_ by _{f['artist']}_\n"
        await update.message.reply_text(msg, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")


def auto_notify(bot: Bot):
    while True:
        try:
            with open(cookies_file, "r") as f:
                cookies = json.load(f)
        except:
            cookies = {}

        for user_id, sp_dc in cookies.items():
            friends = fetch_friend_activity(sp_dc)
            changes = detect_changes(user_id, friends)

            for c in changes:
                msg = f"🎵 *{c['name']}* is now listening to:\n*{c['track']}* by *{c['artist']}*"
                bot.send_message(chat_id=user_id, text=msg, parse_mode="Markdown")

        time.sleep(60)


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Command Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("login", login))
    app.add_handler(CommandHandler("friends", friends))

    threading.Thread(target=auto_notify, args=(app.bot,), daemon=True).start()
    app.run_polling()


if __name__ == "__main__":
    main()
