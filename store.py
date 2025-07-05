import json
import os

TOKENS_FILE = "sp_dc_tokens.json"

def save_sp_dc(telegram_id: str, sp_dc: str):
    try:
        if os.path.exists(TOKENS_FILE):
            with open(TOKENS_FILE, "r") as f:
                data = json.load(f)
        else:
            data = {}

        data[telegram_id] = sp_dc

        with open(TOKENS_FILE, "w") as f:
            json.dump(data, f, indent=2)
        print(f"[store] ✅ Cookie saved for {telegram_id}")
    except Exception as e:
        print(f"[store] ❌ Error saving cookie: {e}")

def get_sp_dc(telegram_id: str):
    try:
        with open(TOKENS_FILE, "r") as f:
            data = json.load(f)
        return data.get(telegram_id)
    except Exception as e:
        print(f"[store] ❌ Error reading cookie: {e}")
        return None

def delete_sp_dc(telegram_id: str):
    try:
        with open(TOKENS_FILE, "r") as f:
            data = json.load(f)
        if telegram_id in data:
            del data[telegram_id]
            with open(TOKENS_FILE, "w") as f:
                json.dump(data, f, indent=2)
            print(f"[store] 🚪 Logged out {telegram_id}")
    except Exception as e:
        print(f"[store] ❌ Logout error: {e}")
