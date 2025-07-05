from flask import Flask, request, render_template
import json
import asyncio
import logging
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

app = Flask(__name__)
TOKENS_FILE = "sp_dc_tokens.json"

# ✅ Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%H:%M:%S'
)

# 🔐 Grab sp_dc token after login
async def get_sp_dc(user_id):
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-dev-shm-usage"]
            )
            context = await browser.new_context()
            page = await context.new_page()

            await page.goto("https://accounts.spotify.com/en/login")
            logging.info("🔐 Waiting for Spotify login...")

            await page.wait_for_url("https://open.spotify.com/*", timeout=120000)

            cookies = await context.cookies()
            sp_dc = next((c["value"] for c in cookies if c["name"] == "sp_dc"), None)

            await browser.close()

            if not sp_dc:
                raise Exception("sp_dc cookie not found after login.")

            # 💾 Save cookie
            try:
                with open(TOKENS_FILE, "r") as f:
                    data = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                data = {}

            data[str(user_id)] = sp_dc
            with open(TOKENS_FILE, "w") as f:
                json.dump(data, f, indent=2)

            logging.info(f"✅ sp_dc saved for user: {user_id}")
            return True

    except PlaywrightTimeoutError:
        logging.error("⏰ Timeout: Login not completed.")
        return False
    except Exception as e:
        logging.error(f"❌ Error: {e}")
        return False

# 🌐 Routes
@app.route("/")
def index():
    return "✅ Flask + Playwright auth server is running!"

@app.route("/start_login")
def start_login():
    user_id = request.args.get("user_id")
    if not user_id:
        return "❌ Missing `user_id`", 400

    try:
        logging.info(f"🔁 Starting login flow for user: {user_id}")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        success = loop.run_until_complete(get_sp_dc(user_id))

        if success:
            return render_template("login_success.html")
        else:
            return "❌ Login failed. Try again.", 500
    except Exception as e:
        logging.error(f"❌ Server error: {e}")
        return "❌ Internal server error", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
