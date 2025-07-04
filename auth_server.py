from flask import Flask, request, redirect
import requests, json, urllib.parse
from datetime import datetime, timedelta
from config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI

app = Flask(__name__)
TOKENS_FILE = "tokens.json"

def save_token(user_id, data, display_name, spotify_id):
    try:
        with open(TOKENS_FILE, "r") as f:
            tokens = json.load(f)
    except FileNotFoundError:
        tokens = {}

    tokens[user_id] = {
        "access_token": data["access_token"],
        "refresh_token": data["refresh_token"],
        "token_expiry": (datetime.now() + timedelta(seconds=data["expires_in"])).isoformat(),
        "display_name": display_name,
        "spotify_id": spotify_id
    }

    with open(TOKENS_FILE, "w") as f:
        json.dump(tokens, f, indent=4)

@app.route('/')
def home():
    return "✅ Spotify OAuth Server Running"

@app.route('/login')
def spotify_login():
    user_id = request.args.get('user_id')
    scope = "user-read-currently-playing user-read-recently-played user-top-read"

    auth_url = "https://accounts.spotify.com/authorize?" + urllib.parse.urlencode({
        "client_id": SPOTIFY_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": SPOTIFY_REDIRECT_URI,
        "scope": scope,
        "state": user_id
    })

    return redirect(auth_url)

@app.route('/callback')
def callback():
    code = request.args.get("code")
    user_id = request.args.get("state")

    token_data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": SPOTIFY_REDIRECT_URI,
        "client_id": SPOTIFY_CLIENT_ID,
        "client_secret": SPOTIFY_CLIENT_SECRET
    }

    r = requests.post("https://accounts.spotify.com/api/token", data=token_data)
    data = r.json()

    headers = {"Authorization": f"Bearer {data['access_token']}"}
    profile = requests.get("https://api.spotify.com/v1/me", headers=headers).json()

    save_token(user_id, data, profile.get("display_name", "Unknown"), profile["id"])
    return "✅ Spotify login successful! You can return to Telegram."

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)

application = app  # for Render deployment
