<div align="center">

# 🎧 VEGA Spotify Downloader Bot

**A Telegram bot for retrieving audio from Spotify links and sending the resulting MP3 files directly in chat.**

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Telegram](https://img.shields.io/badge/Telegram-Bot-26A5E4?style=for-the-badge&logo=telegram&logoColor=white)](https://telegram.org/)
[![Powered by SpotDL](https://img.shields.io/badge/Powered%20by-SpotDL-1DB954?style=for-the-badge&logo=spotify&logoColor=white)](https://github.com/spotDL/spotify-downloader)

**VEGA & Logic** · By [@TopVeGa](https://t.me/TopVeGa)

</div>

---

## 📖 Overview

VEGA Spotify Downloader is a Python-based Telegram bot that accepts supported Spotify URLs, processes them with **SpotDL**, and sends the resulting audio files to the user as MP3 audio messages.

The bot can process individual tracks, albums, playlists, and artist links. It also displays download progress and includes an optional password-based access system.

## ✨ Features

- **Multiple Spotify link types** — supports tracks, albums, playlists, and artists.
- **MP3 delivery** — sends downloaded audio files directly to the Telegram chat.
- **Live progress updates** — displays the current processing stage and an overall progress bar.
- **Metadata-aware filenames** — uses artist and track title information in output filenames.
- **Optional access control** — restricts usage to authorized Telegram users when authentication is enabled.
- **Password login** — users can authenticate by sending the configured password.
- **Owner access** — the configured owner ID is automatically authorized.
- **Logout command** — allows an authorized user to remove their own login entry.
- **Temporary file cleanup** — removes each request's download directory after processing.
- **Logging and error handling** — records processing details and reports download or delivery failures.

## 🔗 Supported Spotify Links

The bot recognizes these Spotify URL formats:

| Content | Example format |
|---|---|
| Track | `https://open.spotify.com/track/TRACK_ID` |
| Album | `https://open.spotify.com/album/ALBUM_ID` |
| Playlist | `https://open.spotify.com/playlist/PLAYLIST_ID` |
| Artist | `https://open.spotify.com/artist/ARTIST_ID` |
| Spotify URI | `spotify:track:TRACK_ID` |

Regional Spotify URLs containing a locale segment are also recognized.

## 🧰 Requirements

- Python 3.10 or newer
- A Telegram bot token from [@BotFather](https://t.me/BotFather)
- `spotdl` installed and available in the system `PATH`
- Internet access on the host machine

Python packages:

- `python-telegram-bot`
- `python-dotenv`

## 🚀 Installation

### 1. Clone the repository

```bash
git clone https://github.com/TopVeGa/Spotify-Bot.git
cd Spotify-Bot
```

Replace the repository URL with your actual repository URL if the project is hosted elsewhere.

### 2. Install Python dependencies

```bash
python -m pip install -U python-telegram-bot python-dotenv spotdl
```

Make sure the `spotdl` command is available:

```bash
spotdl --version
```

### 3. Configure the Telegram token

Create a `.env` file in the same directory as `spotify.py`:

```env
TELEGRAM_TOKEN=YOUR_TELEGRAM_BOT_TOKEN
```

Do not publish your bot token or commit the `.env` file to Git.

### 4. Configure access control

The project includes a `config.json` file:

```json
{
  "AUTH": {
    "ENABLE": false,
    "PASSWORD": "CHANGE_THIS_PASSWORD",
    "OWNER_ID": null,
    "USERS": []
  }
}
```

| Setting | Description |
|---|---|
| `ENABLE` | Set to `true` to require authentication. |
| `PASSWORD` | Password users send to log in. |
| `OWNER_ID` | Telegram numeric ID of the owner. |
| `USERS` | List of authorized Telegram user IDs. |

When authentication is disabled, the bot accepts requests from users who can access it. When enabled, users must be listed as authorized or log in with the configured password.

**Security note:** Change the example password before enabling authentication. Keep `config.json` private because it contains access-control information.

### 5. Start the bot

```bash
python spotify.py
```

The bot will start polling Telegram for updates.

## 💬 Commands & Usage

| Command | Description |
|---|---|
| `/start` | Shows the welcome message and authentication prompt when enabled. |
| `/help` | Displays usage instructions and available commands. |
| `/logout` | Removes the current user from the authorized-user list. |

### Downloading audio

1. Open the Telegram bot.
2. Send `/start`.
3. If authentication is enabled, send the configured password.
4. Send a supported Spotify track, album, playlist, or artist link.
5. Wait for the progress message.
6. The bot sends the available MP3 files to the chat.

## 📊 Download Progress

The bot tracks SpotDL's output and reports stages such as:

1. Searching for the song
2. Retrieving audio metadata
3. Downloading audio
4. Converting audio
5. Embedding metadata
6. Completed, skipped, or failed

For multi-track requests, the progress message also indicates the current item and overall completion percentage.

## 📁 Project Structure

```text
Spotify-Bot/
├── spotify.py       # Main Telegram bot application
├── config.json      # Authentication configuration
├── .env             # Telegram token (create this file)
├── downloads/       # Temporary per-request download folders
├── LICENSE
└── README.md
```

The `downloads/` directory is created automatically when the bot starts. Individual request folders are removed after processing.

## ⚙️ Important Notes

- The bot relies on the external `spotdl` command-line program to process Spotify links.
- The host must have a working internet connection and a compatible SpotDL installation.
- Spotify availability, metadata, and source availability may affect whether a requested item can be retrieved.
- Telegram upload limits and network conditions may affect audio delivery.
- The bot sends files with the `.mp3` extension found in the request's temporary output directory.
- This project does not provide Spotify Premium access or bypass Spotify account restrictions.

## 🛡️ Copyright & Responsible Use

Use this project only for content you are legally permitted to access, download, and store. Respect Spotify's terms, copyright laws, and the rights of artists, labels, publishers, and other content owners.

Do not redistribute copyrighted audio without the required permission or license. The project author does not claim ownership of third-party music or metadata.

## 📄 License

This repository includes an MIT license file together with a VEGA intellectual-property and responsible-use notice. Review the included `LICENSE` file before copying, modifying, or redistributing the project.

## 👨‍💻 Credits

- **Project / Brand:** VEGA & Logic
- **Developer:** [@TopVeGa](https://t.me/TopVeGa)
- **Audio processing:** [SpotDL](https://github.com/spotDL/spotify-downloader)
- **Telegram framework:** [python-telegram-bot](https://python-telegram-bot.org/)

---

<div align="center">

**VEGA & Logic**  
© 2015–2025 · All rights reserved to their respective owners.

</div>


<!-- ═══════════════════════════════════════════════════════════════════════ --><!--                       Copyright | Footer                              --><!-- ═══════════════════════════════════════════════════════════════════════ --><div align="center">
  <img src="https://capsule-render.vercel.app/api?type=rect&color=0:3B82F6,100:0F172A&height=4&width=40%&section=header" />
  <br><br>  <p style="color: #9CA3AF; font-size: 14px;">
    <b style="color: #3B82F6;">Brand:</b> VEGA &amp; Logic &nbsp;|&nbsp;
    <b style="color: #3B82F6;">Copyright:</b> © 2015 - 2025
  </p>
  <p style="color: #6B7280; font-size: 12px;">
  </p>
</div><br><!-- Smooth Gradient Footer Background --><img src="https://capsule-render.vercel.app/api?type=waving&color=0:3B82F6,50:1E3A8A,100:0F172A&height=120&section=footer" width="100%" /></div>
