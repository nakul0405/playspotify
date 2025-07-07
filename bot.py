import os
import json
import time
import threading
from telegram import (
    Bot,
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputFile
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ChatMemberHandler,
    ContextTypes,
    filters
)
from spotify_utils import (
    fetch_friend_activity,
    detect_changes,
    fetch_user_track,
    download_spotify_track
)

BOT_TOKEN = os.environ["BOT_TOKEN"]
cookies_file = "cookies.json"

# --- START ---
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
            """👋 🎧 Welcome to *PlaySpotify* by Nakul!

Track what your friends are listening to — even what Spotify won’t show you!

✅ Friends' Live Activity  
✅ Song Details (Title, Artist, Album, Time)  
✅ Your Listening Activity  
📥 Song Downloader from Spotify  

Use any one method to login:

1. Use /login to login via Spotify  
2. Use /setcookie <your sp_dc token>  

*Commands:*  
🔐 /login – Login via Spotify  
🔐 /setcookie <token> – Set cookie manually  
🎵 /mytrack – Show your current playing track  
👥 /friends – Show friends listening activity  
📥 /download <song name or link> – Download any song  
🚪 /logout – Logout  
👋 /hello – Bot intro

𝘔𝘢𝘥𝘦 𝘣𝘺 @NakulRathod0405""",
            parse_mode="Markdown"
        )

# --- LOGIN ---
async def login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔐 Open Spotify Login Page", url="https://nakul0405.github.io/playspotify/helper.html")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Tap below to log in and send your Spotify cookie 👇",
        reply_markup=reply_markup
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

        await update.message.reply_text("✅ Cookie saved. Spotify tracking is now active.")
    except Exception as e:
        await update.message.reply_text(f"❌ Cookie validation failed:\n`{str(e)}`", parse_mode="Markdown")

# --- FRIENDS ---
async def friends(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    try:
        with open(cookies_file, "r") as f:
            cookies = json.load(f)
        sp_dc = cookies.get(user_id)
        if not sp_dc:
            await update.message.reply_text("⚠️ Cookie not found. Use /login or /setcookie first.")
            return
        friends = fetch_friend_activity(sp_dc)
        msg = "🎧 Your friends are listening to:\n\n"
        for f in friends:
            msg += f"• *{f['name']}* → _{f['track']}_ by _{f['artist']}_\n"
        await update.message.reply_text(msg, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Error:\n{str(e)}")

# --- MY TRACK ---
async def mytrack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    try:
        with open(cookies_file, "r") as f:
            cookies = json.load(f)
        sp_dc = cookies.get(user_id)
        if not sp_dc:
            await update.message.reply_text("⚠️ Cookie not found. Use /login or /setcookie first.")
            return
        track = fetch_user_track(sp_dc)
        if track:
            msg = f"🎵 You are listening to:\n*{track['track']}* by *{track['artist']}*"
        else:
            msg = "😴 No active track found."
        await update.message.reply_text(msg, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Error:\n{str(e)}")

# --- DOWNLOAD ---
async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ Please provide a Spotify song name or link.\nUsage: /download <song>")
        return

    query = " ".join(context.args)
    msg = await update.message.reply_text("🔍 Searching & Downloading... Please wait ⏳")
    
    try:
        file_path = download_spotify_track(query)
        if not file_path or not os.path.exists(file_path):
            await msg.edit_text("❌ Failed to download song.")
            return

        await update.message.reply_audio(audio=InputFile(file_path), caption="📥 Here's your song!")
        os.remove(file_path)
        await msg.delete()

    except Exception as e:
        await msg.edit_text(f"❌ Error:\n{str(e)}")

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
        await update.message.reply_text("🚪 Logged out successfully.")
    else:
        await update.message.reply_text("⚠️ You’re not logged in yet.")

# --- HELLO ---
async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎧 Try Bot", url="https://t.me/spotifybyNakul_bot"),
         InlineKeyboardButton("👤 Developer", url="https://t.me/NakulRathod0405")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "✅ I’m *PlaySpotify*, the best Spotify activity + downloader bot 🔥",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

# --- GROUP ADD HANDLER ---
async def welcome_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    member = update.chat_member
    if not member.new_chat_member or member.new_chat_member.user.id != context.bot.id:
        return
    chat_id = member.chat.id
    keyboard = [[InlineKeyboardButton("Try Bot", url="https://t.me/spotifybyNakul_bot")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id, "Thanks for adding me! Use /start to begin.", reply_markup=reply_markup)

# --- AUTO NOTIFY ---
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
                for f in changes:
                    msg = f"🎧 *{f['name']}* is listening:\n*{f['track']}* by *{f['artist']}*"
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
    app.add_handler(ChatMemberHandler(welcome_bot, ChatMemberHandler.MY_CHAT_MEMBER))

    threading.Thread(target=auto_notify, args=(app.bot,), daemon=True).start()
    print("✅ Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
