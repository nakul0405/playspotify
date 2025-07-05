import requests

# ------------------ Fetch Raw Buddylist ------------------ #
def get_buddylist(sp_dc: str, sp_key: str = None):
    headers = {
        "cookie": f"sp_dc={sp_dc};"
    }

    if sp_key:
        headers["cookie"] += f" sp_key={sp_key};"

    headers.update({
        "user-agent": "Spotify/1.1.46.916.g416cacf1 Spotify/1.1.46.916.g416cacf1",
        "app-platform": "WebPlayer",
        "accept": "application/json",
    })

    try:
        response = requests.get("https://guc-spclient.spotify.com/presence-view/v1/buddylist", headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"[ERROR] Failed to fetch buddylist: {e}")
        return None


# ------------------ Parse Buddylist ------------------ #
def parse_buddylist(data):
    if not data or "friends" not in data:
        return []

    friends = []

    for friend in data["friends"]:
        try:
            user = friend.get("user", {})
            track = friend.get("track", {}).get("track", {})

            friend_info = {
                "username": user.get("name", "Unknown"),
                "track": track.get("name", "Unknown Track"),
                "artist": track.get("artist", {}).get("name", "Unknown Artist"),
                "timestamp": friend.get("timestamp", None),
                "uri": track.get("uri", None)
            }

            friends.append(friend_info)
        except Exception as e:
            print(f"[WARN] Error parsing friend: {e}")
            continue

    return friends
