import os
import json
import time
import threading
import subprocess
from telegram import (
    Bot,
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)
from spotify_utils import fetch_friend_activity, detect_changes, fetch_user_track

BOT_TOKEN = os.environ["BOT_TOKEN"]
cookies_file = "cookies.json"
search_results = {}

# --- START ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    text = update.message.text

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
            "👋 🎧 *Welcome to PlaySpotify by Nakul!*\n\n"
            "Track what your friends are listening to — even what Spotify won’t show you!\n\n"
            "✅ Friends' Live Activity\n"
            "✅ Song Details (Title, Artist, Album, Time)\n"
            "✅ Your Listening Activity\n"
            "✅ Spotify Song Downloader\n\n"
            "*Login Options:*\n"
            "1. /login – Auto login via browser\n"
            "2. /setcookie <sp_dc> – Manual cookie\n\n"
            "*Commands:*\n"
            "🔐 /login – Login via Spotify\n"
            "🔐 /setcookie <token> – Set cookie manually\n"
            "🎵 /mytrack – Show your current playing track\n"
            "👥 /friends – Show friends listening activity\n"
            "🎧 /download <song or link> – Download Spotify song\n"
            "🚪 /logout – Logout\n"
            "👋 /hello – Bot intro\n\n"
            " _Made with ❤️ by @NakulRathod0405_ ",
            parse_mode="MarkdownV2"
        )

# --- LOGIN ---
async def login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔐 Open Spotify Login Page", url="https://nakul0405.github.io/playspotify/helper.html")]
    ]
    await update.message.reply_text("Tap below to log in and copy your cookie 👇", reply_markup=InlineKeyboardMarkup(keyboard))

# --- SETCOOKIE ---
async def setcookie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    args = context.args
    if not args:
        await update.message.reply_text("⚠️ Send your sp_dc cookie like this:\n/setcookie abc123xyz")
        return
    sp_dc = args[0]
    try:
        fetch_friend_activity(sp_dc)
        try:
            with open(cookies_file, "r") as f:
                cookies = json.load(f)
        except:
            cookies = {}
        cookies[user_id] = sp_dc
        with open(cookies_file, "w") as f:
            json.dump(cookies, f, indent=2)
        await update.message.reply_text("✅ Cookie saved! Spotify tracking is active.")
    except Exception as e:
        await update.message.reply_text(f"❌ Cookie validation failed:\n`{e}`", parse_mode="Markdown")

# --- FRIENDS ---
async def friends(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    try:
        with open(cookies_file, "r") as f:
            cookies = json.load(f)
        sp_dc = cookies.get(user_id)
        if not sp_dc:
            await update.message.reply_text("⚠️ Cookie missing. Use /login or /setcookie first.")
            return
        friends = fetch_friend_activity(sp_dc)
        msg = "🎧 Your friends are listening to:\n\n"
        for f in friends:
            msg += f"• *{f['name']}* → _{f['track']}_ by _{f['artist']}_\n"
        await update.message.reply_text(msg, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

# --- MYTRACK ---
async def mytrack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    try:
        with open(cookies_file, "r") as f:
            cookies = json.load(f)
        sp_dc = cookies.get(user_id)
        if not sp_dc:
            await update.message.reply_text("⚠️ Cookie missing. Use /login or /setcookie first.")
            return
        current = fetch_user_track(sp_dc)
        if current:
            msg = f"🎵 You’re listening to:\n*{current['track']}* by *{current['artist']}*"
        else:
            msg = "😴 No track found. Maybe you’re not playing anything?"
        await update.message.reply_text(msg, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

# --- DOWNLOAD ---
async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    query = " ".join(context.args)
    if not query:
        await update.message.reply_text("⚠️ Use like this:\n/download believer", parse_mode="Markdown")
        return
    await update.message.reply_text("🔄 Downloading... Please wait ⏳")
    try:
        output_dir = f"downloads/{user_id}"
        os.makedirs(output_dir, exist_ok=True)
        command = f'spotdl "{query}" --output "{output_dir}/"'
        subprocess.run(command, shell=True)
        files = os.listdir(output_dir)
        for filename in files:
            path = os.path.join(output_dir, filename)
            with open(path, "rb") as f:
                await update.message.reply_audio(audio=f)
            os.remove(path)
        os.rmdir(output_dir)
    except Exception as e:
        await update.message.reply_text(f"❌ Download failed:\n`{e}`", parse_mode="Markdown")

# --- LOGOUT ---
async def logout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    try:
        with open(cookies_file, "r") as f:
            cookies = json.load(f)
    except:
        cookies = {}
    if user_id in cookies:
        del cookies[user_id]
        with open(cookies_file, "w") as f:
            json.dump(cookies, f, indent=2)
        await update.message.reply_text("🚪 You’ve been logged out.")
    else:
        await update.message.reply_text("⚠️ You’re not logged in.")

# --- HELLO ---
async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("🎧 Try the Bot", url="https://t.me/spotifybyNakul_bot"),
            InlineKeyboardButton("👤 Developer", url="https://t.me/NakulRathod0405")
        ]
    ]
    await update.message.reply_text(
        "✅Hey, I’m *PlaySpotify* — the bot that shows what your friends are secretly vibing to 🎧",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

# --- AUTO NOTIFY THREAD ---
def auto_notify(bot: Bot):
    while True:
        try:
            with open(cookies_file, "r") as f:
                cookies = json.load(f)
        except:
            cookies = {}
        for user_id, sp_dc in cookies.items():
            try:
                friends = fetch_friend_activity(sp_dc)
                changes = detect_changes(user_id, friends)
                for c in changes:
                    msg = f"🎵 *{c['name']}* is now listening to:\n*{c['track']}* by *{c['artist']}*"
                    bot.send_message(chat_id=user_id, text=msg, parse_mode="Markdown")
            except:
                continue
        time.sleep(60)

# --- MAIN ---
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("login", login))
    app.add_handler(CommandHandler("setcookie", setcookie))
    app.add_handler(CommandHandler("friends", friends))
    app.add_handler(CommandHandler("mytrack", mytrack))
    app.add_handler(CommandHandler("logout", logout))
    app.add_handler(CommandHandler("hello", hello))
    app.add_handler(CommandHandler("download", download))
    threading.Thread(target=auto_notify, args=(app.bot,), daemon=True).start()
    print("🚀 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()

