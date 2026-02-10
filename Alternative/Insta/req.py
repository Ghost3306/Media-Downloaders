from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

INSTAGRAM_URL = "https://www.instagram.com/reel/DT0oRaDDbpn/?igsh=MTNodWk5Y3luYW5neg=="

options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
options.add_argument("--disable-blink-features=AutomationControlled")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

# 1️⃣ Open cobalt.tools
driver.get("https://cobalt.tools")
time.sleep(4)

# 2️⃣ Find input box & paste URL
input_box = driver.find_element(By.TAG_NAME, "input")
input_box.clear()
input_box.send_keys(INSTAGRAM_URL)
time.sleep(1)

# 3️⃣ Press Enter (same as clicking Download)
input_box.send_keys(Keys.ENTER)

# 4️⃣ Wait for processing
time.sleep(10)

print("✔ Download triggered in browser")

# Keep browser open so you can see / download
input("Press Enter to close...")
driver.quit()
