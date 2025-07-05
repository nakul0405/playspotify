import json
import os

TOKENS_FILE = "tokens.json"
COOKIES_FILE = "cookies.json"
FRIENDS_FILE = "last_seen_friends.json"


# ------------------ TOKENS ------------------ #
def save_token(user_id, token_data):
    data = {}
    if os.path.exists(TOKENS_FILE):
        with open(TOKENS_FILE, "r") as f:
            data = json.load(f)

    data[str(user_id)] = token_data

    with open(TOKENS_FILE, "w") as f:
        json.dump(data, f, indent=2)


def load_tokens():
    if not os.path.exists(TOKENS_FILE):
        return {}
    with open(TOKENS_FILE, "r") as f:
        return json.load(f)


def get_token(user_id):
    data = load_tokens()
    return data.get(str(user_id))


def delete_token(user_id):
    data = load_tokens()
    if str(user_id) in data:
        del data[str(user_id)]
        with open(TOKENS_FILE, "w") as f:
            json.dump(data, f, indent=2)


# ------------------ COOKIES ------------------ #
def save_cookie(user_id, sp_dc, sp_key=None):
    data = {}
    if os.path.exists(COOKIES_FILE):
        with open(COOKIES_FILE, "r") as f:
            data = json.load(f)

    data[str(user_id)] = {
        "sp_dc": sp_dc,
        "sp_key": sp_key
    }

    with open(COOKIES_FILE, "w") as f:
        json.dump(data, f, indent=2)


def get_cookie(user_id):
    if not os.path.exists(COOKIES_FILE):
        return None, None
    with open(COOKIES_FILE, "r") as f:
        data = json.load(f)
        user_data = data.get(str(user_id))
        if not user_data:
            return None, None
        return user_data.get("sp_dc"), user_data.get("sp_key")


# ------------------ FRIEND SNAPSHOTS ------------------ #
def load_last_seen():
    if not os.path.exists(FRIENDS_FILE):
        return {}
    with open(FRIENDS_FILE, "r") as f:
        return json.load(f)


def save_last_seen(user_id, friends_list):
    data = load_last_seen()
    data[str(user_id)] = friends_list
    with open(FRIENDS_FILE, "w") as f:
        json.dump(data, f, indent=2)
