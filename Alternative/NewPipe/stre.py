import os
import re
from streamlink import Streamlink
from urllib.parse import urlparse, parse_qs

# ---------------- CONFIG ----------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOWNLOADS_DIR = os.path.join(BASE_DIR, "downloads")
os.makedirs(DOWNLOADS_DIR, exist_ok=True)

CHUNK_SIZE = 1024 * 1024  # 1MB

# ---------------- HELPERS ----------------

def get_video_id(url):
    parsed = urlparse(url)
    if "youtu.be" in parsed.netloc:
        return parsed.path.strip("/")
    qs = parse_qs(parsed.query)
    return qs.get("v", ["video"])[0]

def choose_stream(streams):
    """
    Prefer 720p, then 480p, then 360p
    """
    preferred = ["720p", "480p", "360p"]

    for res in preferred:
        if res in streams:
            return streams[res], res

    # fallback
    return streams["best"], "best"

# ---------------- DOWNLOADER ----------------

def download_with_streamlink(url):
    session = Streamlink()

    # IMPORTANT OPTIONS
    session.set_option("stream-types", "mp4")
    session.set_option("ffmpeg-fout", "mp4")
    session.set_option("stream-timeout", 60)

    streams = session.streams(url)
    if not streams:
        print(f"✖ No streams found: {url}")
        return

    stream, resolution = choose_stream(streams)

    video_id = get_video_id(url)
    output_path = os.path.join(DOWNLOADS_DIR, f"{video_id}.mp4")

    print(f"⬇ Downloading {video_id} at {resolution}")
    print(f"🎞 Available streams: {', '.join(streams.keys())}")

    with stream.open() as fd, open(output_path, "wb") as f:
        while True:
            data = fd.read(CHUNK_SIZE)
            if not data:
                break
            f.write(data)

    print(f"✔ Saved: {output_path}\n")

# ---------------- MAIN ----------------

URLS = [
    "https://youtu.be/rkW_0_ZDDw0",
    "https://youtu.be/TmXL3Ejl9II",
]

for url in URLS:
    download_with_streamlink(url)
