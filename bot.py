from telegram.ext import Updater, CommandHandler
from config import BOT_TOKEN
import requests, json

TOKENS_FILE = "tokens.json"

def start(update, context):
    welcome_text = (
        "🎧 *Welcome to PlaySpotify by Nakul!*\n\n"
        "Track what your friends are listening to — see all the things your Spotify *doesn’t* have!\n\n"
        "This bot connects with your Spotify account and shows:\n"
        "✅ Friends' Live Activity\n"
        "✅ Song details (title, artist, album, time)\n"
        "✅ Your listening activity\n\n"
        "*To get started, tap the button below to log in with your Spotify account 👇*\n\n"
        "🔐 /login – Connect your Spotify account securely\n\n"
        "_Made with ❤️  by @Nakulrathod0405_"
    )
    update.message.reply_text(welcome_text, parse_mode="Markdown")

def login(update, context):
    user_id = str(update.effective_user.id)
    login_url = f"https://playspotify.onrender.com/login?user_id={user_id}"
    text = f"[🔗 Click here to log in with Spotify]({login_url})"
    update.message.reply_text(text, parse_mode="Markdown")

def logout(update, context):
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
        update.message.reply_text("✅ Successfully logged out.")
    else:
        update.message.reply_text("⚠️ You are not logged in.")

def mytrack(update, context):
    user_id = str(update.effective_user.id)
    try:
        with open(TOKENS_FILE, "r") as f:
            tokens = json.load(f)
        token = tokens[user_id]["access_token"]
    except:
        update.message.reply_text("⚠️ You are not logged in.")
        return

    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get("https://api.spotify.com/v1/me/player/currently-playing", headers=headers)

    if r.status_code in [204, 202]:
        update.message.reply_text("⏸ You are not playing anything.")
        return

    try:
        data = r.json()
        track = data.get("item")
        if not track:
            update.message.reply_text("⚠️ Couldn't fetch track.")
            return

        name = track["name"]
        artists = ", ".join([a["name"] for a in track["artists"]])
        url = track["external_urls"]["spotify"]
        update.message.reply_text(f"🎵 [{name} - {artists}]({url})", parse_mode="Markdown")

    except Exception as e:
        update.message.reply_text("⚠️ Error fetching track.")
        print(e)

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("login", login))
    dp.add_handler(CommandHandler("logout", logout))
    dp.add_handler(CommandHandler("mytrack", mytrack))

    print("🤖 Bot is running...")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
