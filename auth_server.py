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
        return "❌ Missing code or user_id in request."

    payload = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": SPOTIFY_REDIRECT_URI,
        "client_id": SPOTIFY_CLIENT_ID,
        "client_secret": SPOTIFY_CLIENT_SECRET,
    }

    res = requests.post("https://accounts.spotify.com/api/token", data=payload)
    token_data = res.json()

    print("Spotify token response:", token_data)  # ✅ Debug print

    if "access_token" in token_data:
        save_token(user_id, token_data)
        return render_template("login.html", user_id=user_id)
    else:
        # Show real error on screen
        return f"❌ Token exchange failed: {token_data}"

@app.route("/set_spdc", methods=["POST"])
def set_spdc():
    json_data = request.get_json()
    user_id = json_data.get("user_id")
    sp_dc = json_data.get("sp_dc")

    if not sp_dc or not user_id:
        return "❌ Missing cookie or user_id", 400

    save_cookie(user_id, sp_dc)

    # ✅ Notify user via Telegram bot
    msg = "✅ *Spotify login successful!*\nNow use /mytrack and /friends."
    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", data={
        "chat_id": user_id,
        "text": msg,
        "parse_mode": "Markdown"
    })

    return "✅ Cookie saved & login complete!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))  # Railway or Render default
    app.run(host="0.0.0.0", port=port)
