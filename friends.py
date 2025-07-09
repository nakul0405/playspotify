import requests
from spotify_utils import get_access_token

def get_friends_activity(sp_dc):
    token = get_access_token(sp_dc)
    if not token:
        return "❌ Token error. Cookie may be invalid or expired."

    headers = {
        "Authorization": f"Bearer {token}",
        "User-Agent": "Mozilla/5.0"
    }

    url = "https://spclient.wg.spotify.com/presence-view/v1/buddylist"
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        return f"❌ Failed to fetch friends: {r.status_code}"

    data = r.json()
    friends = data.get("friends", [])
    if not friends:
        return "🤷 No friends are listening right now."

    msg = ""
    for f in friends:
        user = f["user"]["name"]
        song = f["track"]["name"]
        artist = f["track"]["artist"]["name"]
        msg += f"👤 {user}\n🎧 {song} — {artist}\n\n"

    return msg.strip()
