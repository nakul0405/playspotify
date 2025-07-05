## 🎧 PlaySpotify – Telegram Bot for Spotify Friends Activity

> *Made with ❤️ & Madness by [@Nakulrathod0405](https://t.me/Nakulrathod0405)*

A Telegram bot that shows **your Spotify activity** and your **friends' listening activity**, — even if Spotify doesn’t show it anymore!

This bot uses your `sp_dc` cookie (captured automatically via login) to show real-time activity.

---

### ⚙️ Features

* 🔐 Spotify login with **automatic cookie extraction**
* 🎵 See what **you're currently listening to**
* 👥 Track what **your Spotify friends** are listening to (Spotivity-style)
* 📲 Fully works inside Telegram
* 🧠 No need for Spotify Developer credentials
* ☁️ Hosted using Render with Docker

---

### 🚀 Commands

| Command      | Description                                       |
| ------------ | ------------------------------------------------- |
| `/start`     | Welcome message with instructions                 |
| `/login`     | Login securely via Spotify to auto-extract cookie |
| `/setcookie` | Manually set your `sp_dc` token                   |
| `/mytrack`   | See your currently playing song                   |
| `/friends`   | See what your friends are listening to            |
| `/logout`    | Logout and clear your stored token                |

---

### 🧠 How It Works

1. User types `/login` in the Telegram bot
2. Bot gives a secure login URL (powered by Flask)
3. User logs in to Spotify → `sp_dc` cookie is auto-extracted
4. Bot stores the cookie and uses it for all Spotify requests
5. User can now use `/mytrack` or `/friends` at any time

---

### 🛠 Setup Instructions (For Devs)

#### 🔐 1. Clone the Repo

```bash
git clone https://github.com/yourname/playspotify.git
cd playspotify
```

#### 🧪 2. Install Dependencies

```bash
pip install -r requirements.txt
```

#### ⚙️ 3. Add Your `.env`

Create a `.env` file or set environment variables:

```
BOT_TOKEN=your_telegram_bot_token
AUTH_SERVER_URL=https://yourdomain.com
```

#### ▶️ 4. Run Locally

```bash
bash start.sh
```

Or:

```bash
python backend/auth_server.py &
python bot/bot.py
```

---

### 🐳 Docker (Optional)

#### 📦 Build

```bash
docker build -t playspotify .
```

#### ▶️ Run

```bash
docker run -d -p 5000:5000 --env-file .env playspotify
```

---

### 🛡️ Security Note

* No Spotify password is ever saved.
* Only the `sp_dc` cookie is used for login (same method as Spotivity).
* Cookies are stored securely in a local JSON file.
* For production, consider encrypting token storage or using a DB.

---

### 🤝 Credits

Used by:

* Telegram + Python community

Created with 💻 by **[Nakulrathod0405](https://t.me/Nakulrathod0405)**

---

### 🌐 Hosting

* Telegram bot runs on Render
* Flask login server also hosted on same Render container

---

### ✅ Example Usage

```
/login → Login link
/mytrack → 🎵 Blinding Lights - The Weeknd
/friends → 👥 Nishuuu: Listening to "Lover - Taylor Swift"
