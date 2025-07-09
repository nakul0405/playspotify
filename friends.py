from spotify_utils import get_friends_activity

def fetch_friend_activity(sp_dc):
    data = get_friends_activity(sp_dc)
    if not data:
        return None

    friends = []
    for f in data.get("friends", []):
        try:
            name = f["user"]["name"]
            track = f["track"]["name"]
            artist = f["track"]["artist"]["name"]
            friends.append({
                "user_name": name,
                "track": track,
                "artist": artist
            })
        except:
            continue

    return friends
