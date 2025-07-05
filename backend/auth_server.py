from flask import Flask, request, redirect
import json
import asyncio
import os

from playwright.async_api import async_playwright

app = Flask(__name__)
TOKENS_FILE = "sp_dc_tokens.json"

async def get_sp_dc(user_id):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # set to True if deploying headlessly
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto("https://accounts.spotify.com/en/login")

        # Wait until login is complete (can be improved later)
        print("▶️ Waiting for login to complete...")
        await page.wait_for_url("https://www.spotify.com/*", timeout=120000)

        # Get cookies
        cookies = await context.cookies()
        for cookie in cookies:
            if cookie["name"] == "sp_dc":
                sp_dc = cookie["value"]
                print(f"✅ sp_dc token: {sp_dc}")

                # Save to tokens.json
                try:
                    with open(TOKENS_FILE, "r") as f:
                        data = json.load(f)
                except:
                    data = {}

                data[str(user_id)] = sp_dc
                with open(TOKENS_FILE, "w") as f:
                    json.dump(data, f, indent=2)

                break

        await browser.close()

@app.route("/start_login")
def start_login():
    user_id = request.args.get("user_id")
    if not user_id:
        return "Missing user_id", 400

    asyncio.run(get_sp_dc(user_id))
    return "✅ Logged in successfully! You can now return to the bot."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
