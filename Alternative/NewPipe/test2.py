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

URLS = [
    "https://youtu.be/Qt1G4wP9iGk?si=0OMosTUp9sxvVLz-",
    ""
    "",
    "https://youtu.be/mlDI2hovd14?si=OkG8EV7zgs3pv5sl",
]

# 🔴 EXTENSION BUTTON COORDINATES
EXTENSION_X = 1021
EXTENSION_Y = 983

PAGE_LOAD_WAIT = 8     
EXTENSION_WAIT = 5      

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

# ==============================
# PROCESS EACH URL (SAME TAB)
# ==============================
for index, url in enumerate(URLS, start=1):
    print(f"\nProcessing {index}/{len(URLS)}")
    print("Opening:", url)

    driver.get(url)

    print("Waiting for page to load...")
    time.sleep(PAGE_LOAD_WAIT)

    print("Clicking extension button...")
    pyautogui.moveTo(EXTENSION_X, EXTENSION_Y, duration=0.3)
    pyautogui.click()

    print("Waiting for extension to finish...")
    time.sleep(EXTENSION_WAIT)

print("\nAll URLs processed successfully")

# ==============================
# CLEANUP (OPTIONAL)
# ==============================
# driver.quit()
