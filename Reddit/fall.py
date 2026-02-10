from redvid import Downloader
import os

def down(link, download_dir):
    reddit = Downloader(max_q=True)

    # ensure directory exists
    os.makedirs(download_dir, exist_ok=True)

    # force redvid to save here
    reddit.path = download_dir

    reddit.url = link
    reddit.download()
