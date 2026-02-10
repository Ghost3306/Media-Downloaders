import random
import time
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service

FIREFOX_PROFILE_PATH = r"C:\Users\lrraw\AppData\Roaming\Mozilla\Firefox\Profiles\WqByBQr9.Profile 2"
OUTPUT_FILE = "linkedin_post_links2.txt"

PROXIES = [
    ("dc.oxylabs.io", 8001),
    ("dc.oxylabs.io", 8002),
    ("dc.oxylabs.io", 8003),
    ("dc.oxylabs.io", 8004),
    ("dc.oxylabs.io", 8005),
    None  
]

selected_proxy = random.choice(PROXIES)


options = Options()
options.headless = False
options.add_argument("-profile")
options.add_argument(FIREFOX_PROFILE_PATH)


if selected_proxy:
    proxy_host, proxy_port = selected_proxy
    print(f"[INFO] Using proxy: {proxy_host}:{proxy_port}")

    options.set_preference("network.proxy.type", 1)
    options.set_preference("network.proxy.http", proxy_host)
    options.set_preference("network.proxy.http_port", proxy_port)
    options.set_preference("network.proxy.ssl", proxy_host)
    options.set_preference("network.proxy.ssl_port", proxy_port)
    options.set_preference("network.proxy.ftp", proxy_host)
    options.set_preference("network.proxy.ftp_port", proxy_port)
    options.set_preference("network.proxy.socks_remote_dns", True)
else:
    print("[INFO] Running without proxy")
    options.set_preference("network.proxy.type", 0)


driver = webdriver.Firefox(service=Service(), options=options)

driver.get("https://www.linkedin.com/feed/")
time.sleep(8)

print("\n🔹 MANUAL MODE ENABLED")
print("Search & scroll manually in the browser")
print("Type 0 here and press ENTER to stop & save\n")

post_links = set()

while True:
    posts = driver.find_elements(
        By.XPATH,
        "//div[contains(@data-urn, 'urn:li:activity:')]"
    )

    for post in posts:
        urn = post.get_attribute("data-urn")
        if urn and "activity" in urn:
            post_id = urn.split(":")[-1]
            link = f"https://www.linkedin.com/feed/update/urn:li:activity:{post_id}"
            post_links.add(link)

    print(f"Collected so far: {len(post_links)} links")

    time.sleep(4)

    user_input = input("Enter 0 to stop (or press ENTER to continue): ").strip()
    if user_input == "0":
        break

try:
    driver.quit()
except:
    pass

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    for link in sorted(post_links):
        f.write(link + "\n")

print(f"\n✅ FINAL COUNT: {len(post_links)} post links")
print(f"📁 Saved to {OUTPUT_FILE}")
