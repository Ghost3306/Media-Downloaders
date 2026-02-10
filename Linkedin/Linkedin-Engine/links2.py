from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
import time
import threading
import sys

FIREFOX_PROFILE_PATH = r"C:\Users\lrraw\AppData\Roaming\Mozilla\Firefox\Profiles\X41F8uLF.Profile 2"
OUTPUT_FILE = "linkedin_post_links.txt"

stop_flag = False
post_links = set()

def listen_for_stop():
    global stop_flag
    while True:
        user_input = input().strip()
        if user_input == "0":
            stop_flag = True
            print("\n  Finishing capture...")
            break

options = Options()
options.headless = False
options.add_argument("-profile")
options.add_argument(FIREFOX_PROFILE_PATH)

driver = webdriver.Firefox(service=Service(), options=options)
driver.get("https://www.linkedin.com/feed/")
time.sleep(8)

print("\nMANUAL MODE ENABLED")
print("Scroll/search manually in browser")
print("Type 0 anytime and press ENTER to stop\n")

threading.Thread(target=listen_for_stop, daemon=True).start()

try:
    while not stop_flag:
        posts = driver.find_elements(
            By.XPATH,
            "//div[contains(@data-urn, 'urn:li:activity:')]"
        )

        new_count = 0
        for post in posts:
            urn = post.get_attribute("data-urn")
            if urn and "activity" in urn:
                post_id = urn.split(":")[-1]
                link = f"https://www.linkedin.com/feed/update/urn:li:activity:{post_id}"
                if link not in post_links:
                    post_links.add(link)
                    new_count += 1

        if new_count:
            print(f"New links added: {new_count} | Total: {len(post_links)}")

        time.sleep(3)  

finally:
    driver.quit()

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    for link in sorted(post_links):
        f.write(link + "\n")

print(f"\nFINAL COUNT: {len(post_links)} links")
print(f"Saved to {OUTPUT_FILE}")
