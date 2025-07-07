import requests
import json
import os
import subprocess
import uuid

activity_cache_file = "activity_cache.json"

# --- FRIEND ACTIVITY ---
def fetch_friend_activity(sp_dc):
    headers = {
        "cookie": f"sp_dc={sp_dc}",
        "User-Agent": "Mozilla/5.0",
        "app-platform": "WebPlayer",
        "accept": "application/json"
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
        # temp folder
        out_dir = "downloads"
        os.makedirs(out_dir, exist_ok=True)

        # create unique filename prefix
        unique = str(uuid.uuid4())[:8]
        output_template = f"{out_dir}/{unique}.mp3"

        # Run spotdl command
        command = [
            "spotdl",
            query,
            "--output", output_template,
            "--format", "mp3",
            "--lyrics", "no",
        ]

        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Check if file got created
        for file in os.listdir(out_dir):
            if file.endswith(".mp3") and unique in file:
                return os.path.join(out_dir, file)

        raise Exception("Download failed or file not found.")

    except Exception as e:
        raise Exception(f"spotdl error: {str(e)}")
