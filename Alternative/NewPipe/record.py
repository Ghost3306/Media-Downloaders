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
OUTPUT_FILE = "actions.json"
CLICK_XPATH = "//button[@id='submit']"  # 👈 the ONE thing you want to click
WAIT_TIME = 10

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

wait = WebDriverWait(driver, WAIT_TIME)

# ==============================
# SAFE SINGLE CLICK
# ==============================
try:
    element = wait.until(
        EC.presence_of_element_located((By.XPATH, CLICK_XPATH))
    )

    driver.execute_script(
        "arguments[0].scrollIntoView({block: 'center'});",
        element
    )
    time.sleep(0.5)

    try:
        element.click()
    except ElementNotInteractableException:
        driver.execute_script("arguments[0].click();", element)

    print("✅ Click successful")

except Exception as e:
    print(f"❌ Click failed: {e}")