import os
import re
import subprocess
import logging
from pytubefix import YouTube
from pytubefix.cli import on_progress
from concurrent.futures import ThreadPoolExecutor, as_completed

# ---------------- CONFIG ----------------
URLS = [
    "https://www.youtube.com/watch?v=SdfipypqcsM",
    "https://www.youtube.com/watch?v=lexgFTZ6Wi4",
    "https://www.youtube.com/watch?v=gM5JYzyksOI",
    "https://www.youtube.com/watch?v=vUKQHLkgUqQ",
    "https://www.youtube.com/watch?v=pccIe9LgEZc",
    "https://www.youtube.com/watch?v=CQRH7UdArkc",
    "https://www.youtube.com/watch?v=JTCrCrsi3rM",
    "https://www.youtube.com/watch?v=vW_l0EBQYKw",
    "https://www.youtube.com/watch?v=gIiXo_P-hbc",
    "https://www.youtube.com/watch?v=aswaHgLa19E",
    "https://www.youtube.com/watch?v=NlYyT1uHeLM",
]

DOWNLOAD_DIR = "downloads"
MAX_CONCURRENT = 5
# ----------------------------------------

os.makedirs(DOWNLOAD_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(threadName)s | %(message)s",
    datefmt="%H:%M:%S"
)


def safe_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "", name)


def download_high_res(url):
    try:
        yt = YouTube(url, on_progress_callback=on_progress)
        title = safe_filename(yt.title)

        logging.info(f"START → {title}")

        video_stream = (
            yt.streams
            .filter(adaptive=True, file_extension="mp4", only_video=True)
            .order_by("resolution")
            .desc()
            .first()
        )

        audio_stream = yt.streams.get_audio_only()

        video_temp = os.path.join(DOWNLOAD_DIR, f"{title}__video.mp4")
        audio_temp = os.path.join(DOWNLOAD_DIR, f"{title}__audio.m4a")
        output_file = os.path.join(DOWNLOAD_DIR, f"{title}.mp4")

        video_stream.download(DOWNLOAD_DIR, filename=os.path.basename(video_temp))
        audio_stream.download(DOWNLOAD_DIR, filename=os.path.basename(audio_temp))

        subprocess.run(
            [
                "ffmpeg", "-y",
                "-i", video_temp,
                "-i", audio_temp,
                "-c", "copy",
                output_file
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        os.remove(video_temp)
        os.remove(audio_temp)

        logging.info(f"DONE  → {output_file}")

    except Exception as e:
        logging.error(f"FAIL  → {url} | {e}")


if __name__ == "__main__":
    

    with ThreadPoolExecutor(max_workers=MAX_CONCURRENT) as executor:
        futures = [executor.submit(download_high_res, url) for url in URLS]

        for future in as_completed(futures):
            future.result()

    logging.info("=== All downloads finished ===")
