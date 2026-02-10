import instaloader
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed

# ---------------------------
# CONFIG
# ---------------------------
DOWNLOAD_DIR = "downloads"
MAX_WORKERS = 3   # parallel downloads

URLS = [
    "https://www.instagram.com/reel/DUD8FaWEqlf/?igsh=dzBiYnk0bmZ1aTd2",
    "https://www.instagram.com/reel/DSsFamCjFgy/?igsh=aXFnN2pkaXZpZTE1",
    "https://www.instagram.com/reel/DSMp_gLDPP-/?igsh=eG43bXp1MGt6cXg=",
    "https://www.instagram.com/reel/DRmTjrdj-oU/?igsh=MTVocmRoZ3E5N3VwMA==",


]

USERNAME = None   # optional
PASSWORD = None   # optional

# ---------------------------
# HELPERS
# ---------------------------
def extract_shortcode(url: str) -> str:
    path = urlparse(url).path.strip("/")
    parts = path.split("/")
    if len(parts) < 2:
        raise ValueError(f"Invalid Instagram URL: {url}")
    return parts[1]

def download_reel(url: str) -> str:
    shortcode = extract_shortcode(url)

    # One Instaloader instance PER THREAD
    L = instaloader.Instaloader(
        download_comments=False,
        save_metadata=False,
        post_metadata_txt_pattern="",
        dirname_pattern=DOWNLOAD_DIR
    )

    # Optional login (highly recommended)
    if USERNAME and PASSWORD:
        L.login(USERNAME, PASSWORD)

    post = instaloader.Post.from_shortcode(L.context, shortcode)
    L.download_post(post, target=DOWNLOAD_DIR)

    return shortcode

# ---------------------------
# PARALLEL EXECUTION
# ---------------------------
print(f"Starting downloads (max {MAX_WORKERS} at a time)...\n")

with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    future_to_url = {
        executor.submit(download_reel, url): url for url in URLS
    }

    for future in as_completed(future_to_url):
        url = future_to_url[future]
        try:
            shortcode = future.result()
            print(f"Downloaded: {shortcode}")
        except Exception as e:
            print(f"Failed: {url}")
            print(f"Reason: {e}")

print("\nAll tasks finished.")
