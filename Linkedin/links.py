from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
import time
import random
import urllib.parse

# ==============================
# CONFIG
# ==============================
FIREFOX_PROFILE_PATH = r"C:\Users\lrraw\AppData\Roaming\Mozilla\Firefox\Profiles\AVtzXYQk.Profile 1"
KEYWORD = input("Enter Keyword : ")
SCROLL_COUNT = 25
OUTPUT_FILE = "linkedin_post_links.txt"

# ==============================
# FIREFOX SETUP
# ==============================
options = Options()
options.headless = False
options.add_argument("-profile")
options.add_argument(FIREFOX_PROFILE_PATH)

driver = webdriver.Firefox(service=Service(), options=options)

# ==============================
# OPEN POSTS SEARCH
# ==============================
encoded = urllib.parse.quote(KEYWORD)
url = f"https://www.linkedin.com/search/results/content/?keywords={encoded}"
driver.get(url)
time.sleep(6)


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


with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    for link in sorted(post_links):
        f.write(link + "\n")

print(f"\nExtracted {len(post_links)} REAL post links")
print(f"Saved to {OUTPUT_FILE}")
