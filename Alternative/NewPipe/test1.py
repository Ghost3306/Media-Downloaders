import time
import pyautogui
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from webdriver_manager.firefox import GeckoDriverManager

# ==============================
# CONFIG
# ==============================
FIREFOX_PROFILE_PATH = r"C:\Users\lrraw\AppData\Roaming\Mozilla\Firefox\Profiles\X41F8uLF.Profile 2"
START_URL = "https://www.youtube.com/watch?v=QWvi520xCZg"


EXTENSION_X = 1018
EXTENSION_Y = 990

# ==============================
# OPEN FIREFOX WITH PROFILE
# ==============================
profile = FirefoxProfile(FIREFOX_PROFILE_PATH)

options = Options()
options.profile = profile

driver = webdriver.Firefox(
    service=Service(GeckoDriverManager().install()),
    options=options
)

driver.maximize_window()
driver.get(START_URL)

print("⏳ Waiting for page to fully load...")
time.sleep(8)

# ==============================
# CLICK EXTENSION BUTTON
# ==============================
print("🖱 Clicking extension button...")
pyautogui.moveTo(EXTENSION_X, EXTENSION_Y, duration=0.3)
pyautogui.click()

print("✅ Extension button clicked")

# ==============================
# OPTIONAL: WAIT / CLOSE
# ==============================
time.sleep(5)
# driver.quit()
