from flask import Flask, request, render_template
import json, os

app = Flask(__name__, template_folder="templates", static_folder="static")
TOKEN_FILE = "../sp_dc_tokens.json"  # stores user_id → sp_dc

@app.route("/autologin")
def autologin():
    return render_template("login.html")

@app.route("/save_spdc", methods=["POST"])
def save_spdc():
    data = request.get_json()
    user_id = str(data.get("user_id"))
    sp_dc = data.get("sp_dc")

    try:
        with open(TOKEN_FILE, "r") as f:
            tokens = json.load(f)
    except:
        tokens = {}

    tokens[user_id] = sp_dc
    with open(TOKEN_FILE, "w") as f:
        json.dump(tokens, f, indent=2)

    return {"status": "ok"}, 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
