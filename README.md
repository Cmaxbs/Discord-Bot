# Discord Music Bot

A Python-based Discord music bot that lets users play music in voice channels using YouTube and Spotify.

## Features

- 🎵 Play music from YouTube
- 🎧 Play Spotify tracks and playlists
- 📃 Queue multiple songs and playlists
- ⏭️ Skip, pause, resume, and stop playback
- 🔎 Automatically finds the best YouTube match for Spotify tracks
- 🔊 Stream audio directly into Discord voice channels

## Commands

| Command | Description |
|---|---|
| `/play <query>` | Play a YouTube/Spotify track or search for a song |
| `/queue` | Show the current music queue |
| `/skip` | Skip the current song |
| `/pause` | Pause playback |
| `/resume` | Resume playback |
| `/stop` | Stop playback and disconnect from the voice channel |

## Tech Stack

- **Python**
- **discord.py** — Discord bot and voice integration
- **yt-dlp** — YouTube search and audio extraction
- **Spotipy** — Spotify API integration
- **Spotify Web API**
- **FFmpeg** — Audio processing and playback

## How It Works

When a user requests a song, the bot determines the source:

1. **YouTube link** → Uses the provided YouTube URL.
2. **Spotify track** → Retrieves the track and artist information through Spotify, then searches YouTube for the best matching audio.
3. **Spotify playlist** → Retrieves the playlist tracks and adds their YouTube matches to the queue.
4. **Search query** → Searches YouTube and selects the closest matching result.

The selected audio is then streamed through FFmpeg into the Discord voice channel.

## Requirements

- Python 3.10+
- FFmpeg
- A Discord Bot application
- Spotify Developer credentials

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/Cmaxbs/Discord-Bot.git
cd Discord-Bot
```

### 2. Install Python dependencies

```bash
pip install discord.py yt-dlp spotipy
```

### 3. Install FFmpeg

FFmpeg must be installed and available in your system PATH.

### 4. Configure API credentials

Create your Discord bot through the Discord Developer Portal and create Spotify API credentials through the Spotify Developer Dashboard.

Store your credentials securely rather than committing them directly to the repository.

### 5. Run the bot

```bash
python Discordbot.py
```

Once the bot is running, its slash commands will be synchronized with Discord.

## Project Structure

```text
Discord-Bot/
├── .github/
│   └── workflows/
│       └── python-package-conda.yml
├── Discordbot.py
├── .gitignore
└── README.md
```

## Future Improvements

- Add volume control
- Add `/remove` and `/clear` queue commands
- Improve YouTube search accuracy
- Add automatic voice-channel disconnect after inactivity
- Improve error handling and user feedback
- Move credentials to environment variables
- Add automated tests and CI/CD

## License

This project is open source. Add a license here if you decide to publish the project under a specific license.

## Author

**Max**

GitHub: https://github.com/Cmaxbs
