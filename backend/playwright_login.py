from playwright.sync_api import sync_playwright
import sys
import json

user_id = sys.argv[1]

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    page.goto("https://accounts.spotify.com/en/login")

    print("[INFO] Waiting 45 seconds for user to login...")
    page.wait_for_timeout(45000)  # Waits 45 seconds

    cookies = context.cookies()
    sp_dc = None
    for c in cookies:
        if c['name'] == 'sp_dc':
            sp_dc = c['value']
            break

    if sp_dc:
        try:
            with open("cookies.json") as f:
                all_tokens = json.load(f)
        except:
            all_tokens = {}

        all_tokens[user_id] = sp_dc

        with open("cookies.json", "w") as f:
            json.dump(all_tokens, f, indent=2)

        print(f"[✅] sp_dc saved for user {user_id}")
    else:
        print("[❌] sp_dc NOT FOUND")

    browser.close()
