from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
import time
import random
import urllib.parse
import os
import csv
import time
import random
import subprocess
import urllib3
import base64
from selenium.common.exceptions import TimeoutException, WebDriverException
from bs4 import BeautifulSoup


#config
FIREFOX_PROFILE_PATH = r"C:\Users\lrraw\AppData\Roaming\Mozilla\Firefox\Profiles\AVtzXYQk.Profile 1"
INPUT_LINKS_FILE = "linkedin_post_links.txt"
KEYWORD = input("Enter Keyword : ")
SCROLL_COUNT = 2
OUTPUT_FILE = "linkedin_post_links.txt"

#firefox setup
options = Options()
options.headless = False
options.add_argument("-profile")
options.add_argument(FIREFOX_PROFILE_PATH)

driver = webdriver.Firefox(service=Service(), options=options)


encoded = urllib.parse.quote(KEYWORD)
url = f"https://www.linkedin.com/search/results/content/?keywords={encoded}"
driver.get(url)
time.sleep(6)

#scrapping
post_links = set()

for scroll in range(SCROLL_COUNT):
    print(f"Scroll {scroll + 1}/{SCROLL_COUNT}")

    posts = driver.find_elements(By.XPATH, "//div[contains(@data-urn, 'urn:li:activity:')]")

    for post in posts:
        urn = post.get_attribute("data-urn")
        if urn and "activity" in urn:
            link = f"https://www.linkedin.com/feed/update/{urn}"
            post_links.add(link)

    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(random.uniform(2.5, 4))

driver.quit()

#save
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    for link in sorted(post_links):
        f.write(link + "\n")

print(f"\nExtracted {len(post_links)} REAL post links")
print(f"Saved to {OUTPUT_FILE}")


BASE_DIR = "linkedin_downloads"
IMAGE_DIR = os.path.join(BASE_DIR, "images")
VIDEO_DIR = os.path.join(BASE_DIR, "videos")
CSV_FILE = os.path.join(BASE_DIR, "text_posts.csv")

MAX_RETRIES_PER_POST = 3
RETRY_COOLDOWN = 8

os.makedirs(IMAGE_DIR, exist_ok=True)
os.makedirs(VIDEO_DIR, exist_ok=True)
os.makedirs(BASE_DIR, exist_ok=True)


options = Options()
options.headless = False
options.page_load_strategy = "none"
options.add_argument("-profile")
options.add_argument(FIREFOX_PROFILE_PATH)

driver = webdriver.Firefox(service=Service(), options=options)
driver.set_page_load_timeout(10)
driver.set_script_timeout(10)


if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow(["post_url", "post_text"])


def safe_execute(action, label="action"):
    for attempt in range(1, MAX_RETRIES_PER_POST + 1):
        try:
            return action()
        except (TimeoutException, WebDriverException, urllib3.exceptions.ReadTimeoutError) as e:
            print(f"⚠️ {label} failed ({attempt}/{MAX_RETRIES_PER_POST}) → {type(e).__name__}")
            try:
                driver.execute_script("window.stop();")
                driver.get("about:blank")
            except:
                pass
            time.sleep(RETRY_COOLDOWN)
    print(f"{label} skipped after retries")
    return None

def safe_open(url):
    def _open():
        driver.get(url)
        time.sleep(3)
        driver.execute_script("window.stop();")
    safe_execute(_open, f"open {url}")

#video
def download_video(url):
    def _download():
        driver.get("about:blank")
        time.sleep(2)
        subprocess.run(
            ["yt-dlp", "-f", "mp4", "-o",
             os.path.join(VIDEO_DIR, "%(id)s.%(ext)s"), url],
            timeout=600,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    safe_execute(_download, "video download")

#image save


def save_images(post_index):
    imgs = driver.find_elements(By.XPATH, "//img[contains(@src,'media.licdn.com')]")
    seen = set()
    count = 0

    for img in imgs:
        src = img.get_attribute("src")
        if not src or src in seen:
            continue
        seen.add(src)
        count += 1

        img_path = os.path.join(IMAGE_DIR, f"post_{post_index}_img_{count}.jpg")

        def _fetch():
            return driver.execute_async_script("""
                const src = arguments[0];
                const cb = arguments[arguments.length - 1];
                fetch(src)
                  .then(r => r.blob())
                  .then(b => {
                      const fr = new FileReader();
                      fr.onloadend = () => cb(fr.result);
                      fr.readAsDataURL(b);
                  });
            """, src)

        data = safe_execute(_fetch, "image fetch")

        if data:
            image_base64 = data.split(",")[1]
            image_bytes = base64.b64decode(image_base64)

            with open(img_path, "wb") as f:
                f.write(image_bytes)

            print(f"Saved {img_path}")

#text extraction
def extract_post_text():
    texts = []

    elements = driver.find_elements(
        By.XPATH,
        "//div[contains(@data-test-id,'commentary') or "
        "contains(@class,'feed-shared-update-v2__description')]"
    )

    for el in elements:
        t = el.text.strip()
        if t and t not in texts:
            texts.append(t)

    if not texts:
        fallback = driver.find_elements(
            By.XPATH,
            "//*[string-length(normalize-space(text())) > 20]"
        )
        for el in fallback[:5]:
            if el.text.strip():
                texts.append(el.text.strip())

    return " ".join(texts).strip()[:5000]

def save_text_to_csv(url, text):
    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([url, text or "[NO TEXT FOUND]"])

# =========================
# MAIN LOOP
# =========================

from urllib.parse import urlsplit, urlunsplit

def clean_url(url):
    p = urlsplit(url)
    return urlunsplit((p.scheme, p.netloc, p.path, "", ""))

with open(INPUT_LINKS_FILE, "r", encoding="utf-8") as f:
    links = [clean_url(l.strip()) for l in f if l.strip()]


for idx, url in enumerate(links, start=1):
    print(f"\n🔍 Processing post {idx}")
    safe_open(url)

    soup = BeautifulSoup(driver.page_source, "html.parser")

    # VIDEO
    if soup.find("video"):
        download_video(url)
        continue

    # IMAGE
    if soup.find("img", src=lambda x: x and "media.licdn.com" in x):
        save_images(idx)
        continue

    # TEXT
    post_text = extract_post_text()
    save_text_to_csv(url, post_text)

    time.sleep(random.uniform(3, 6))

driver.quit()
print("\nProgram excuted successfully")
