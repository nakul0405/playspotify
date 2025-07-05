from flask import Flask, request
import json
import asyncio
import os
import logging
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

app = Flask(__name__)
TOKENS_FILE = "sp_dc_tokens.json"

# Enable debug logs
logging.basicConfig(level=logging.INFO)

async def get_sp_dc(user_id):
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)  # True for deployment
            context = await browser.new_context()
            page = await context.new_page()

            await page.goto("https://accounts.spotify.com/en/login")

            # Wait for user to login manually
            logging.info("▶️ Waiting for Spotify login...")
            await page.wait_for_url("https://www.spotify.com/*", timeout=120000)

            cookies = await context.cookies()
            sp_dc = None

            for cookie in cookies:
                if cookie["name"] == "sp_dc":
                    sp_dc = cookie["value"]
                    break

            await browser.close()

            if not sp_dc:
                raise Exception("sp_dc cookie not found after login.")

            # Save to JSON
            try:
                with open(TOKENS_FILE, "r") as f:
                    data = json.load(f)
            except:
                data = {}

            data[str(user_id)] = sp_dc
            with open(TOKENS_FILE, "w") as f:
                json.dump(data, f, indent=2)

            logging.info(f"✅ sp_dc token saved for user {user_id}")
            return True

    except PlaywrightTimeoutError:
        logging.error("❌ Login timeout. User did not complete login in time.")
        return False
    except Exception as e:
        logging.error(f"❌ Error during login: {e}")
        return False

@app.route("/")
def index():
    return "✅ Flask backend is running!"

@app.route("/start_login")
def start_login():
    user_id = request.args.get("user_id")
    if not user_id:
        return "❌ Missing user_id", 400

    success = asyncio.run(get_sp_dc(user_id))
    if success:
        return "✅ Login successful! You can now return to the bot."
    else:
        return "❌ Login failed. Please try again or contact support.", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
