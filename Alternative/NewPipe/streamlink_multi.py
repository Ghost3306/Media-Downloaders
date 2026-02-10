import subprocess
import os
import re
from urllib.parse import urlparse, parse_qs

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOWNLOADS_DIR = os.path.join(BASE_DIR, "downloads")
os.makedirs(DOWNLOADS_DIR, exist_ok=True)

def get_video_id(url):
    parsed = urlparse(url)

    if "youtu.be" in parsed.netloc:
        return parsed.path.strip("/")

    qs = parse_qs(parsed.query)
    return qs.get("v", ["video"])[0]

def get_best_resolution(url):
    """
    Uses streamlink to list available streams
    and returns the highest resolution found.
    """
    try:
        result = subprocess.run(
            ["streamlink", url],
            capture_output=True,
            text=True,
            check=True
        )
    except subprocess.CalledProcessError:
        return "unknown"

    # Example matches: 360p, 720p, 1080p, 1440p
    resolutions = re.findall(r"(\d+p)", result.stdout)

    if not resolutions:
        return "unknown"

    # Sort numerically (720p < 1080p < 1440p)
    resolutions.sort(key=lambda x: int(x.replace("p", "")))
    return resolutions[-1]

def download_with_streamlink(url, quality="best"):
    video_id = get_video_id(url)
    output_file = os.path.join(DOWNLOADS_DIR, f"{video_id}.mp4")

    resolution = get_best_resolution(url)
    print(f"⬇ Downloading {video_id} at resolution: {resolution}")

    cmd = [
        "streamlink",
        "--loglevel", "error",
        url,
        quality,
        "-o", output_file
    ]

    try:
        subprocess.run(cmd, check=True)
        print(f"Saved: {output_file}\n")
    except subprocess.CalledProcessError:
        print(f"Failed: {url}\n")

# ---------------- MAIN ----------------

URLS = [
    "https://youtu.be/rkW_0_ZDDw0",
    "https://youtu.be/TmXL3Ejl9II",
    "https://youtu.be/OK8Vu12zN8A",
    "https://youtu.be/MVeeRCRw5kM",
    "https://youtu.be/QMKPvfNB6l0",
    "https://youtu.be/IolHQoQso0c",
    "https://youtu.be/OMpVji16f2E",
]

for url in URLS:
    download_with_streamlink(url)
