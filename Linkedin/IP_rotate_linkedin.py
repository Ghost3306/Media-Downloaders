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
SCROLL_COUNT = 3
OUTPUT_FILE = "linkedin_post_links.txt"

# ==============================
# SMARTPROXY LIST
# ==============================
PROXIES = [
    ("142.111.48.253", 7030, "oqzdcrtg", "fjm6xic73k79"),
    ("23.95.150.145", 6114, "oqzdcrtg", "fjm6xic73k79"),
    ("198.23.239.134", 6540, "oqzdcrtg", "fjm6xic73k79"),
    ("107.172.163.27", 6543, "oqzdcrtg", "fjm6xic73k79"),
    ("198.105.121.200", 6462, "oqzdcrtg", "fjm6xic73k79"),
    ("64.137.96.74", 6641, "oqzdcrtg", "fjm6xic73k79"),
    ("84.247.60.125", 6095, "oqzdcrtg", "fjm6xic73k79"),
    ("216.10.27.159", 6837, "oqzdcrtg", "fjm6xic73k79"),
    ("23.26.71.145", 5628, "oqzdcrtg", "fjm6xic73k79"),
    ("23.27.208.120", 5830, "oqzdcrtg", "fjm6xic73k79"),
]

proxy_host, proxy_port, proxy_user, proxy_pass = random.choice(PROXIES)

# ==============================
# FIREFOX SETUP WITH PROXY
# ==============================
options = Options()
options.headless = False
options.add_argument("-profile")
options.add_argument(FIREFOX_PROFILE_PATH)

# --- proxy settings ---
options.set_preference("network.proxy.type", 1)
options.set_preference("network.proxy.http", proxy_host)
options.set_preference("network.proxy.http_port", proxy_port)
options.set_preference("network.proxy.ssl", proxy_host)
options.set_preference("network.proxy.ssl_port", proxy_port)
options.set_preference("network.proxy.socks_remote_dns", True)

# --- proxy auth ---
options.set_preference("network.proxy.username", proxy_user)
options.set_preference("network.proxy.password", proxy_pass)

driver = webdriver.Firefox(
    service=Service(),
    options=options
)

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
        if urn:
            post_links.add(f"https://www.linkedin.com/feed/update/{urn}")

    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(random.uniform(2.5, 4))

driver.quit()

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    for link in sorted(post_links):
        f.write(link + "\n")

print(f"\nExtracted {len(post_links)} post links")
print(f"Saved to {OUTPUT_FILE}")
