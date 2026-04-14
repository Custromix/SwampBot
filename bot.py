import yt_dlp

url = "https://www.youtube.com/watch?v=DdZluvojGWI"

ydl_opts = {
    "quiet": False,
    "listformats": True,
}

#test
with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    ydl.extract_info(url, download=False)