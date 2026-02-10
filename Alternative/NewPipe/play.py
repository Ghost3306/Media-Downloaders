import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementNotInteractableException
from webdriver_manager.firefox import GeckoDriverManager
# ==============================
# CONFIG
# ==============================
FIREFOX_PROFILE_PATH = r"C:\Users\lrraw\AppData\Roaming\Mozilla\Firefox\Profiles\X41F8uLF.Profile 2"
START_URL = "https://www.youtube.com/watch?v=QWvi520xCZg"
ACTIONS_FILE = "actions.json"
REPEAT_COUNT = 1
DEFAULT_WAIT = 5

# ==============================
# FIREFOX WITH PROFILE
# ==============================
profile = FirefoxProfile(FIREFOX_PROFILE_PATH)

options = Options()
options.profile = profile

driver = webdriver.Firefox(
    service=Service(GeckoDriverManager().install()),
    options=options
)

driver.get(START_URL)

wait = WebDriverWait(driver, DEFAULT_WAIT)

# ==============================
# SAFE CLICK FUNCTION
# ==============================
def safe_click(driver, xpath):
    try:
        element = wait.until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )

        # Scroll element into view
        driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});",
            element
        )
        time.sleep(0.4)

        try:
            # Normal click
            element.click()
        except ElementNotInteractableException:
            # JS click fallback (for overlays like YouTube)
            driver.execute_script("arguments[0].click();", element)

    except Exception as e:
        print(f"⚠️ Click skipped for [{xpath}] → {e}")

# ==============================
# SAFE INPUT FUNCTION
# ==============================
def safe_input(driver, xpath, value):
    try:
        element = wait.until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )

        driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});",
            element
        )
        time.sleep(0.4)

        element.clear()
        element.send_keys(value)

    except Exception as e:
        print(f"⚠️ Input skipped for [{xpath}] → {e}")

# ==============================
# LOAD ACTIONS
# ==============================
with open(ACTIONS_FILE, "r", encoding="utf-8") as f:
    actions = json.load(f)

print("\n🔁 Starting replay\n")

# ==============================
# PLAY ACTIONS
# ==============================
for cycle in range(REPEAT_COUNT):
    print(f"▶ Cycle {cycle + 1}")

    for act in actions:
        if act["type"] == "click":
            safe_click(driver, act["xpath"])
            time.sleep(1)

        elif act["type"] == "input":
            safe_input(driver, act["xpath"], act["value"])
            time.sleep(1)

print("\n✅ Replay completed")

# ==============================
# CLEANUP (OPTIONAL)
# ==============================
# driver.quit()