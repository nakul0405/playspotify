# friends.py

import requests
import base64
import hmac
import hashlib
import time
import json
from datetime import datetime, timezone
from spotify_utils import spotify_uri_to_url, spotify_user_uri_to_url, time_player

# --- TOTP GENERATOR ---
def generate_totp(secret_base32, time_step=30, digits=6):
    secret = base64.b32decode(secret_base32)
    counter = int(time.time() // time_step)
    counter_bytes = counter.to_bytes(8, 'big')
    hmac_hash = hmac.new(secret, counter_bytes, hashlib.sha1).digest()
    offset = hmac_hash[-1] & 0x0F
    code = ((hmac_hash[offset] & 0x7F) << 24 |
            (hmac_hash[offset + 1] & 0xFF) << 16 |
            (hmac_hash[offset + 2] & 0xFF) << 8 |
            (hmac_hash[offset + 3] & 0xFF))
    return str(code % (10 ** digits)).zfill(digits)

# --- ACCESS TOKEN GENERATOR ---
def generate_access_token(sp_dc):
    # Get Spotify server time
    server_time_resp = requests.get("https://open.spotify.com/server-time")
    server_time = server_time_resp.json().get("serverTime")

    # TOTP Secret (hardcoded, from Swift)
    secret_base32 = "GU2TANZRGQ2TQNJTGQ4DONBZHE2TSMRSGQ4DMMZQGMZDSMZUG4"
    totp = generate_totp(secret_base32)

    params = {
        "reason": "transport",
        "productType": "web-player",
        "totp": totp,
        "totpServer": int(time.time()),
        "totpVer": 5,
        "sTime": server_time,
        "cTime": server_time
    }

    headers = {
        "Cookie": f"sp_dc={sp_dc}",
        "User-Agent": "Mozilla/5.0"
    }

    resp = requests.get("https://open.spotify.com/get_access_token", headers=headers, params=params)
    if resp.status_code != 200:
        raise Exception(f"Access token error: {resp.status_code} - {resp.text}")

    data = resp.json()
    return data["accessToken"]

# --- MAIN FRIEND ACTIVITY FETCHER ---
def fetch_friend_activity(sp_dc):
    access_token = generate_access_token(sp_dc)

    headers = {
        "Authorization": f"Bearer {access_token}",
        "User-Agent": "Mozilla/5.0",
        "App-Platform": "WebPlayer"
    }

    resp = requests.get("https://spclient.wg.spotify.com/presence-view/v1/buddylist", headers=headers)
    if resp.status_code != 200:
        raise Exception(f"Spotify friend API error: {resp.status_code} - {resp.text}")

    data = resp.json()
    friends = parse_friends_json(data)
    return friends

# --- PARSER FOR FRIEND JSON ---
def parse_friends_json(data):
    friends = []
    raw = data.get("friends", [])
    raw.reverse()  # Like in Swift code

    for item in raw:
        try:
            timestamp = item["timestamp"]
            user_data = item["user"]
            track_data = item["track"]
            context_data = track_data.get("context", {})

            user_name = user_data.get("name")
            user_url = spotify_user_uri_to_url(user_data.get("uri"))
            user_image = user_data.get("imageUrl")

            track_name = track_data.get("name")
            track_url = spotify_uri_to_url(track_data.get("uri"))
            artist = track_data.get("artist", {}).get("name", "unknown")
            album = track_data.get("album", {}).get("name", "")
            image_url = track_data.get("imageUrl")
            played_when, now = time_player(timestamp)

            context_name = context_data.get("name", "")
            context_url = spotify_uri_to_url(context_data.get("uri")) if context_data.get("uri") else None

            friends.append({
                "user_name": user_name,
                "user_url": user_url,
                "user_image": user_image,
                "track": {
                    "name": track_name,
                    "url": track_url,
                    "artist": artist,
                    "album": album,
                    "image": image_url,
                    "context": {
                        "name": context_name,
                        "url": context_url
                    }
                },
                "played": played_when,
                "now": now
            })
        except Exception as e:
            print(f"[parse error] {e}")
            continue

    return friends
