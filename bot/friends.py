import requests
import json

def get_friends_activity(sp_dc_token):
    try:
        cookies = {
            "sp_dc": sp_dc_token
        }

        headers = {
            "User-Agent": "Spotify/8.6.72 Android/29 (Xiaomi Redmi Note 10)",
        }

        response = requests.get("https://guc-spclient.spotify.com/presence-view/v1/buddylist", headers=headers, cookies=cookies)

        if response.status_code != 200:
            return "❌ Failed to fetch friends activity (invalid or expired cookie)."

        data = response.json()
        friends = data.get("friends", [])

        if not friends:
            return "😕 No friends are currently active."

        message = "🎧 *Your Friends' Spotify Activity:*\n\n"
        for friend in friends:
            name = friend.get("user", {}).get("name", "Unknown")
            track = friend.get("track", {})
            if not track:
                continue

            song_name = track.get("name")
            artist_name = ", ".join([a.get("name") for a in track.get("artist", [])])
            album_name = track.get("album", {}).get("name")
            track_url = track.get("link")

            message += f"👤 *{name}*\n🎵 [{song_name} - {artist_name}]({track_url})\n💽 {album_name}\n\n"

        return message.strip()

    except Exception as e:
        print(e)
        return "⚠️ Error occurred while fetching friends activity."
