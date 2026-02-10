from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

INSTAGRAM_URL = "https://www.instagram.com/reel/DT0oRaDDbpn/"

options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
options.add_argument("--disable-blink-features=AutomationControlled")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

driver.get("http://localhost:9000")
time.sleep(3)

input_box = driver.find_element(By.TAG_NAME, "input")
input_box.send_keys(INSTAGRAM_URL)
input_box.send_keys(Keys.ENTER)

time.sleep(15)  # wait for download
