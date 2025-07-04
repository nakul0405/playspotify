import threading
import bot
import auth_server

# Bot ko background thread me chalao
bot_thread = threading.Thread(target=bot.main)
bot_thread.start()

# Flask Spotify auth server ko run karo
auth_server.app.run(host="0.0.0.0", port=8080)
