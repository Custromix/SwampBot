import discord
from discord.ext import commands
import yt_dlp
import asyncio
from collections import deque
import os
from dotenv import load_dotenv
load_dotenv()
from stay_alive import Stay_alive
from william_ta_gueule import handle_spam

# ─────────────────────────────────────────────
#  Configuration yt-dlp
# ─────────────────────────────────────────────
YTDL_OPTIONS = {
    "format": "bestaudio/best",
    "noplaylist": False,
    "quiet": True,
    "listformats": True,
    "no_warnings": True,
    "default_search": "auto",
    "source_address": "0.0.0.0",
    "verbose": True,
}


cookies_path = os.getenv("COOKIES_PATH")
if cookies_path:
    if os.path.exists(cookies_path):
        print(f"✅ Fichier cookies trouvé : {cookies_path}")
        YTDL_OPTIONS["cookiefile"] = cookies_path
    else:
        print(f"❌ Fichier cookies introuvable : {cookies_path}")
else:
    print("⚠️ COOKIES_PATH non défini dans le .env")

    

FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn",
}


url = "https://www.youtube.com/watch?v=DdZluvojGWI"

ydl_opts = {
    "quiet": False,
    "listformats": True,
}
#test
with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    ydl.extract_info(url, download=False)


