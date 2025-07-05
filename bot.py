import os
print("🔍 Debug BOT_TOKEN =", os.getenv("BOT_TOKEN"))

from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import requests
from config import BOT_TOKEN, SPOTIFY_CLIENT_ID, SPOTIFY_REDIRECT_URI, ADMIN_ID
from store import get_token, save_cookie, get_cookie, delete_token, load_tokens
from buddylist import get_buddylist, parse_buddylist
from scheduler import start_scheduler

# ------------------ /start ------------------ #
def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "🎶 Welcome to *PlaySpotify*!\n\n"
        "Use /login to connect your Spotify account.\n"
        "Use /setcookie <sp_dc> to see your friends’ activity.",
        parse_mode="Markdown"
    )

# ------------------ /login ------------------ #
def login(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    auth_url = (
        f"https://accounts.spotify.com/authorize"
        f"?client_id={SPOTIFY_CLIENT_ID}"
        f"&response_type=code"
        f"&redirect_uri={SPOTIFY_REDIRECT_URI}"
        f"&scope=user-read-playback-state+user-read-currently-playing"
        f"&state={user_id}"
    )
    update.message.reply_text(f"🔗 Click to connect Spotify:\n{auth_url}")

# ------------------ /logout ------------------ #
def logout(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    delete_token(user_id)
    update.message.reply_text("✅ You’ve been logged out of Spotify.")

# ------------------ /mytrack ------------------ #
def mytrack(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    token_data = get_token(user_id)

    if not token_data:
        update.message.reply_text("⚠️ You’re not logged in. Use /login first.")
        return

    access_token = token_data.get("access_token")

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    r = requests.get("https://api.spotify.com/v1/me/player/currently-playing", headers=headers)

    if r.status_code == 200:
        data = r.json()
        if data.get("is_playing"):
            track = data["item"]["name"]
            artist = data["item"]["artists"][0]["name"]
            update.message.reply_text(f"🎧 Now playing:\n*{track}* by *{artist}*", parse_mode="Markdown")
        else:
            update.message.reply_text("😴 Nothing is playing right now.")
    elif r.status_code == 204:
        update.message.reply_text("😶 Nothing is currently playing.")
    elif r.status_code == 401:
        update.message.reply_text("🔑 Token expired. Use /login again.")
    elif r.status_code == 429:
        retry = int(r.headers.get("Retry-After", 10))
        update.message.reply_text(f"⏳ Too many requests. Try again in {retry} seconds.")
    else:
        update.message.reply_text(f"⚠️ Spotify error: {r.status_code}")

# ------------------ /setcookie <sp_dc> [sp_key optional] ------------------ #
def setcookie(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    args = context.args

    if not args:
        update.message.reply_text("⚠️ Usage: /setcookie <sp_dc> [sp_key]")
        return

    sp_dc = args[0]
    sp_key = args[1] if len(args) > 1 else None

    save_cookie(user_id, sp_dc, sp_key)
    update.message.reply_text("✅ Cookie saved!")

# ------------------ /friends ------------------ #
def friends(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    sp_dc, sp_key = get_cookie(user_id)

    if not sp_dc:
        update.message.reply_text("⚠️ Set your cookie using /setcookie <sp_dc>")
        return

    data = get_buddylist(sp_dc, sp_key)

    if not data:
        update.message.reply_text("❌ Failed to fetch friend data.")
        return

    parsed = parse_buddylist(data)

    if not parsed:
        update.message.reply_text("🫤 No active friends found.")
        return

    msg = "🎧 *Friends' Activity:*\n\n"
    for f in parsed:
        msg += f"👤 *{f['username']}*: {f['track']} – {f['artist']}\n"

    update.message.reply_text(msg, parse_mode="Markdown")

# ------------------ /onlyforadmin ------------------ #
def onlyforadmin(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    if user_id != ADMIN_ID:
        update.message.reply_text("🚫 You're not allowed.")
        return

    tokens = load_tokens()
    if not tokens:
        update.message.reply_text("📭 No users have logged in yet.")
        return

    msg = "🧑‍💻 *Logged-in users:*\n"
    for uid in tokens:
        msg += f"- `{uid}`\n"

    update.message.reply_text(msg, parse_mode="Markdown")

# ------------------ Main ------------------ #
def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("login", login))
    dp.add_handler(CommandHandler("logout", logout))
    dp.add_handler(CommandHandler("mytrack", mytrack))
    dp.add_handler(CommandHandler("setcookie", setcookie))
    dp.add_handler(CommandHandler("friends", friends))
    dp.add_handler(CommandHandler("onlyforadmin", onlyforadmin))

    start_scheduler()  # Start background friend polling

    print("✅ Bot is running...")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
