# friends.py

import requests

def get_friends_activity(sp_dc):
    headers = {
        "Cookie": f"sp_dc={sp_dc}",
        "app-platform": "WebPlayer",
        "User-Agent": "Mozilla/5.0"
    }

    url = "https://spclient.wg.spotify.com/presence-view/v1/buddylist"
    r = requests.get(url, headers=headers)

    print("Friends API status:", r.status_code)
    print("Response:", r.text)

    if r.status_code == 200:
        return r.json()
    else:
        return None
