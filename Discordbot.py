import discord
from discord import app_commands
from discord.ext import commands
import yt_dlp
import asyncio
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import difflib

# ========= SPOTIFY SETUP =========
SPOTIFY_CLIENT_ID = "id"
SPOTIFY_CLIENT_SECRET = "secret"

sp = spotipy.Spotify(
    auth_manager=SpotifyClientCredentials(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET
    )
)

# ========= DISCORD BOT SETUP =========
intents = discord.Intents.default()

class MusicBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="/",
            intents=intents,
            application_id=1443219816545779775
        )
        self.queue = {}

    async def setup_hook(self):
        await self.tree.sync()
        print("Slash commands synced.")

bot = MusicBot()


# ========= YOUTUBE SEARCH (Improved) =========
async def best_youtube_match(song_name, artist_name=None):
    search_queries = [
        f"{song_name} official audio",
        f"{song_name} {artist_name}",
        f"{song_name} lyrics",
        f"{song_name}",
    ]

    results = []

    for query in search_queries:
        try:
            with yt_dlp.YoutubeDL({
                "quiet": True,
                "extract_flat": "in_playlist",
                "default_search": "ytsearch"
            }) as ydl:
                info = ydl.extract_info(query, download=False)
                if "entries" in info:
                    entry = info["entries"][0]
                    results.append(entry)
        except:
            pass

    if not results:
        return None

    # pick best match using title similarity
    def score(entry):
        title = entry.get("title", "").lower()
        target = f"{song_name} {artist_name}".lower() if artist_name else song_name.lower()
        similarity = difflib.SequenceMatcher(None, title, target).ratio()
        return similarity

    best = max(results, key=score)
    return f"https://www.youtube.com/watch?v={best['id']}"


# ========= PLAY AUDIO =========
async def play_audio(vc, url):
    ydl_opts = {
        "format": "bestaudio/best",
        "quiet": True,
    }

    ffmpeg_opts = {
        "before_options": (
            "-reconnect 1 "
            "-reconnect_streamed 1 "
            "-reconnect_delay_max 5 "
            "-reconnect_at_eof 1 "
            "-reconnect_on_network_error 1 "
            "-nostdin"
        ),
        "options": (
            "-vn "
            "-sn "
            "-dn "
            "-ignore_unknown "
            "-ignore_length 1 "
            "-af \"aresample=async=1\""
        )
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        audio_url = info["url"]

    vc.play(discord.FFmpegPCMAudio(audio_url, **ffmpeg_opts))

# ========= SLASH COMMANDS =========

@bot.tree.command(name="play", description="Play music from YouTube or Spotify")
async def play(interaction: discord.Interaction, query: str):
    await interaction.response.defer()

    if interaction.user.voice is None:
        return await interaction.followup.send("❌ You must be in a voice channel!")

    voice_channel = interaction.user.voice.channel

    if interaction.guild.id not in bot.queue:
        bot.queue[interaction.guild.id] = []

    vc = interaction.guild.voice_client

    if vc is None:
        vc = await voice_channel.connect()

    # Spotify track link
    if "spotify.com/track" in query:
        track_id = query.split("/")[-1].split("?")[0]
        track = sp.track(track_id)

        song_name = track["name"]
        artist_name = track["artists"][0]["name"]

        url = await best_youtube_match(song_name, artist_name)

    # Spotify playlist
    elif "spotify.com/playlist" in query:
        playlist_id = query.split("/")[-1].split("?")[0]
        playlist = sp.playlist_tracks(playlist_id)

        for item in playlist["items"]:
            t = item["track"]
            name = t["name"]
            artist = t["artists"][0]["name"]

            yt = await best_youtube_match(name, artist)
            if yt:
                bot.queue[interaction.guild.id].append(yt)

        return await interaction.followup.send("📃 Playlist added to queue!")

    # YouTube link
    elif "youtube.com" in query or "youtu.be" in query:
        url = query

    # Normal search
    else:
        url = await best_youtube_match(query)

    bot.queue[interaction.guild.id].append(url)
    await interaction.followup.send("🎵 Added to queue.")

    # Play queue automatically
    if not vc.is_playing():
        while bot.queue[interaction.guild.id]:
            song = bot.queue[interaction.guild.id].pop(0)
            await play_audio(vc, song)
            while vc.is_playing():
                await asyncio.sleep(1)


@bot.tree.command(name="queue", description="Show current queue")
async def show_queue(interaction: discord.Interaction):
    guild_id = interaction.guild.id

    if guild_id not in bot.queue or len(bot.queue[guild_id]) == 0:
        return await interaction.response.send_message("📭 Queue is empty.")

    msg = "**🎶 Current Queue:**\n\n"
    for i, url in enumerate(bot.queue[guild_id], start=1):
        msg += f"**{i}.** {url}\n"

    await interaction.response.send_message(msg)


@bot.tree.command(name="skip", description="Skip the current song")
async def skip(interaction: discord.Interaction):
    vc = interaction.guild.voice_client
    if vc and vc.is_playing():
        vc.stop()
        await interaction.response.send_message("⏭️ Skipped!")
    else:
        await interaction.response.send_message("❌ Nothing is playing.")


@bot.tree.command(name="pause", description="Pause the current song")
async def pause(interaction: discord.Interaction):
    vc = interaction.guild.voice_client
    if vc and vc.is_playing():
        vc.pause()
        await interaction.response.send_message("⏸️ Paused!")
    else:
        await interaction.response.send_message("❌ Nothing to pause.")


@bot.tree.command(name="resume", description="Resume the current song")
async def resume(interaction: discord.Interaction):
    vc = interaction.guild.voice_client
    if vc and vc.is_paused():
        vc.resume()
        await interaction.response.send_message("▶️ Resumed!")
    else:
        await interaction.response.send_message("❌ Nothing is paused.")


@bot.tree.command(name="stop", description="Stop and disconnect the bot")
async def stop(interaction: discord.Interaction):
    vc = interaction.guild.voice_client
    bot.queue[interaction.guild.id] = []
    if vc:
        vc.stop()
        await vc.disconnect()
    await interaction.response.send_message("⛔ Stopped and disconnected.")

# ========= RUN BOT =========
bot.run("bot")

