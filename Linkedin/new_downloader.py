import os
import csv
import time
import random
import subprocess
import urllib3
import base64
import re



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
MAX_COMMENTS = 30 #change according

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

def to_mobile_url(url):
    if "linkedin.com" in url and "m.linkedin.com" not in url:
        return url.replace("www.linkedin.com", "www.linkedin.com")
    return url


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
    texts = []

    soup = BeautifulSoup(driver.page_source, "html.parser")
    for p in soup.find_all("p"):
        t = p.get_text(strip=True)
        if t and len(t) > 30:
            texts.append(t)

    return " ".join(dict.fromkeys(texts))[:5000]

BLOCK_PHRASES = [
    "by clicking continue to join",
    "user agreement",
    "privacy policy",
    "cookie policy",
    "to view or add a comment",
    "sign in",
    "don’t have the app",
    "get it in the microsoft store",
    "create your free account",
    "join linkedin",
    "continue your search"
]

def clean_text(text):
    text = re.sub(r"\s+", " ", text).strip()

    patterns = [
        r"By clicking Continue to join.*?Cookie Policy\.?",
        r"To view or add a comment.*",
        r"Don’t have the app\?.*",
        r"Create your free account.*",
    ]

    for pattern in patterns:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)

    return text.strip()

def is_valid_text(text):
    lower = text.lower()

    for phrase in BLOCK_PHRASES:
        if phrase in lower:
            return False

    if len(text) < 20:
        return False

    policy_words = ["policy", "agreement", "sign", "account"]
    if sum(word in lower for word in policy_words) >= 2:
        return False

    return True






def extract_comments(max_comments=30):
    comments = []

    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)

    soup = BeautifulSoup(driver.page_source, "html.parser")

    for p in soup.find_all("p"):
        raw_text = p.get_text(" ", strip=True)
        cleaned = clean_text(raw_text)

        if cleaned and is_valid_text(cleaned) and cleaned not in comments:
            comments.append(cleaned)

        if len(comments) >= max_comments:
            break

    return comments[:max_comments]

def save_to_csv(url, text, comments):
    joined = " || ".join(comments) if comments else "[COMMENTS NOT PUBLIC]"
    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([url, text or "[NO TEXT FOUND]", joined])


def clean_comments(comments):
    blocked_phrases = [
        "agree & join linkedin",
        "join linkedin",
        "sign in",
        "never miss a beat",
        "get it in the microsoft store",
        "new to linkedin",
        "by clicking",
        "user agreement",
        "privacy policy",
        "cookie policy",
        "followers",
        "looking to create a page",
        "continue to join",
        "create your free account",
        "don’t have the app",
        "don't have the app",
        "install the app",
        "To view or add a comment,sign in Don’t have the app? Get it in the Microsoft Store. Create your free account or sign in to continue your search"
    ]

    cleaned = []

    for c in comments:
        c_lower = c.lower()

      
        if any(bad in c_lower for bad in blocked_phrases):
            continue

       
        if "followers" in c_lower:
            continue

     
        if len(c.strip()) < 8:
            continue

        cleaned.append(c.strip())

    return cleaned


with open(INPUT_LINKS_FILE, "r", encoding="utf-8") as f:
    links = [l.strip() for l in f if l.strip()]

log(f"Total Posts: {len(links)}")

for idx, url in enumerate(links, 1):
    log(f"\nProcessing post {idx}")

    mobile_url = to_mobile_url(url)
    log(f"URL: {mobile_url}")

    safe_open(mobile_url)
    soup = BeautifulSoup(driver.page_source, "html.parser")

    # VIDEO
    if soup.find("video"):
        log("Video detected")
        download_video(mobile_url)
        

    # IMAGE
    if soup.find("img", src=lambda x: x and "media.licdn.com" in x):
        log("Image detected")
        save_images(idx)
        
    # TEXT + COMMENTS
    post_text = extract_post_text()
    comments = clean_comments(extract_comments(MAX_COMMENTS))


    log(f"Post text length: {len(post_text)}")
    log(f"Comments scraped: {len(comments)}")

    save_to_csv(mobile_url, post_text, comments)


    time.sleep(random.uniform(4, 7))

driver.quit()
log("Successful")
