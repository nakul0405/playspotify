import json
import os

TOKEN_FILE = "tokens.json"
COOKIE_FILE = "cookies.json"

def save_token(user_id, data):
    tokens = load_all(TOKEN_FILE)
    tokens[str(user_id)] = data
    save_all(TOKEN_FILE, tokens)

def get_token(user_id):
    return load_all(TOKEN_FILE).get(str(user_id))

def save_cookie(user_id, sp_dc):
    cookies = load_all(COOKIE_FILE)
    cookies[str(user_id)] = sp_dc
    save_all(COOKIE_FILE, cookies)

def get_cookie(user_id):
    return load_all(COOKIE_FILE).get(str(user_id))

def load_all(path):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {}

def save_all(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
