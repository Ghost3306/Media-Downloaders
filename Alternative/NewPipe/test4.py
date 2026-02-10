import os
import re
import subprocess
from pytubefix import YouTube
from pytubefix.cli import on_progress
URLS = [
    "https://www.youtube.com/watch?v=JrOiJJQnnsM",
"https://www.youtube.com/watch?v=SdfipypqcsM",
"https://www.youtube.com/watch?v=lexgFTZ6Wi4",
"https://www.youtube.com/watch?v=gM5JYzyksOI",
"https://www.youtube.com/watch?v=vUKQHLkgUqQ"
]

def safe_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "", name)

def download_high_res(url):
    yt = YouTube(url, on_progress_callback=on_progress)

    title = safe_filename(yt.title)
    print(f"\nTitle: {title}")

    video_stream = (
        yt.streams
        .filter(adaptive=True, file_extension="mp4", only_video=True)
        .order_by("resolution")
        .desc()
        .first()
    )

    audio_stream = yt.streams.get_audio_only()

    print("\nDownloading video...")
    video_file = video_stream.download(filename="__video.mp4")

    print("\nDownloading audio...")
    audio_file = audio_stream.download(filename="__audio.m4a")

    output_file = f"{title}.mp4"

    print("\nMerging with ffmpeg...")

    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i", video_file,
            "-i", audio_file,
            "-c", "copy",
            output_file
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    os.remove(video_file)
    os.remove(audio_file)

    print(f"\nDone! Saved as: {output_file}")


for url in URLS:
    download_high_res(url)