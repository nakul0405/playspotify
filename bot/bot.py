from telegram.ext import Updater, CommandHandler, CallbackContext
from telegram import Update
from config import BOT_TOKEN, AUTH_SERVER_URL
import requests, json

print("✅ bot.py loaded successfully")
TOKENS_FILE = "sp_dc_tokens.json"

def start(update: Update, context: CallbackContext):
    welcome_text = (
        "🎧 *Welcome to PlaySpotify by Nakul!*\n\n"
        "Track what your friends are listening to — even what Spotify won’t show you\\!\n\n"
        "✅ Friends' Live Activity  \n"
        "✅ Song Details \Title, Artist, Album, Time\  \n"
        "✅ Your Listening Activity\n\n"
        "To get started, tap below to log in with Spotify 👇\n\n"
        "> Use any one method to login:\\n"
        "1\\. Use `/login` to login via Spotify and automatically set your cookie\\.\\n"
        "2\\. Use `/setcookie <your_sp_dc_token>` if you want to set cookie manually\\. 🌝\n\n"
        "*Commands:*\n"
        "🔐 /login \\- Login via Spotify\n"
        "🔐 /setcookie your\\_sp\\_dc\\_token \\- Set cookie manually\n"
        "🎵 /mytrack \\- Show your current playing track\n"
        "👥 /friends \\- Show friends listening activity\n"
        "🚪 /logout \\- Logout\n\n"
        "_Made with ❤️ & Madness by @Nakulrathod0405_"
    )
    update.message.reply_text(welcome_text, parse_mode="MarkdownV2")

def login(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    login_url = f"{AUTH_SERVER_URL}/login?telegram_id={user_id}"
    update.message.reply_text(f"🔐 Click here to login to Spotify:\n{login_url}")

def setcookie(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    if len(context.args) != 1:
        return update.message.reply_text("❌ Usage: /setcookie your_sp_dc_token")
    sp_dc = context.args[0]
    try:
        tokens = {}
        try:
            with open(TOKENS_FILE, "r") as f:
                tokens = json.load(f)
        except: pass
        tokens[user_id] = sp_dc
        with open(TOKENS_FILE, "w") as f:
            json.dump(tokens, f)
        update.message.reply_text("✅ Cookie saved! Use /mytrack or /friends now.")
    except:
        update.message.reply_text("⚠️ Failed to save cookie.")

def get_sp_dc(user_id):
    try:
        with open(TOKENS_FILE, "r") as f:
            tokens = json.load(f)
            return tokens.get(str(user_id))
    except:
        return None

def mytrack(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    sp_dc = get_sp_dc(user_id)
    if not sp_dc:
        return update.message.reply_text("⚠️ Please /login or /setcookie first.")

    headers = {
        "cookie": f"sp_dc={sp_dc}",
        "user-agent": "Spotify/8.5.0"
    }
    r = requests.get("https://spclient.wg.spotify.com/current-track/v1/me", headers=headers)
    if r.status_code != 200:
        return update.message.reply_text("⚠️ Failed to fetch current track.")

    data = r.json()
    track = data.get("track")
    if not track:
        return update.message.reply_text("⏸ You're not playing anything.")
    
    name = track["name"]
    artist = track["artist_name"]
    url = track["uri"].replace("spotify:track:", "https://open.spotify.com/track/")
    update.message.reply_text(f"🎵 [{name} - {artist}]({url})", parse_mode="Markdown")

def friends(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    sp_dc = get_sp_dc(user_id)
    if not sp_dc:
        return update.message.reply_text("⚠️ Please /login or /setcookie first.")

    headers = {
        "cookie": f"sp_dc={sp_dc}",
        "user-agent": "Spotify/8.5.0"
    }
    r = requests.get("https://guc-spclient.spotify.com/presence-view/v1/buddylist", headers=headers)
    if r.status_code != 200:
        return update.message.reply_text("⚠️ Failed to fetch friends activity.")

    data = r.json()
    friends = data.get("friends", [])
    if not friends:
        return update.message.reply_text("👥 No friends are listening right now.")

    reply = "🎧 *Friends Listening Now:*\n\n"
    for f in friends:
        u = f.get("user")
        t = f.get("track")
        if u and t:
            name = u.get("name", "Unknown")
            track = t.get("name", "Unknown")
            artist = t.get("artist", "Unknown")
            url = t["uri"].replace("spotify:track:", "https://open.spotify.com/track/")
            reply += f"• *{name}*: [{track} - {artist}]({url})\n"

    update.message.reply_text(reply, parse_mode="Markdown")

def logout(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    try:
        with open(TOKENS_FILE, "r") as f:
            tokens = json.load(f)
        if user_id in tokens:
            del tokens[user_id]
            with open(TOKENS_FILE, "w") as f:
                json.dump(tokens, f)
            update.message.reply_text("🚪 Logged out.")
        else:
            update.message.reply_text("⚠️ You weren't logged in.")
    except:
        update.message.reply_text("⚠️ Logout error.")

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("login", login))
    dp.add_handler(CommandHandler("setcookie", setcookie))
    dp.add_handler(CommandHandler("mytrack", mytrack))
    dp.add_handler(CommandHandler("friends", friends))
    dp.add_handler(CommandHandler("logout", logout))
    print("🤖 Bot started and polling...")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
