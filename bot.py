import os
import json
import time
import threading
from telegram import (
    Bot,
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    ChatMemberHandler,
    MessageHandler,
    filters,
)
from spotify_utils import fetch_friend_activity, detect_changes, fetch_user_track

BOT_TOKEN = os.environ["BOT_TOKEN"]
cookies_file = "cookies.json"

# --- START ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Hello! I'm PlaySpotify bot!\nUse /login or /setcookie to begin."
    )

# --- LOGIN ---
async def login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔐 Open Spotify Login Page", url="https://nakul0405.github.io/playspotify/helper.html")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Tap below to log in and automatically send your Spotify cookie 👇",
        reply_markup=reply_markup
    )

# --- SETCOOKIE ---
async def setcookie(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    args = context.args
    if not args:
        await update.message.reply_text("⚠️ Send your sp_dc cookie like this:\n/setcookie abc123xyz")
        return
    sp_dc = args[0]
    try:
        with open(cookies_file, "r") as f:
            cookies = json.load(f)
    except:
        cookies = {}
    cookies[user_id] = sp_dc
    with open(cookies_file, "w") as f:
        json.dump(cookies, f, indent=2)
    await update.message.reply_text("✅ Cookie set successfully!")

# --- FRIENDS ---
async def friends(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    try:
        with open(cookies_file, "r") as f:
            cookies = json.load(f)
        sp_dc = cookies.get(user_id)
        if not sp_dc:
            await update.message.reply_text("⚠️ Cookie not found.")
            return
        friends = fetch_friend_activity(sp_dc)
        msg = "🎧 Your friends are listening to:\n\n"
        for f in friends:
            msg += f"• *{f['name']}* → _{f['track']}_ by _{f['artist']}_\n"
        await update.message.reply_text(msg, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

# --- MYTRACK ---
async def mytrack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    try:
        with open(cookies_file, "r") as f:
            cookies = json.load(f)
        sp_dc = cookies.get(user_id)
        if not sp_dc:
            await update.message.reply_text("⚠️ Cookie not found.")
            return
        current = fetch_user_track(sp_dc)
        if current:
            msg = f"🎵 You’re currently listening to:\n*{current['track']}* by *{current['artist']}*"
        else:
            msg = "😴 You're not listening to anything right now."
        await update.message.reply_text(msg, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

# --- LOGOUT ---
async def logout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    try:
        with open(cookies_file, "r") as f:
            cookies = json.load(f)
    except:
        cookies = {}
    if user_id in cookies:
        del cookies[user_id]
        with open(cookies_file, "w") as f:
            json.dump(cookies, f, indent=2)
        await update.message.reply_text("🚪 Logged out successfully.")
    else:
        await update.message.reply_text("⚠️ You're not logged in.")

# --- /test command: sends message to channel ---
async def test_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await context.bot.send_message(
            chat_id="@nakulbhaikabot",
            text="🚀 Channel test message from /test command successful!"
        )
        await update.message.reply_text("✅ Message sent to channel.")
    except Exception as e:
        await update.message.reply_text(f"❌ Error sending to channel: {e}")

# --- Bot added to group handler ---
async def welcome_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    member_update = update.chat_member
    bot_id = context.bot.id
    print("[DEBUG] ChatMember event triggered")

    if member_update.new_chat_member.user.id == bot_id:
        new_status = member_update.new_chat_member.status
        old_status = member_update.old_chat_member.status
        print(f"[DEBUG] Old: {old_status}, New: {new_status}")
        if old_status in ("left", "kicked") and new_status in ("member", "administrator"):
            chat_id = update.effective_chat.id
            await context.bot.send_message(
                chat_id=chat_id,
                text="👋 Thanks for adding me! Use /start to begin 🎧"
            )

# --- Background Spotify friend activity notifier ---
def auto_notify(bot: Bot):
    while True:
        try:
            with open(cookies_file, "r") as f:
                cookies = json.load(f)
        except:
            cookies = {}
        for user_id, sp_dc in cookies.items():
            friends = fetch_friend_activity(sp_dc)
            changes = detect_changes(user_id, friends)
            for c in changes:
                msg = f"🎵 *{c['name']}* is now listening to:\n*{c['track']}* by *{c['artist']}*"
                try:
                    bot.send_message(chat_id=user_id, text=msg, parse_mode="Markdown")
                except Exception as e:
                    print(f"Send error: {e}")
        time.sleep(60)

# --- MAIN ---
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("login", login))
    app.add_handler(CommandHandler("setcookie", setcookie))
    app.add_handler(CommandHandler("friends", friends))
    app.add_handler(CommandHandler("mytrack", mytrack))
    app.add_handler(CommandHandler("logout", logout))
    app.add_handler(CommandHandler("test", test_channel))
    app.add_handler(ChatMemberHandler(welcome_bot, ChatMemberHandler.CHAT_MEMBER))

    # Optional: fallback echo for debugging
    app.add_handler(MessageHandler(filters.TEXT, lambda u, c: print("[DEBUG] Message received:", u.message.text)))

    threading.Thread(target=auto_notify, args=(app.bot,), daemon=True).start()
    print("[BOT] Running polling...")
    app.run_polling()

if __name__ == "__main__":
    main()
