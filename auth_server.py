from flask import Flask, request, redirect
import requests
import base64
import urllib.parse
from store import save_token
from config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI

app = Flask(__name__)

@app.route("/callback")
def callback():
    code = request.args.get("code")
    state = request.args.get("state")  # Telegram user_id
    error = request.args.get("error")

    if error:
        return "❌ Spotify authorization failed."

    # Encode client ID + secret in base64
    auth_str = f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}"
    b64_auth = base64.b64encode(auth_str.encode()).decode()

    headers = {
        "Authorization": f"Basic {b64_auth}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": SPOTIFY_REDIRECT_URI
    }

    r = requests.post("https://accounts.spotify.com/api/token", headers=headers, data=data)

    if r.status_code != 200:
        return "❌ Failed to get token from Spotify."

    tokens = r.json()
    access_token = tokens.get("access_token")
    refresh_token = tokens.get("refresh_token")

    if not access_token or not refresh_token:
        return "❌ Spotify did not return tokens."

    # Save the token with user_id as key
    save_token(state, {
        "access_token": access_token,
        "refresh_token": refresh_token
    })

    return f"✅ Spotify connected successfully! You can now return to Telegram."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
