import requests
import json
import os

# Optional: local file to cache friend activity (for auto_notify)
activity_cache_file = "activity_cache.json"

# --- FRIEND ACTIVITY ---
def fetch_friend_activity(sp_dc):
    headers = {
        "cookie": f"sp_dc={sp_dc}",
        "User-Agent": "Mozilla/5.0",
        "app-platform": "WebPlayer",  # 🟢 Spotify needs this header
        "accept": "application/json"
    }

    resp = requests.get("https://guc-spclient.spotify.com/presence-view/v1/buddylist", headers=headers)

    # ❗ Strict cookie/auth validation
    if resp.status_code != 200:
        raise Exception(f"Spotify API error: {resp.status_code} - {resp.text}")

    data = resp.json()
    friends = []

    for username, f in data.get("buddylist", {}).items():
        try:
            name = f["user"]["name"]
            track = f["track"]["name"]
            artist = f["track"]["artist"]["name"]
            friends.append({
                "name": name,
                "track": track,
                "artist": artist
            })
        except:
            continue

    return friends

# --- DETECT CHANGES ---
def detect_changes(user_id, latest_friends):
    try:
        if os.path.exists(activity_cache_file):
            with open(activity_cache_file, "r") as f:
                cache = json.load(f)
        else:
            cache = {}

        previous = cache.get(user_id, [])
        new_activity = []

        for friend in latest_friends:
            if friend not in previous:
                new_activity.append(friend)

        # Update cache
        cache[user_id] = latest_friends
        with open(activity_cache_file, "w") as f:
            json.dump(cache, f, indent=2)

        return new_activity
    except:
        return []

# --- MY TRACK FETCHER ---
def fetch_user_track(sp_dc):
    headers = {
        "cookie": f"sp_dc={sp_dc}",
        "User-Agent": "Mozilla/5.0"
    }

    try:
        resp = requests.get("https://api.spotify.com/v1/me/player", headers=headers)
        data = resp.json()

        if "item" not in data or not data["item"]:
            return None

        track_name = data["item"]["name"]
        artist_name = data["item"]["artists"][0]["name"]

        return {
            "track": track_name,
            "artist": artist_name
        }
    except:
        return None
