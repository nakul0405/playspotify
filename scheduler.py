import time
import threading
from telegram import Bot
from config import BOT_TOKEN
from store import load_last_seen, save_last_seen, get_cookie, load_tokens
from buddylist import get_buddylist, parse_buddylist

bot = Bot(token=BOT_TOKEN)

def detect_changes(user_id, old, new):
    """Return newly playing friends by comparing old vs new list"""
    old_map = {f['username']: f['track'] for f in old}
    new_tracks = []

    for friend in new:
        name = friend["username"]
        track = friend["track"]
        if name not in old_map or old_map[name] != track:
            new_tracks.append(friend)

    return new_tracks

def auto_check_loop():
    print("[SCHEDULER] Started background friend tracking...")

    while True:
        try:
            tokens = load_tokens()
            if not tokens:
                print("[SCHEDULER] No logged-in users.")
                time.sleep(300)
                continue

            for user_id in tokens:
                sp_dc, sp_key = get_cookie(user_id)
                if not sp_dc:
                    continue

                raw = get_buddylist(sp_dc, sp_key)
                if not raw:
                    continue

                new_list = parse_buddylist(raw)
                old_list = load_last_seen().get(str(user_id), [])

                changes = detect_changes(user_id, old_list, new_list)

                if changes:
                    msg = "🆕 *Friend Activity Update:*\n"
                    for f in changes:
                        msg += f"👤 *{f['username']}* is now listening to *{f['track']}* by *{f['artist']}*\n"

                    try:
                        bot.send_message(chat_id=int(user_id), text=msg, parse_mode="Markdown")
                        print(f"[SCHEDULER] Sent update to {user_id}")
                    except Exception as e:
                        print(f"[SCHEDULER ERROR] Failed to send to {user_id}: {e}")

                # Update last seen
                save_last_seen(user_id, new_list)

        except Exception as e:
            print(f"[SCHEDULER ERROR] {e}")

        time.sleep(300)  # Wait 5 minutes

# ------------------ Run Thread ------------------ #
def start_scheduler():
    thread = threading.Thread(target=auto_check_loop)
    thread.daemon = True
    thread.start()
