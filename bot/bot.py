from telegram.ext import Updater, CommandHandler, CallbackContext
from telegram import Update
from config import BOT_TOKEN, AUTH_SERVER_URL
import requests
import json

print("✅ bot.py loaded successfully")
print("BOT_TOKEN:", BOT_TOKEN)
print("AUTH_SERVER_URL:", AUTH_SERVER_URL)

TOKENS_FILE = "sp_dc_tokens.json"

def start(update: Update, context: CallbackContext):
    welcome_text = (
        "🎧 *Welcome to PlaySpotify by Nakul!*\n\n"
        "Track what your friends are listening to — even what Spotify won’t show you!\n\n"
        "Use /login to login via Spotify and automatically set your cookie.\n"
        "Or use /setcookie if you want to set cookie manually.\n\n"
        "*Commands:*\n"
        "🔐 /login - Login via Spotify\n"
        "🔐 /setcookie your_sp_dc_token - Set cookie manually\n"
        "🎵 /mytrack - Show your current playing track\n"
        "👥 /friends - Show friends listening activity\n"
        "🚪 /logout - Logout\n\n"
        "_Made with ❤️ by @Nakulrathod0405_"
    )
    update.message.reply_text(welcome_text, parse_mode="Markdown")
kdownV2")

def login(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    login_url = f"{AUTH_SERVER_URL}/login?telegram_id={user_id}"
    print(f"🔐 Login requested by {user_id} → {login_url}")
    update.message.reply_text(
        f"🔐 Click here to login to Spotify and link your account:\n{login_url}"
    )

def setcookie(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    if len(context.args) != 1:
        update.message.reply_text("❌ Usage: /setcookie your_sp_dc_token")
        return

    sp_dc = context.args[0]

    try:
        try:
            with open(TOKENS_FILE, "r") as f:
                tokens = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            tokens = {}

        tokens[user_id] = sp_dc

        with open(TOKENS_FILE, "w") as f:
            json.dump(tokens, f, indent=2)

        print(f"✅ Cookie saved for user {user_id}")
        update.message.reply_text("✅ Cookie saved successfully! Now you can use /mytrack or /friends.")
    except Exception as e:
        print("❌ Error saving cookie:", e)
        update.message.reply_text("⚠️ Error saving cookie.")

def mytrack(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    sp_dc = get_sp_dc(user_id)
    if not sp_dc:
        update.message.reply_text("⚠️ You are not logged in. Use /login or /setcookie first.")
        return

    headers = {
        "cookie": f"sp_dc={sp_dc}",
        "user-agent": "Mozilla/5.0"
    }

    try:
        r = requests.get("https://spclient.wg.spotify.com/current-track/v1/me", headers=headers)
        print(f"🎵 Fetched /mytrack for user {user_id} | Status: {r.status_code}")

        if r.status_code != 200:
            update.message.reply_text("⚠️ Failed to fetch current track.")
            return

        data = r.json()
        track = data.get("track")
        if not track:
            update.message.reply_text("⏸ You're not playing anything right now.")
            return

        name = track["name"]
        artist = track["artist_name"]
        url = track["uri"].replace("spotify:track:", "https://open.spotify.com/track/")
        update.message.reply_text(f"🎵 [{name} - {artist}]({url})", parse_mode="Markdown")

    except Exception as e:
        print("❌ Error in /mytrack:", e)
        update.message.reply_text("⚠️ Error processing track info.")

def friends(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    sp_dc = get_sp_dc(user_id)
    if not sp_dc:
        update.message.reply_text("⚠️ You are not logged in. Use /login or /setcookie first.")
        return

    headers = {
        "cookie": f"sp_dc={sp_dc}",
        "user-agent": "Mozilla/5.0"
    }

    try:
        r = requests.get("https://guc-spclient.spotify.com/presence-view/v1/buddylist", headers=headers)
        print(f"👥 Fetched /friends for user {user_id} | Status: {r.status_code}")

        if r.status_code != 200:
            update.message.reply_text("⚠️ Failed to fetch friends activity.")
            return

        data = r.json()
        friends = data.get("friends", [])

        if not friends:
            update.message.reply_text("👥 No friends are listening right now.")
            return

        reply = "🎧 *Friends Listening Now:*\n\n"
        for friend in friends:
            user = friend.get("user")
            track = friend.get("track")
            if user and track:
                username = user.get("name") or "Unknown"
                song = track.get("name")
                artist = track.get("artist")
                uri = track["uri"].replace("spotify:track:", "https://open.spotify.com/track/")
                reply += f"• *{username}*: [{song} - {artist}]({uri})\n"

        update.message.reply_text(reply, parse_mode="Markdown")

    except Exception as e:
        print("❌ Error in /friends:", e)
        update.message.reply_text("⚠️ Error processing friends activity.")

def logout(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    try:
        with open(TOKENS_FILE, "r") as f:
            tokens = json.load(f)
        if user_id in tokens:
            del tokens[user_id]
            with open(TOKENS_FILE, "w") as f:
                json.dump(tokens, f, indent=2)
            print(f"🚪 Logged out {user_id}")
            update.message.reply_text("✅ Successfully logged out.")
        else:
            update.message.reply_text("⚠️ You are not logged in.")
    except Exception as e:
        print("❌ Logout error:", e)
        update.message.reply_text("⚠️ Error during logout.")

def get_sp_dc(user_id: str):
    try:
        with open(TOKENS_FILE, "r") as f:
            tokens = json.load(f)
        return tokens.get(user_id)
    except Exception as e:
        print("❌ Error loading tokens:", e)
        return None

def main():
    print("🔁 Starting main() function...")

    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("login", login))
    dp.add_handler(CommandHandler("setcookie", setcookie))
    dp.add_handler(CommandHandler("mytrack", mytrack))
    dp.add_handler(CommandHandler("friends", friends))
    dp.add_handler(CommandHandler("logout", logout))

    print("🤖 Bot is running and polling...")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
