import requests
import json
import os
import subprocess
import uuid
from datetime import datetime, timezone

activity_cache_file = "activity_cache.json"

# --- FRIEND ACTIVITY ---
def fetch_friend_activity(sp_dc):
    # Step 1: Get access token using sp_dc
    token_url = "https://open.spotify.com/get_access_token?reason=transport&productType=web_player"
    headers_token = {
        "Cookie": f"sp_dc={sp_dc}",
        "User-Agent": "Mozilla/5.0"
    }

    token_resp = requests.get(token_url, headers=headers_token)
    if token_resp.status_code != 200:
        raise Exception(f"Spotify token fetch error: {token_resp.status_code} - {token_resp.text}")

    token_data = token_resp.json()
    access_token = token_data.get("accessToken")
    if not access_token:
        raise Exception("No access token in response.")

    # Step 2: Use token to fetch friends activity
    headers = {
        "Authorization": f"Bearer {access_token}",
        "User-Agent": "Mozilla/5.0",
        "App-Platform": "WebPlayer",
        "Accept": "application/json"
    }

    resp = requests.get("https://guc-spclient.spotify.com/presence-view/v1/buddylist", headers=headers)
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

# --- DOWNLOAD TRACK USING spotdl ---
def download_spotify_track(query):
    try:
        out_dir = "downloads"
        os.makedirs(out_dir, exist_ok=True)

        unique = str(uuid.uuid4())[:8]
        output_template = f"{out_dir}/{unique}.mp3"

        command = [
            "spotdl",
            query,
            "--output", output_template,
            "--format", "mp3",
            "--lyrics", "no",
        ]

        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        for file in os.listdir(out_dir):
            if file.endswith(".mp3") and unique in file:
                return os.path.join(out_dir, file)

        raise Exception("Download failed or file not found.")

    except Exception as e:
        raise Exception(f"spotdl error: {str(e)}")

# --- URI → open.spotify.com URL ---
def spotify_uri_to_url(uri: str) -> str:
    parts = uri.split(":")
    if len(parts) == 3:
        return f"https://open.spotify.com/{parts[1]}/{parts[2]}"
    raise ValueError(f"Invalid Spotify URI: {uri}")

def spotify_user_uri_to_url(uri: str) -> str:
    parts = uri.split(":")
    if len(parts) >= 3:
        return f"https://open.spotify.com/{parts[1]}/{parts[2]}"
    raise ValueError(f"Invalid Spotify User URI: {uri}")

# --- TIMESTAMP TO TEXT ---
def time_player(initial_timestamp_ms: int) -> tuple[str, bool]:
    now = datetime.now(timezone.utc)
    timestamp = datetime.fromtimestamp(initial_timestamp_ms / 1000, tz=timezone.utc)
    minutes_diff = abs(int((now - timestamp).total_seconds() // 60))

    if minutes_diff > (24 * 60):
        return (f"{minutes_diff // (24 * 60)} d", False)
    elif minutes_diff > 60:
        return (f"{minutes_diff // 60} hr", False)
    elif minutes_diff > 5:
        return (f"{minutes_diff} m", False)
    else:
        return ("now", True)
