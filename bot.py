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
from friends import fetch_friend_activity
from spotify_utils import detect_changes, get_my_track

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
        welcome_text = (
            "<b>🎧 Welcome to PlaySpotify by Nakul!</b>\n\n"
            "Track what your friends are listening to — even what Spotify won’t show you!\n\n"
            "✅ Friends' Live Activity\n"
            "✅ Song Details (Title, Artist, Album, Time)\n"
            "✅ Your Listening Activity\n"
            "✅ Spotify Song Downloader\n\n"
            "<b>Login Options:</b>\n"
            "1. /login – Auto login via browser\n"
            "2. /setcookie &lt;sp_dc&gt; – Manual cookie\n\n"
            "<b>Commands:</b>\n"
            "🔐 /login – Login via Spotify\n"
            "🔐 /setcookie &lt;token&gt; – Set cookie manually\n"
            "🎵 /mytrack – Show your current playing track\n"
            "👥 /friends – Show friends listening activity\n"
            "🎧 /download &lt;song or link&gt; – Download Spotify song\n"
            "🚪 /logout – Logout\n"
            "👋 /hello – Bot intro\n\n"
            "<i>Made with ❤️ by @NakulRathod0405</i>"
        )
        await update.message.reply_text(welcome_text, parse_mode="HTML")

# --- LOGIN ---
async def login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔐 Open Spotify Login Page", url="https://nakul0405.github.io/playspotify/helper.html")]
    ]
    await update.message.reply_text(
        "Tap below to log in and send your Spotify cookie.\n(If link doesn’t load, open in Chrome/Safari) 👇",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

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
        await update.message.reply_text(f"❌ Cookie validation failed:\n<code>{e}</code>", parse_mode="HTML")

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
            msg += f"• <b>{f['name']}</b> → <i>{f['track']}</i> by <i>{f['artist']}</i>\n"
        await update.message.reply_text(msg, parse_mode="HTML")
    except Exception as e:
        await update.message.reply_text(f"❌ Error:\n<code>{e}</code>", parse_mode="HTML")

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
            msg = f"🎵 You’re listening to:\n<b>{current['track']}</b> by <i>{current['artist']}</i>"
        else:
            msg = "😴 No track found. Maybe you’re not playing anything?"
        await update.message.reply_text(msg, parse_mode="HTML")
    except Exception as e:
        await update.message.reply_text(f"❌ Error:\n<code>{e}</code>", parse_mode="HTML")

# --- DOWNLOAD ---
async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    query = " ".join(context.args)
    if not query:
        await update.message.reply_text("⚠️ Use like this:\n/download believer")
        return
    await update.message.reply_text("🔍 Searching songs...")
    try:
        result = subprocess.run(
            ["spotdl", "search", query, "--save-file", "search.json"],
            capture_output=True, text=True
        )
        with open("search.json", "r") as f:
            data = json.load(f)
        songs = data.get("songs", [])[:5]
        if not songs:
            await update.message.reply_text("❌ No matching songs found.")
            return
        keyboard = []
        search_results[user_id] = songs
        for idx, song in enumerate(songs):
            name = f"{song['name']} - {song['artists'][0]['name']}"
            keyboard.append([InlineKeyboardButton(name, callback_data=f"select_{idx}")])
        await update.message.reply_text(
            "🎵 Select a song to download:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Search failed:\n<code>{e}</code>", parse_mode="HTML")

# --- CALLBACK HANDLER ---
async def handle_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)
    data = query.data
    if not data.startswith("select_") or user_id not in search_results:
        await query.edit_message_text("⚠️ Invalid selection.")
        return
    index = int(data.split("_")[1])
    song = search_results[user_id][index]
    url = song["url"]
    title = f"{song['name']} - {song['artists'][0]['name']}"
    await query.edit_message_text(f"⬇️ Downloading: <b>{title}</b>", parse_mode="HTML")
    try:
        output_dir = f"downloads/{user_id}"
        os.makedirs(output_dir, exist_ok=True)
        command = f'spotdl "{url}" --output "{output_dir}/"'
        subprocess.run(command, shell=True)
        files = os.listdir(output_dir)
        for filename in files:
            path = os.path.join(output_dir, filename)
            with open(path, "rb") as f:
                await context.bot.send_audio(chat_id=user_id, audio=f)
            os.remove(path)
        os.rmdir(output_dir)
    except Exception as e:
        await context.bot.send_message(chat_id=user_id, text=f"❌ Download failed:\n<code>{e}</code>", parse_mode="HTML")

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
        await update.message.reply_text("🚪 Logged out.")
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
        "✅Hey, I’m <b>PlaySpotify</b> — the bot that shows what your friends are secretly vibing to 🎧\n\nTry me or DM creator 👇",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
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
                    msg = f"🎵 <b>{c['name']}</b> is now listening to:\n<b>{c['track']}</b> by <i>{c['artist']}</i>"
                    bot.send_message(chat_id=user_id, text=msg, parse_mode="HTML")
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
    app.add_handler(CallbackQueryHandler(handle_selection))
    threading.Thread(target=auto_notify, args=(app.bot,), daemon=True).start()
    print("🚀 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
