import os
import csv
import time
import random
import urllib3

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, WebDriverException

# =========================
# CONFIG
# =========================
FIREFOX_PROFILE_PATH = r"C:\Users\lrraw\AppData\Roaming\Mozilla\Firefox\Profiles\AVtzXYQk.Profile 1"
INPUT_LINKS_FILE = "linkedin_post_links.txt"

BASE_DIR = "linkedin_text_only"
CSV_FILE = os.path.join(BASE_DIR, "text_posts.csv")

MAX_RETRIES_PER_POST = 3
RETRY_COOLDOWN = 6

os.makedirs(BASE_DIR, exist_ok=True)

# =========================
# FIREFOX SETUP (CRITICAL)
# =========================
options = Options()
options.headless = False
options.page_load_strategy = "none"
options.add_argument("-profile")
options.add_argument(FIREFOX_PROFILE_PATH)

driver = webdriver.Firefox(service=Service(), options=options)
driver.set_page_load_timeout(10)
driver.set_script_timeout(10)

# =========================
# CSV INIT
# =========================
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow(["post_url", "post_text"])

# =========================
# SAFE EXECUTOR
# =========================
def safe_execute(action, label="action"):
    for attempt in range(1, MAX_RETRIES_PER_POST + 1):
        try:
            return action()
        except (TimeoutException, WebDriverException, urllib3.exceptions.ReadTimeoutError) as e:
            print(f"⚠️ {label} failed ({attempt}/{MAX_RETRIES_PER_POST})")
            try:
                driver.execute_script("window.stop();")
                driver.get("about:blank")
            except:
                pass
            time.sleep(RETRY_COOLDOWN)
    print(f"❌ {label} skipped")
    return None

# =========================
# SAFE NAVIGATION
# =========================
def safe_open(url):
    def _open():
        driver.get(url)
        time.sleep(3)
        driver.execute_script("window.stop();")
    safe_execute(_open, f"open {url}")

# =========================
# TEXT EXTRACTION (ROBUST)
# =========================
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

def save_text(url, text):
    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([url, text or "[NO TEXT FOUND]"])

# =========================
# MAIN LOOP
# =========================
with open(INPUT_LINKS_FILE, "r", encoding="utf-8") as f:
    links = [l.strip() for l in f if l.strip()]

for idx, url in enumerate(links, start=1):
    print(f"\n📝 Processing {idx}")
    safe_open(url)

    text = extract_post_text()
    save_text(url, text)

    time.sleep(random.uniform(3, 6))

driver.quit()
print("\n✅ TEXT-ONLY SCRAPING COMPLETED")
