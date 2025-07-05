from flask import Flask, request
import json
import asyncio
import logging
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

app = Flask(__name__)
TOKENS_FILE = "sp_dc_tokens.json"

# ✅ Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%H:%M:%S'
)

# 🔐 Async function to grab sp_dc
async def get_sp_dc(user_id):
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)  # headless=True for deployment
            context = await browser.new_context()
            page = await context.new_page()

            # 🔗 Open Spotify login
            await page.goto("https://accounts.spotify.com/en/login")
            logging.info("🔐 Please log in to your Spotify account manually...")

            # ⏳ Wait for user to complete login and redirect
            await page.wait_for_url("https://open.spotify.com/*", timeout=120000)

            # 🍪 Grab cookies
            cookies = await context.cookies()
            sp_dc = next((cookie["value"] for cookie in cookies if cookie["name"] == "sp_dc"), None)

            await browser.close()

            if not sp_dc:
                raise Exception("sp_dc cookie not found after login.")

            # 💾 Save sp_dc to JSON file
            try:
                with open(TOKENS_FILE, "r") as f:
                    data = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                data = {}

            data[str(user_id)] = sp_dc

            with open(TOKENS_FILE, "w") as f:
                json.dump(data, f, indent=2)

            logging.info(f"✅ sp_dc saved for user ID: {user_id}")
            return True

    except PlaywrightTimeoutError:
        logging.error("⏰ Login timeout. User did not complete login in time.")
        return False
    except Exception as e:
        logging.error(f"❌ Error during login: {e}")
        return False

# 🌐 Routes
@app.route("/")
def index():
    return "✅ Flask + Playwright server is running!"

@app.route("/start_login")
def start_login():
    user_id = request.args.get("user_id")
    if not user_id:
        return "❌ Missing `user_id` in URL", 400

    try:
        logging.info(f"🔁 Starting login flow for user: {user_id}")
        success = asyncio.run(get_sp_dc(user_id))

        if success:
            return f"""
            <h2>✅ Spotify Login Successful</h2>
            <p>Your <code>sp_dc</code> token has been saved.</p>
            <p>You may now return to Telegram and use <b>/friends</b> command.</p>
            """
        else:
            return "❌ Login failed. Please try again.", 500

    except Exception as e:
        logging.error(f"❌ Server error: {e}")
        return "❌ Internal server error", 500

# 🚀 Start Server
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
