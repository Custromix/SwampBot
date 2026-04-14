import os
from dotenv import load_dotenv
load_dotenv()
import yt_dlp

url = "https://www.youtube.com/watch?v=DdZluvojGWI"

YTDL_OPTIONS = {
    "format": "bestaudio/best",
    "quiet": True,
    "no_warnings": True,
    "noplaylist": True,
    "extractor_args": {
        "youtube": {
            "player_client": ["android", "ios"]
        }
    },
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

#test
with yt_dlp.YoutubeDL(YTDL_OPTIONS) as ydl:
    ydl.extract_info(url, download=False)