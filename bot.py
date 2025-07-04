from telegram.ext import Updater, CommandHandler
from config import BOT_TOKEN
import requests
import json
from friends import get_friends_activity
from store import save_sp_dc_token, get_sp_dc_token

TOKENS_FILE = "tokens.json"

# /start command
def start(update, context):
    welcome_text = (
        "🎿 *Welcome to PlaySpotify by Nakul!*\n\n"
        "Track what your friends are listening to — see all the things your Spotify doesn’t have!\n\n"
        "*This bot connects with your Spotify account and shows:*\n"
        "✅ Friends' Live Activity\n"
        "✅ Song details (title, artist, album, time)\n"
        "✅ Your listening activity\n\n"
        "To get started, tap the button below to log in with your Spotify account 👇\n\n"
        "🔐 /login – Connect your Spotify account securely\n\n"
        "_Made with ❤️ by @Nakulrathod0405_"
    )
    update.message.reply_text(welcome_text, parse_mode="Markdown")

# /login command
def login(update, context):
    user_id = str(update.effective_user.id)
    login_url = f"https://playspotify.onrender.com/login?user_id={user_id}"
    text = f"🔗 [Click here to log in with Spotify]({login_url})"
    update.message.reply_text(text, parse_mode="Markdown")

# /setcookie command
def setcookie(update, context):
    try:
        token = context.args[0].strip()
        user_id = str(update.effective_user.id)
        save_sp_dc_token(user_id, token)
        update.message.reply_text("✅ Cookie saved! Now type /friends to see your friends' activity.")
    except IndexError:
        update.message.reply_text("⚠️ Please provide your sp_dc token after the command.\nExample: /setcookie abcdef...1234")

# /friends command
def friends(update, context):
    user_id = str(update.effective_user.id)
    token = get_sp_dc_token(user_id)

    if not token:
        update.message.reply_text("⚠️ Please set your Spotify login cookie using /setcookie command first.")
        return

    try:
        activity = get_friends_activity(token)
        update.message.reply_text(activity, parse_mode="Markdown")
    except Exception as e:
        print(e)
        update.message.reply_text("❌ Failed to fetch friends activity. Make sure your cookie is valid.")

# /logout command
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

# /mytrack command
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

# Run the bot
def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("login", login))
    dp.add_handler(CommandHandler("setcookie", setcookie))
    dp.add_handler(CommandHandler("friends", friends))
    dp.add_handler(CommandHandler("logout", logout))
    dp.add_handler(CommandHandler("mytrack", mytrack))

    print("🤖 Bot is running...")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
