# store.py
import json

STORE_FILE = "sp_dc_tokens.json"

def save_sp_dc_token(user_id, token):
    try:
        with open(STORE_FILE, "r") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}

    data[user_id] = token

    with open(STORE_FILE, "w") as f:
        json.dump(data, f, indent=4)

def get_sp_dc_token(user_id):
    try:
        with open(STORE_FILE, "r") as f:
            data = json.load(f)
        return data.get(user_id)
    except:
        return None
