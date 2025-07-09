import requests
import time
import hmac
import hashlib
import base64

# Step 1: Get server time from Spotify
def get_server_time():
    r = requests.get("https://open.spotify.com/server-time")
    return r.json()["serverTime"]

# Step 2: Generate TOTP based on Spotify's hardcoded secret
def generate_totp(secret: bytes, interval=30, digits=6, digest=hashlib.sha1):
    counter = int(time.time()) // interval
    counter_bytes = counter.to_bytes(8, byteorder='big')
    hmac_digest = hmac.new(secret, counter_bytes, digest).digest()
    offset = hmac_digest[-1] & 0x0F
    code = (int.from_bytes(hmac_digest[offset:offset+4], byteorder='big') & 0x7FFFFFFF) % (10 ** digits)
    return str(code).zfill(digits)

# Step 3: Get access token from sp_dc
def get_access_token(sp_dc):
    base32_secret = "GU2TANZRGQ2TQNJTGQ4DONBZHE2TSMRSGQ4DMMZQGMZDSMZUG4"
    secret = base64.b32decode(base32_secret, casefold=True)

    server_time = get_server_time()
    totp = generate_totp(secret)
    ts = int(time.time())

    url = f"https://open.spotify.com/get_access_token?reason=transport&productType=web-player&totp={totp}&totpServer={ts}&totpVer=5&sTime={server_time}&cTime={server_time}"
    headers = {
        "Cookie": f"sp_dc={sp_dc}",
        "User-Agent": "Mozilla/5.0"
    }

    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        return res.json()["accessToken"]
    else:
        print("❌ Error getting access token:", res.text)
        return None

# Step 4: Fetch friends' activity
def get_friends_activity(sp_dc):
    token = get_access_token(sp_dc)
    if not token:
        return None

    headers = {
        "Authorization": f"Bearer {token}",
        "User-Agent": "Mozilla/5.0"
    }

    url = "https://spclient.wg.spotify.com/presence-view/v1/buddylist"
    r = requests.get(url, headers=headers)

    if r.status_code == 200:
        return r.json()
    else:
        print("❌ Error getting friends activity:", r.text)
        return None

# Step 5: Get current playing track of the user
def get_my_track(access_token):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "User-Agent": "Mozilla/5.0"
    }

    resp = requests.get("https://api.spotify.com/v1/me/player", headers=headers)
    if resp.status_code != 200:
        return None

    data = resp.json()
    if "item" not in data or not data["item"]:
        return None

    track_name = data["item"]["name"]
    artist_name = data["item"]["artists"][0]["name"]

    return {
        "track": track_name,
        "artist": artist_name
    }
