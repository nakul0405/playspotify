from telegram.ext import Updater, CommandHandler
from telegram import ParseMode
import requests
from config import *
from store import get_token, get_cookie

updater = Updater(BOT_TOKEN, use_context=True)
dp = updater.dispatcher

def start(update, context):
    update.message.reply_text("👋 Welcome! Use /login to connect your Spotify account.")

def login(update, context):
    user_id = update.effective_user.id
    login_url = (
        f"https://accounts.spotify.com/authorize?"
        f"client_id={SPOTIFY_CLIENT_ID}&response_type=code"
        f"&redirect_uri={SPOTIFY_REDIRECT_URI}"
        f"&scope=user-read-playback-state+user-read-recently-played"
        f"&state={user_id}&show_dialog=true"
    )
    update.message.reply_text(f"🔗 Click here to login:\n{login_url}")

def mytrack(update, context):
    user_id = update.effective_user.id
    token_data = get_token(user_id)
    if not token_data:
        update.message.reply_text("❌ You are not logged in. Use /login first.")
        return

    access_token = token_data.get("access_token")
    headers = {"Authorization": f"Bearer {access_token}"}
    res = requests.get("https://api.spotify.com/v1/me/player/currently-playing", headers=headers)

    if res.status_code == 204:
        update.message.reply_text("🛑 Nothing is playing.")
    elif res.status_code == 429:
        update.message.reply_text("⚠️ Rate limited. Try again in a few seconds.")
    else:
        data = res.json()
        if not data.get("item"):
            update.message.reply_text("😕 No track found.")
            return

        track = data["item"]
        name = track["name"]
        artist = track["artists"][0]["name"]
        url = track["external_urls"]["spotify"]
        update.message.reply_text(f"🎵 [{name} - {artist}]({url})", parse_mode=ParseMode.MARKDOWN)

def friends(update, context):
    user_id = update.effective_user.id
    sp_dc = get_cookie(user_id)
    if not sp_dc:
        update.message.reply_text("❌ You are not logged in. Use /login and allow cookie access.")
        return

    headers = {"cookie": f"sp_dc={sp_dc}"}
    res = requests.get("https://guc-spclient.spotify.com/presence-view/v1/buddylist", headers=headers)

    if res.status_code != 200:
        update.message.reply_text("❌ Failed to fetch friends activity.")
        return

    friends = res.json().get("friends")
    if not friends:
        update.message.reply_text("👥 No active friends.")
        return

    msg = "👥 *Friends Activity:*\n"
    for f in friends:
        try:
            name = f["user"]['name']
            track = f["track"]['name']
            artist = f["track"]['artist']['name']
            msg += f"\n{name} → {track} - {artist}"
        except:
            continue
    update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)

dp.add_handler(CommandHandler("start", start))
dp.add_handler(CommandHandler("login", login))
dp.add_handler(CommandHandler("mytrack", mytrack))
dp.add_handler(CommandHandler("friends", friends))

updater.start_polling()
updater.idle()
