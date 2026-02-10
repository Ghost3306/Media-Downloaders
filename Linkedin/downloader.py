import os
import csv
import time
import random
import subprocess
import urllib3
import base64

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, WebDriverException
from bs4 import BeautifulSoup


INPUT_LINKS_FILE = "linkedin_post_links.txt"

BASE_DIR = "linkedin_downloads"
IMAGE_DIR = os.path.join(BASE_DIR, "images")
VIDEO_DIR = os.path.join(BASE_DIR, "videos")
CSV_FILE = os.path.join(BASE_DIR, "text_posts.csv")

MAX_RETRIES_PER_POST = 3
RETRY_COOLDOWN = 8
MAX_COMMENTS = 30

os.makedirs(BASE_DIR, exist_ok=True)
os.makedirs(IMAGE_DIR, exist_ok=True)
os.makedirs(VIDEO_DIR, exist_ok=True)


options = Options()
options.headless = False
options.add_argument("-private")

driver = webdriver.Firefox(service=Service(), options=options)
driver.set_page_load_timeout(25)
driver.set_script_timeout(25)

if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow(["post_url", "post_text", "comments"])


def log(msg):
    print(msg, flush=True)

def safe_execute(action):
    for _ in range(MAX_RETRIES_PER_POST):
        try:
            return action()
        except (TimeoutException, WebDriverException, urllib3.exceptions.ReadTimeoutError):
            time.sleep(RETRY_COOLDOWN)
    return None


def safe_open(url):
    driver.get(url)
    time.sleep(6)


def download_video(url):
    log("Downloading video...")
    subprocess.run(
        ["yt-dlp", "-f", "mp4", "-o",
         os.path.join(VIDEO_DIR, "%(id)s.%(ext)s"), url],
        timeout=600,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )


def save_images(post_index):
    log("Downloading images...")
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

        data = driver.execute_async_script("""
            const src = arguments[0];
            const cb = arguments[arguments.length - 1];
            fetch(src).then(r => r.blob()).then(b => {
                const fr = new FileReader();
                fr.onloadend = () => cb(fr.result);
                fr.readAsDataURL(b);
            });
        """, src)

        image_bytes = base64.b64decode(data.split(",")[1])
        with open(img_path, "wb") as f:
            f.write(image_bytes)


def extract_post_text():
    log("Extracting post text...")
    texts = []

    # Expand "See more"
    try:
        see_more = driver.find_elements(
            By.XPATH, "//button[contains(.,'See more')]"
        )
        for btn in see_more:
            driver.execute_script("arguments[0].click();", btn)
            time.sleep(1)
    except:
        pass

    elements = driver.find_elements(
        By.XPATH,
        "//div[contains(@class,'update-components-text')] | "
        "//span[contains(@class,'break-words')]"
    )

    for el in elements:
        t = el.text.strip()
        if t and t not in texts:
            texts.append(t)

    return " ".join(texts).strip()[:5000]


def extract_comments(max_comments=30):
    log("Extracting comments...")
    comments = []

    # Scroll to comments area
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.7);")
    time.sleep(3)

    for _ in range(10):
        # Load more comments
        try:
            buttons = driver.find_elements(
                By.XPATH,
                "//button[contains(.,'Load more comments') or contains(.,'Show more comments')]"
            )
            for btn in buttons:
                driver.execute_script("arguments[0].click();", btn)
                time.sleep(1)
        except:
            pass

        driver.execute_script("window.scrollBy(0, 1200);")
        time.sleep(2)

        elements = driver.find_elements(
            By.XPATH,
            "//span[contains(@class,'comments-comment-item__main-content')] | "
            "//div[contains(@class,'comments-comment-item__content')]"
        )

        for el in elements:
            text = el.text.strip()
            if text and text not in comments:
                comments.append(text)

            if len(comments) >= max_comments:
                return comments[:max_comments]

    return comments[:max_comments]

def save_text_to_csv(url, text, comments):
    comments_joined = " || ".join(comments) if comments else "[NO COMMENTS]"
    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([url, text or "[NO TEXT FOUND]", comments_joined])

with open(INPUT_LINKS_FILE, "r", encoding="utf-8") as f:
    links = [l.strip() for l in f if l.strip()]

total = len(links)
log(f"TOTAL POSTS FOUND: {total}")

for idx, url in enumerate(links, start=1):
    log(f"\nProcessing post {idx}/{total}")
    log(f"URL: {url}")

    safe_open(url)
    soup = BeautifulSoup(driver.page_source, "html.parser")

    if soup.find("video"):
        log("Post type: VIDEO")
        download_video(url)
        continue

    if soup.find("img", src=lambda x: x and "media.licdn.com" in x):
        log("Post type: IMAGE")
        save_images(idx)
        continue

    log("Post type: TEXT")
    post_text = extract_post_text()
    comments = extract_comments(MAX_COMMENTS)
    save_text_to_csv(url, post_text, comments)

    log(f"Saved text + {len(comments)} comments")
    time.sleep(random.uniform(4, 7))

driver.quit()
log("ALL POSTS COMPLETED SUCCESSFULLY")
