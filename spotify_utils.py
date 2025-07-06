import requests
import json

def fetch_friend_activity(sp_dc):
    headers = {
        "Cookie": f"sp_dc={sp_dc}",
        "User-Agent": "Mozilla/5.0"
    }
    url = "https://guc-spclient.spotify.com/presence-view/v1/buddylist"
    try:
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            return res.json().get("friends", [])
    except:
        return []

def detect_changes(user_id, new_data):
    try:
        with open("activity_cache.json", "r") as f:
            cache = json.load(f)
    except:
        cache = {}

    old_data = cache.get(user_id, [])
    changes = []

    for friend in new_data:
        fid = friend.get("user_id")
        track = friend.get("track", {}).get("name")
        artist = friend.get("track", {}).get("artist")

        old_track = next((f for f in old_data if f.get("user_id") == fid), {})
        if old_track.get("track", {}).get("name") != track:
            changes.append({
                "name": friend.get("user_name"),
                "track": track,
                "artist": artist
            })

    cache[user_id] = new_data
    with open("activity_cache.json", "w") as f:
        json.dump(cache, f)

    return changes
