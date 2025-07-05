from flask import Flask, request
import json
import os

app = Flask(__name__)
TOKENS_FILE = "sp_dc_tokens.json"


def load_tokens():
    if not os.path.exists(TOKENS_FILE):
        return {}
    try:
        with open(TOKENS_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}


def save_tokens(tokens):
    with open(TOKENS_FILE, "w") as f:
        json.dump(tokens, f, indent=2)


@app.route("/")
def home():
    return "✅ PlaySpotify Auth Server Running!"


@app.route("/login")
def login():
    telegram_id = request.args.get("telegram_id")
    if not telegram_id:
        return "❌ Missing Telegram ID."

    redirect_url = "https://open.spotify.com"

    return f"""
    <html>
        <head><title>Login with Spotify</title></head>
        <body style='text-align: center; font-family: sans-serif; margin-top: 50px;'>
            <h2>Login to Spotify to proceed</h2>
            <p>After logging in, open browser dev tools → Application → Cookies → Copy your <code>sp_dc</code> token</p>
            <a href="{redirect_url}" target="_blank">
                <button style="padding: 10px 25px; font-size: 16px;">Open Spotify</button>
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

    tokens = load_tokens()
    tokens[telegram_id] = sp_dc
    save_tokens(tokens)

    return f"""
    <html>
        <head><title>Cookie Saved</title></head>
        <body style='text-align: center; font-family: sans-serif; margin-top: 50px;'>
            <h2>✅ Cookie saved successfully for user: {telegram_id}</h2>
            <p>Go back to Telegram and use <code>/mytrack</code> or <code>/friends</code>!</p>
        </body>
    </html>
    """


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
