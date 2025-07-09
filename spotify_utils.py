import requests
import time
import hmac
import hashlib
import base64

def get_server_time():
    return requests.get("https://open.spotify.com/server-time").json()["serverTime"]

def generate_totp(secret: bytes, interval=30, digits=6):
    counter = int(time.time()) // interval
    counter_bytes = counter.to_bytes(8, byteorder='big')
    hmac_digest = hmac.new(secret, counter_bytes, hashlib.sha1).digest()
    offset = hmac_digest[-1] & 0x0F
    code = (int.from_bytes(hmac_digest[offset:offset+4], 'big') & 0x7FFFFFFF) % (10 ** digits)
    return str(code).zfill(digits)

def get_access_token(sp_dc):
    base32_secret = "GU2TANZRGQ2TQNJTGQ4DONBZHE2TSMRSGQ4DMMZQGMZDSMZUG4"
    secret = base64.b32decode(base32_secret, casefold=True)

    s_time = get_server_time()
    c_time = int(time.time())
    totp = generate_totp(secret)

    url = f"https://open.spotify.com/get_access_token?reason=transport&productType=web-player&totp={totp}&totpServer={c_time}&totpVer=5&sTime={s_time}&cTime={s_time}"
    headers = {
        "Cookie": f"sp_dc={sp_dc}",
        "User-Agent": "Mozilla/5.0"
    }

    r = requests.get(url, headers=headers)
    return r.json()["accessToken"] if r.status_code == 200 else None
