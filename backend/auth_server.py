from flask import Flask, request, render_template
import subprocess
import json
import os

app = Flask(__name__, template_folder="templates")
TOKEN_FILE = "cookies.json"

@app.route("/login")
def login():
    user_id = request.args.get("user_id")
    if not user_id:
        return "Missing user_id", 400

    # Run playwright script to login user in background
    subprocess.Popen(["python3", "playwright_login.py", user_id])

    return render_template("login.html")

@app.route("/cookies")
def view():
    try:
        with open(TOKEN_FILE) as f:
            return f.read()
    except:
        return "{}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
