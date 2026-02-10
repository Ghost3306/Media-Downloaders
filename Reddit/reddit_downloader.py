import subprocess
import os
from pathlib import Path
import Engine
from RedDownloader import RedDownloader
import re
from concurrent.futures import ThreadPoolExecutor

class Reddit:
    @staticmethod
    def download_by_url(url):

        parent_dir = Path.cwd().parent
        reddit_dir = parent_dir / "Reddit"
        downloads_dir = reddit_dir / "Downloads"
        downloads_dir.mkdir(parents=True, exist_ok=True)

        try:
            v_title = RedDownloader.GetPostTitle(url).Get().split(".")[0]
        except Exception:
            v_title = RedDownloader.GetPostTitle(url).Get()

        v_title = re.sub(r'[<>:"/\\|?*]', '_', v_title)
        print("Title:", v_title)

        download = Engine.Download(
            url,
            quality=1080,
            title=f"temp_{v_title}",
            output=v_title,
            destination=downloads_dir
        )

        result = download.GetResult()
        media_type = result["type"]

        # -------------------------------------------------
        # ONLY VIDEO → FFmpeg
        # -------------------------------------------------
        if media_type != "v":
            print("Not a video post. Skipping FFmpeg.")
            print("Downloaded files:", result["files"])
            return

        temp_video = downloads_dir / f"temp_{v_title}.mp4"
        temp_audio = downloads_dir / f"temp_{v_title}.mp3"
        final_video = downloads_dir / f"{v_title}.mp4"

        if not temp_video.exists() or not temp_audio.exists():
            print("Video or audio file missing. Cannot merge.")
            return

        result = subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i", str(temp_video),
                "-i", str(temp_audio),
                "-c:v", "copy",
                "-c:a", "copy",
                str(final_video)
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        print(result.stderr)

        if temp_video.exists():
            os.remove(temp_video)

        if temp_audio.exists():
            os.remove(temp_audio)

        print("Video downloaded successfully")
        print("Saved at:", final_video)


URLs = [
    "https://www.reddit.com/r/BuyItForLife/comments/1q0zlxe/buy_it_for_life_cars/",
    "https://www.reddit.com/r/coolguides/comments/1iahpgp/a_cool_guide_to_used_cars_to_avoid/",
    "https://www.reddit.com/r/Mcat/comments/1dp9g52/cars_is_easy_actually/",
    "https://www.reddit.com/r/CarsIndia/comments/19f3ye6/tata_cars_dont_have_resale_value/",
    "https://www.reddit.com/r/CarsIndia/comments/1qq8shb/stumbled_upon_this_video_and_now_im_rethinking_my/",
    "https://www.reddit.com/r/youtubeindia/comments/1qbqere/cars_youtube_at_its_best_tata_punch_facelift/"
]

# for url in URLs:
#     Reddit.download_by_url(url)
with ThreadPoolExecutor(max_workers=3) as executor:
    executor.map(Reddit.download_by_url,URLs)