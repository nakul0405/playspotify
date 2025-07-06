import os
import json
import time
import threading
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from spotify_utils import fetch_friend_activity, detect_changes

BOT_TOKEN = os.environ["BOT_TOKEN"]
cookies_file = "cookies.json"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = str(update.effective_user.id)

    if text.startswith("/start setcookie_spdc="):
        cookie = text.split("setcookie_spdc=")[-1]
        try:
            with open(cookies_file, "r") as f:
                cookies = json.load(f)
        except:
            cookies = {}
        cookies[user_id] = cookie
        with open(cookies_file, "w") as f:
            json.dump(cookies, f, indent=2)
        await update.message.reply_text("✅ Login successful! Spotify tracking is now active.")
    else:
        await update.message.reply_text(
            """👋 🎧 Welcome to PlaySpotify by Nakul!

Track what your friends are listening to — even what Spotify won’t show you!

✅ Friends' Live Activity  
✅ Song Details (Title, Artist, Album, Time)  
✅ Your Listening Activity  

To get started, tap below to log in with Spotify 👇

Use any one method to login:

1. Use /login to login via Spotify and automatically set your cookie  
2. Use /setcookie <your sp_dc token> if you want to set cookie manually 🌝

*Commands:*  
🔐 /login – Login via Spotify  
🔐 /setcookie <token> – Set cookie manually  
🎵 /mytrack – Show your current playing track (coming soon)  
👥 /friends – Show friends listening activity  
🚪 /logout – Logout

Made with ❤️ & Madness by @Nakulrathod0405"""
        )

async def login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔐 Open Spotify Login Page", url="https://nakul0405.github.io/playspotify/helper.html")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Tap below to log in and automatically send your Spotify cookie (Copy Link and Paste in chrome/safari in case link doesn't work👇",
        reply_markup=reply_markup
    )

async def friends(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    try:
        with open(cookies_file, "r") as f:
            cookies = json.load(f)
        sp_dc = cookies.get(user_id)
        if not sp_dc:
            await update.message.reply_text("⚠️ Cookie not found. Use /login or /setcookie to connect your Spotify.")
            return
        friends = fetch_friend_activity(sp_dc)
        msg = "🎧 Your friends are listening to:\n\n"
        for f in friends:
            msg += f"• *{f['name']}* → _{f['track']}_ by _{f['artist']}_\n"
        await update.message.reply_text(msg, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

async def setcookie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    args = context.args

    if not args:
        await update.message.reply_text(
            "⚠️ Please send your sp_dc cookie like this:\n/setcookie abc123xyz"
        )
        return

    sp_dc = args[0]
    try:
        with open(cookies_file, "r") as f:
            cookies = json.load(f)
    except:
        cookies = {}
    cookies[user_id] = sp_dc
    with open(cookies_file, "w") as f:
        json.dump(cookies, f, indent=2)

    await update.message.reply_text("✅ Cookie set successfully! Spotify tracking is now active.")

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

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("login", login))
    app.add_handler(CommandHandler("friends", friends))
    app.add_handler(CommandHandler("setcookie", setcookie))

    threading.Thread(target=auto_notify, args=(app.bot,), daemon=True).start()
    app.run_polling()

if __name__ == "__main__":
    main()
