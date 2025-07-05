✅ playwright_login.py — Auto Login & sp_dc Cookie Extractor

from flask import Flask, request, jsonify import asyncio import json import os from playwright.async_api import async_playwright

app = Flask(name) TOKENS_FILE = "../sp_dc_tokens.json"  # Make sure this path is correct

🧠 Util: Save sp_dc token to JSON file

def save_token(user_id, sp_dc): try: with open(TOKENS_FILE, "r") as f: tokens = json.load(f) except: tokens = {}

tokens[user_id] = sp_dc
with open(TOKENS_FILE, "w") as f:
    json.dump(tokens, f, indent=2)

🎯 Login route to trigger headless browser

@app.route("/start_login") def start_login(): user_id = request.args.get("user_id") if not user_id: return "Missing user_id", 400

asyncio.run(run_playwright_login(user_id))
return f"✅ Login complete for user {user_id}. You can go back to Telegram."

🤖 Headless browser function to grab sp_dc

async def run_playwright_login(user_id): async with async_playwright() as p: browser = await p.chromium.launch(headless=False)  # False = show browser context = await browser.new_context() page = await context.new_page() await page.goto("https://accounts.spotify.com/en/login")

print("⏳ Waiting for user to login...")
    # Wait until sp_dc cookie appears
    sp_dc = None
    for _ in range(60):  # wait max ~60s
        cookies = await context.cookies()
        for c in cookies:
            if c['name'] == 'sp_dc':
                sp_dc = c['value']
                break
        if sp_dc:
            break
        await asyncio.sleep(1)

    await browser.close()

    if sp_dc:
        print(f"✅ sp_dc found: {sp_dc}")
        save_token(user_id, sp_dc)
    else:
        print("❌ sp_dc not found after timeout")

if name == "main": app.run(host="0.0.0.0", port=8000)

