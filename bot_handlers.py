from telegram.ext import CommandHandler
import json
import os
from friends import get_friends_activity

COOKIES_FILE = "cookies.json"

def load_cookies():
    if os.path.exists(COOKIES_FILE):
        with open(COOKIES_FILE, "r") as f:
            return json.load(f)
    return {}

def save_cookies(cookies):
    with open(COOKIES_FILE, "w") as f:
        json.dump(cookies, f)

def set_cookie(update, context):
    try:
        sp_dc = context.args[0]
        user_id = str(update.message.from_user.id)
        cookies = load_cookies()
        cookies[user_id] = sp_dc
        save_cookies(cookies)
        update.message.reply_text("✅ Cookie saved! Now use /friends to see who's listening.")
    except Exception as e:
        update.message.reply_text("⚠️ Use like this:\n/setcookie your_sp_dc_cookie")

def show_friends(update, context):
    user_id = str(update.message.from_user.id)
    cookies = load_cookies()

    if user_id not in cookies:
        update.message.reply_text("❗ Please set your cookie first using /setcookie")
        return

    result = get_friends_activity(cookies[user_id])
    update.message.reply_text(result)

def get_handlers():
    return [
        CommandHandler("setcookie", set_cookie),
        CommandHandler("friends", show_friends),
    ]
