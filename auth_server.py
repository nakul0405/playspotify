from flask import Flask, request, render_template
import os
import requests
from store import save_cookie
from config import BOT_TOKEN

app = Flask(__name__)
app.template_folder = "templates"

@app.route("/spotify/callback")
def spotify_callback():
    user_id = request.args.get("state")
    if not user_id:
        return "❌ Missing user_id."
    return render_template("login.html", user_id=user_id)

@app.route("/set_spdc", methods=["POST"])
def set_spdc():
    json_data = request.get_json()
    user_id = json_data.get("user_id")
    sp_dc = json_data.get("sp_dc")

    if not sp_dc or not user_id:
        return "❌ Missing cookie or user_id", 400

    save_cookie(user_id, sp_dc)

    # ✅ Notify user via Telegram
    msg = "✅ *Spotify login successful!*\nYou can now use /mytrack and /friends."
    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", data={
        "chat_id": user_id,
        "text": msg,
        "parse_mode": "Markdown"
    })

    return "✅ Cookie saved & login complete!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
