import json
import os

COOKIES_FILE = "cookies.json"

def save_sp_dc_token(user_id, token):
    try:
        if os.path.exists(COOKIES_FILE):
            with open(COOKIES_FILE, "r") as f:
                cookies = json.load(f)
        else:
            cookies = {}

        cookies[user_id] = token

        with open(COOKIES_FILE, "w") as f:
            json.dump(cookies, f, indent=4)
    except Exception as e:
        print("Error saving token:", e)

def get_sp_dc_token(user_id):
    try:
        if not os.path.exists(COOKIES_FILE):
            return None

        with open(COOKIES_FILE, "r") as f:
            cookies = json.load(f)

        return cookies.get(user_id)
    except Exception as e:
        print("Error reading token:", e)
        return None
