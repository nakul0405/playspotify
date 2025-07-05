from flask import Flask, redirect, request
import urllib.parse
from store import save_sp_dc

app = Flask(__name__)

@app.route("/")
def index():
    return "✅ PlaySpotify Auth Server is Running!"

@app.route("/login")
def login():
    telegram_id = request.args.get("telegram_id")
    if not telegram_id:
        return "❌ Missing Telegram ID."

    # Spotify login page
    redirect_url = f"https://accounts.spotify.com/en/login?continue=https://open.spotify.com"
    return f"""
    <html>
        <head><title>Login with Spotify</title></head>
        <body style='text-align: center; font-family: sans-serif; margin-top: 50px;'>
            <h2>Login to Spotify to proceed</h2>
            <p>Once logged in, you’ll need to extract your <code>sp_dc</code> cookie manually.</p>
            <a href="{redirect_url}" target="_blank">
                <button style="padding: 10px 25px; font-size: 16px;">Login with Spotify</button>
            </a>
            <br/><br/>
            <form action="/setcookie" method="get">
                <input type="hidden" name="telegram_id" value="{telegram_id}" />
                <input name="sp_dc" placeholder="Paste your sp_dc cookie" style="width: 300px;" />
                <br/><br/>
                <button type="submit">Submit Cookie</button>
            </form>
        </body>
    </html>
    """

@app.route("/setcookie")
def setcookie():
    telegram_id = request.args.get("telegram_id")
    sp_dc = request.args.get("sp_dc")

    if not telegram_id or not sp_dc:
        return "❌ Missing telegram_id or sp_dc."

    save_sp_dc(telegram_id, sp_dc)

    return f"""
    <html>
        <head><title>Cookie Saved</title></head>
        <body style='text-align: center; font-family: sans-serif; margin-top: 50px;'>
            <h2>✅ Cookie saved successfully!</h2>
            <p>You can now go back to Telegram and use <b>/mytrack</b> or <b>/friends</b></p>
        </body>
    </html>
    """

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
