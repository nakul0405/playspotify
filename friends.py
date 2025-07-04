friends.py

import requests

def get_friends_activity(sp_dc_cookie): headers = { "Cookie": f"sp_dc={sp_dc_cookie}", "User-Agent": "Spotify/8.6.0 (iPhone; iOS 14.4; Scale/2.00)", "App-platform": "iOS", }

response = requests.get(
    "https://guc-spclient.spotify.com/presence-view/v1/buddylist",
    headers=headers,
    timeout=10
)

if response.status_code != 200:
    raise Exception(f"Spotify API returned status {response.status_code}")

data = response.json()
if not data.get("friends"):
    return None

result = "\ud83c\udfb5 *Your Friends' Spotify Activity:*\n\n"
for friend in data["friends"]:
    try:
        user = friend.get("user", {})
        name = user.get("name") or user.get("uri")
        track = friend.get("track")
        if not track:
            continue

        song = track.get("name")
        artist = track.get("artist", {}).get("name")
        uri = track.get("link")

        result += f"*{name}* is listening to \n[{song} - {artist}]({uri})\n\n"
    except:
        continue

return result.strip()

