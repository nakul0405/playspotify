from telegram.ext import Updater, CommandHandler
from config import BOT_TOKEN
import requests, json

TOKENS_FILE = "sp_dc_tokens.json"  # Path to sp_dc token file

def start(update, context):
    welcome_text = (
        "🎧 *Welcome to PlaySpotify by Nakul!*\n\n"
        "Track what your friends are listening to — even what Spotify won’t show you!\n\n"
        "✅ Friends' Live Activity\n"
        "✅ Song Details (Title, Artist, Album, Time)\n"        
        "✅ Your Listening Activity\n\n"
        "*To get started, tap below to log in with Spotify 👇*\n"
        "🔐 /login\n\n"
        "_Made with ❤️ & Madness by @Nakulrathod0405_"
    )
    update.message.reply_text(welcome_text, parse_mode="Markdown")

def login(update, context):
    user_id = str(update.effective_user.id)
    login_url = f"https://playspotify.onrender.com/start_login?user_id={user_id}"
    update.message.reply_text(
        f"🔐 [Click here to securely log in with Spotify]({login_url})\n\n"
        "After logging in, return and use /friends or /mytrack.",
        parse_mode="Markdown"
    )

def mytrack(update, context):
    user_id = str(update.effective_user.id)
    try:
        with open(TOKENS_FILE, "r") as f:
            tokens = json.load(f)
        sp_dc = tokens.get(user_id)
        if not sp_dc:
            raise Exception("No token found")
    except:
        update.message.reply_text("⚠️ You are not logged in. Use /login first.")
        return

    headers = {
        "cookie": f"sp_dc={sp_dc}",
        "user-agent": "Mozilla/5.0"
    }

    try:
        r = requests.get("https://spclient.wg.spotify.com/current-track/v1/me", headers=headers)
        if r.status_code != 200:
            raise Exception("Invalid response")

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
        print(e)
        update.message.reply_text("⚠️ Couldn't fetch your track. Try again later.")

def friends(update, context):
    user_id = str(update.effective_user.id)
    try:
        with open(TOKENS_FILE, "r") as f:
            tokens = json.load(f)
        sp_dc = tokens.get(user_id)
        if not sp_dc:
            raise Exception("No token found")
    except:
        update.message.reply_text("⚠️ You are not logged in. Use /login first.")
        return

    headers = {
        "cookie": f"sp_dc={sp_dc}",
        "user-agent": "Mozilla/5.0"
    }

    try:
        r = requests.get("https://guc-spclient.spotify.com/presence-view/v1/buddylist", headers=headers)
        if r.status_code != 200:
            raise Exception("Failed request")

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
                uri = track.get("uri").replace("spotify:track:", "https://open.spotify.com/track/")
                reply += f"• *{username}*: [{song} - {artist}]({uri})\n"

        update.message.reply_text(reply, parse_mode="Markdown")

    except Exception as e:
        print(e)
        update.message.reply_text("⚠️ Error processing friends' activity. Try again later.")

def logout(update, context):
    user_id = str(update.effective_user.id)
    try:
        with open(TOKENS_FILE, "r") as f:
            tokens = json.load(f)

        if user_id in tokens:
            del tokens[user_id]
            with open(TOKENS_FILE, "w") as f:
                json.dump(tokens, f, indent=2)
            update.message.reply_text("✅ You have been logged out successfully.")
        else:
            update.message.reply_text("⚠️ You are not logged in.")
    except:
        update.message.reply_text("⚠️ Error during logout. Try again.")

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("login", login))
    dp.add_handler(CommandHandler("mytrack", mytrack))
    dp.add_handler(CommandHandler("friends", friends))
    dp.add_handler(CommandHandler("logout", logout))

    print("🤖 Bot is running...")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
