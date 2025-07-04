import json
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from config import BOT_TOKEN, OWNER_ID

TOKENS_FILE = "tokens.json"

# ----------- BOT COMMANDS -----------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Welcome to Playspotify created by @Nakulrathod0405!\nUse /login to connect your Spotify account.")

async def login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    login_url = f"https://playspotify.onrender.com/login?user_id={user_id}"
    await update.message.reply_text(f"🔗 Click here to log in with Spotify:\n{login_url}")

async def logout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)

    try:
        with open(TOKENS_FILE, "r") as f:
            tokens = json.load(f)
    except FileNotFoundError:
        tokens = {}

    if user_id in tokens:
        del tokens[user_id]
        with open(TOKENS_FILE, "w") as f:
            json.dump(tokens, f, indent=4)
        await update.message.reply_text("✅ Successfully logged out from Spotify.")
    else:
        await update.message.reply_text("⚠️ You are not logged in.")

async def onlyforadmin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        await update.message.reply_text("⛔ You are not authorized to use this command.")
        return

    try:
        with open(TOKENS_FILE, "r") as f:
            tokens = json.load(f)
    except FileNotFoundError:
        tokens = {}

    if not tokens:
        await update.message.reply_text("❌ No one has logged in yet.")
        return

    msg = "👑 Admin View: Logged-in Users\n\n"
    for uid, info in tokens.items():
        name = info.get("display_name", "Unknown")
        msg += f"• {name} (ID: {uid})\n"

    await update.message.reply_text(msg)

async def activeusers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)

    try:
        with open(TOKENS_FILE, "r") as f:
            tokens = json.load(f)
    except FileNotFoundError:
        tokens = {}

    if user_id in tokens:
        await update.message.reply_text("✅ You are logged in with Spotify!")
    else:
        await update.message.reply_text("❌ You are not logged in yet.")

async def mytrack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)

    try:
        with open(TOKENS_FILE, "r") as f:
            tokens = json.load(f)
        token = tokens[user_id]["access_token"]
    except:
        await update.message.reply_text("⚠️ You are not logged in. Use /login first.")
        return

    headers = {
        "Authorization": f"Bearer {token}"
    }
    r = requests.get("https://api.spotify.com/v1/me/player/currently-playing", headers=headers)

    if r.status_code == 204:
        await update.message.reply_text("⏸ You are not playing anything right now.")
        return

    data = r.json()
    item = data.get("item")

    if not item:
        await update.message.reply_text("⚠️ Could not fetch current track.")
        return

    name = item["name"]
    artists = ", ".join([artist["name"] for artist in item["artists"]])
    url = item["external_urls"]["spotify"]

    await update.message.reply_text(f"🎶 Now Playing:\n**{name}**\n👤 {artists}\n🔗 {url}", parse_mode="Markdown")

# ----------- RUN BOT -----------

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("login", login))
    app.add_handler(CommandHandler("logout", logout))
    app.add_handler(CommandHandler("onlyforadmin", onlyforadmin))
    app.add_handler(CommandHandler("activeusers", activeusers))
    app.add_handler(CommandHandler("mytrack", mytrack))

    print("🤖 Bot is running...")
    app.run_polling()
