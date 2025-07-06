from telegram import Update
from telegram.ext import CommandHandler, ContextTypes
import json

def load_cookies():
    try:
        with open("cookies.json", "r") as f:
            return json.load(f)
    except:
        return {}

def save_cookie(user_id, sp_dc):
    cookies = load_cookies()
    cookies[str(user_id)] = sp_dc
    with open("cookies.json", "w") as f:
        json.dump(cookies, f)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text
    if "setcookie_spdc=" in msg:
        sp_dc = msg.split("setcookie_spdc=")[-1]
        save_cookie(update.effective_user.id, sp_dc)
        await update.message.reply_text("✅ Cookie saved! Type /friends to check activity.")
    else:
        await update.message.reply_text("Welcome! Type /login to begin or /setcookie if you already have your Spotify cookie.")

async def login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🧠 Login to Spotify here:\nhttps://accounts.spotify.com/en/login")

async def setcookie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🛠 Paste your sp_dc cookie like this:\n`/start setcookie_spdc=your_cookie_here`", parse_mode="Markdown")

async def friends(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from spotify_utils import fetch_friend_activity
    user_id = str(update.effective_user.id)
    cookies = load_cookies()
    sp_dc = cookies.get(user_id)

    if not sp_dc:
        await update.message.reply_text("❌ No cookie found. Please use /setcookie first.")
        return

    friends = fetch_friend_activity(sp_dc)
    if not friends:
        await update.message.reply_text("😶 Couldn't fetch activity. Is your cookie valid?")
        return

    msg = "🎧 Your Friends’ Activity:\n\n"
    for f in friends:
        track = f.get("track", {}).get("name", "unknown")
        artist = f.get("track", {}).get("artist", "unknown")
        user = f.get("user_name", "unknown")
        msg += f"👤 {user}\n🎵 *{track}* by *{artist}*\n\n"

    await update.message.reply_text(msg, parse_mode="Markdown")

def setup_handlers(app):
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("login", login))
    app.add_handler(CommandHandler("setcookie", setcookie))
    app.add_handler(CommandHandler("friends", friends))
