import requests

# ------------------ Fetch Raw Buddylist ------------------ #
def get_buddylist(sp_dc: str, sp_key: str = None):
    headers = {
        "cookie": f"sp_dc={sp_dc};"
    }

    if sp_key:
        headers["cookie"] += f" sp_key={sp_key};"

    headers.update({
        "user-agent": "Spotify/1.1.46.916.g416cacf1 Spotify/1.1.46.916.g416cacf1",
        "app-platform": "WebPlayer",
        "accept": "application/json",
    })

    try:
