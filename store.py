import json
import os

COOKIES_FILE = "cookies.json"

def save_cookie(user_id, sp_dc):
    if os.path.exists(COOKIES_FILE):
        with open(COOKIES_FILE, "r") as f:
            cookies = json.load(f)
    else:
        cookies = {}

    cookies[user_id] = sp_dc

    with open(COOKIES_FILE, "w") as f:
        json.dump(cookies, f)
