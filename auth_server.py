from flask import Flask, request, render_template
import requests
import os
from config import *
from store import save_token, save_cookie

app = Flask(__name__)
app.template_folder = "templates"

@app.route("/callback")
def callback():
    code = request.args.get("code")
    user_id = request.args.get("state")

    if not code or not user_id:
        return "Missing data"

    payload = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": SPOTIFY_REDIRECT_URI,
        "client_id": SPOTIFY_CLIENT_ID,
        "client_secret": SPOTIFY_CLIENT_SECRET,
    }

    print("Code:", code)
print("Payload:", payload)
print("Token Response:", token_data)
    res = requests.post("https://accounts.spotify.com/api/token", data=payload)
    data = res.json()
    print("Spotify Token Response:", data)

    if "access_token" in data:
        save_token(user_id, data)
        return render_template("login.html", user_id=user_id)
    else:
        return "Token exchange failed."

@app.route("/set_spdc", methods=["POST"])
def set_spdc():
    json_data = request.get_json()
    user_id = json_data.get("user_id")
    sp_dc = json_data.get("sp_dc")

    if not sp_dc or not user_id:
        return "Missing cookie/user_id", 400

    save_cookie(user_id, sp_dc)

    msg = "✅ *Spotify login successful!*\nNow use /mytrack and /friends."
    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", data={
        "chat_id": user_id,
        "text": msg,
        "parse_mode": "Markdown"
    })

    return "✅ Cookie saved & login complete!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
