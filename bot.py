# bot.py

import telebot
import os
import requests
from store import get_cookie, save_cookie
from config import BOT_TOKEN

bot = telebot.TeleBot(BOT_TOKEN)

# ✅ /start
@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(message, "👋 *Welcome to PlaySpotify!*\nUse /login to connect your Spotify account.\n/setcookie your_sp_dc_here to use Friends Activity.", parse_mode="Markdown")

# ✅ /login
@bot.message_handler(commands=["login"])
def login(message):
    user_id = message.chat.id
    client_id = os.getenv("SPOTIFY_CLIENT_ID")
    redirect_uri = os.getenv("SPOTIFY_REDIRECT_URI")

    if not client_id or not redirect_uri:
        bot.reply_to(message, "❌ Missing Spotify Client ID or Redirect URI.")
        return

    auth_url = (
        f"https://accounts.spotify.com/authorize"
        f"?client_id={client_id}"
        f"&response_type=code"
        f"&redirect_uri={redirect_uri}"
        f"&scope=user-read-playback-state%20user-read-recently-played"
        f"&state={user_id}"
        f"&show_dialog=true"
    )

    bot.reply_to(message, f"🔗 [Click here to login with Spotify]({auth_url})", parse_mode="Markdown")

# ✅ /setcookie
@bot.message_handler(commands=["setcookie"])
def setcookie(message):
    args = message.text.split(" ", 1)
    if len(args) != 2:
        bot.reply_to(message, "❌ Usage:\n/setcookie your_sp_dc_cookie_here")
        return

    sp_dc = args[1].strip()
    save_cookie(str(message.chat.id), sp_dc)
    bot.reply_to(message, "✅ Cookie saved! You can now use /mytrack and /friends.")

# ✅ /mytrack
@bot.message_handler(commands=["mytrack"])
def mytrack(message):
    user_id = str(message.chat.id)
    sp_dc = get_cookie(user_id)

    if not sp_dc:
        bot.reply_to(message, "❌ Please login first using /login or /setcookie.")
        return

    try:
        headers = {
            "Cookie": f"sp_dc={sp_dc}",
            "app-platform": "WebPlayer",
            "User-Agent": "Mozilla/5.0"
        }
        session = requests.Session()
        r = session.get("https://guc-spclient.spotify.com/now-playing-view/v1/view", headers=headers)

        if r.status_code == 200:
            data = r.json()
            track = data.get("track", {})
            name = track.get("name", "Unknown")
            artists = ", ".join([a["name"] for a in track.get("artists", [])])
            url = track.get("uri", "").replace("spotify:track:", "https://open.spotify.com/track/")

            bot.reply_to(message, f"🎵 Now playing:\n*{name}* by *{artists}*\n[Open in Spotify]({url})", parse_mode="Markdown")
        elif r.status_code == 204:
            bot.reply_to(message, "🔇 Nothing is playing right now.")
        else:
            bot.reply_to(message, f"⚠️ Could not fetch track. Status code: {r.status_code}")
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {e}")

# ✅ /friends
@bot.message_handler(commands=["friends"])
def friends(message):
    user_id = str(message.chat.id)
    sp_dc = get_cookie(user_id)

    if not sp_dc:
        bot.reply_to(message, "❌ Please login first using /login or /setcookie.")
        return

    try:
        headers = {
            "Cookie": f"sp_dc={sp_dc}",
            "app-platform": "WebPlayer",
            "User-Agent": "Mozilla/5.0"
        }

        r = requests.get("https://spclient.wg.spotify.com/presence-view/v1/buddylist", headers=headers)

        if r.status_code == 200:
            data = r.json()
            friends = data.get("friends", [])
            if not friends:
                bot.reply_to(message, "👥 No friends are listening right now.")
                return

            reply = "🎧 *Friends Listening Activity:*\n"
            for f in friends:
                name = f.get("user", {}).get("name", "Unknown")
                track = f.get("track", {}).get("name", "No Track")
                artists = ", ".join([a['name'] for a in f.get("track", {}).get("artists", [])])
                reply += f"\n👉 *{name}* is listening to *{track}* by *{artists}*"

            bot.reply_to(message, reply, parse_mode="Markdown")
        else:
            bot.reply_to(message, f"❌ Failed to fetch friends activity. Status: {r.status_code}")
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {e}")

# ✅ Start polling
print("🤖 Bot is running...")
bot.infinity_polling()
