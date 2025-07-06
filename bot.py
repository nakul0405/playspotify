import telebot
import os
import requests
from flask import Flask, request
from store import get_cookie, save_cookie
from config import BOT_TOKEN

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

WEBHOOK_URL = os.getenv("WEBHOOK_URL") + "/webhook"  # corrected

@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(message, "👋 Welcome to PlaySpotify!\nUse /login to connect your Spotify account.")

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

@bot.message_handler(commands=["setcookie"])
def setcookie(message):
    args = message.text.split(" ", 1)
    if len(args) != 2:
        bot.reply_to(message, "❌ Usage:\n/setcookie your_sp_dc_cookie_here")
        return

    sp_dc = args[1].strip()
    save_cookie(str(message.chat.id), sp_dc)
    bot.reply_to(message, "✅ Cookie saved! You can now use /mytrack and /friends.")

@bot.message_handler(commands=["mytrack"])
def mytrack(message):
    user_id = str(message.chat.id)
    sp_dc = get_cookie(user_id)

    if not sp_dc:
        bot.reply_to(message, "❌ Please login first using /login.")
        return

    try:
        headers = {
            "Cookie": f"sp_dc={sp_dc}",
            "User-Agent": "Mozilla/5.0"
        }
        res = requests.get("https://api.spotify.com/v1/me/player/currently-playing", headers=headers)
        if res.status_code == 204:
            bot.reply_to(message, "🔇 Nothing is playing right now.")
        elif res.status_code == 200:
            data = res.json()
            name = data['item']['name']
            artists = ", ".join([artist['name'] for artist in data['item']['artists']])
            url = data['item']['external_urls']['spotify']
            bot.reply_to(message, f"🎵 Now playing:\n*{name}* by *{artists}*\n[Open in Spotify]({url})", parse_mode="Markdown")
        else:
            bot.reply_to(message, f"⚠️ Could not fetch track. Status code: {res.status_code}")
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {e}")

@bot.message_handler(commands=["friends"])
def friends(message):
    user_id = str(message.chat.id)
    sp_dc = get_cookie(user_id)

    if not sp_dc:
        bot.reply_to(message, "❌ Please login first using /login.")
        return

    try:
        headers = {
            "Cookie": f"sp_dc={sp_dc}",
            "User-Agent": "Mozilla/5.0"
        }
        res = requests.get("https://guc-spclient.spotify.com/presence-view/v1/buddylist", headers=headers)

        if res.status_code == 200:
            data = res.json()
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
            bot.reply_to(message, f"❌ Failed to fetch friends activity. Status: {res.status_code}")
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {e}")

# ✅ Webhook Receiver
@app.route('/webhook', methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
    bot.process_new_updates([update])
    return "!", 200

# ✅ Set webhook
@app.route("/setwebhook")
def set_webhook():
    response = requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook",
        data={"url": WEBHOOK_URL}
    )
    return f"Webhook set: {response.json()}"

# ✅ Remove webhook (optional)
@app.route("/removewebhook")
def remove_webhook():
    response = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook")
    return f"Webhook removed: {response.json()}"

# ✅ Flask App
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
