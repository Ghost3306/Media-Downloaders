# import time
# import pyautogui
# import cv2
# import numpy as np

# from selenium import webdriver
# from selenium.webdriver.firefox.service import Service
# from selenium.webdriver.firefox.options import Options
# from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
# from webdriver_manager.firefox import GeckoDriverManager

# # ================= CONFIG =================

# FIREFOX_PROFILE_PATH = r"C:\Users\lrraw\AppData\Roaming\Mozilla\Firefox\Profiles\X41F8uLF.Profile 2"

# URLS = [
#     "https://youtu.be/rkW_0_ZDDw0?si=wg9ksoVpqwzXbFAl",
#     "https://youtu.be/TmXL3Ejl9II?si=ipxAAGTspZoHSDgy",
#     "https://youtu.be/OK8Vu12zN8A?si=Q-KOyBzga77OG6Jd",
#     "https://youtu.be/MVeeRCRw5kM?si=MSEIfsByAMewYiLE",
#     "https://youtu.be/QMKPvfNB6l0?si=VgHM91sK1Mur8AUr",
#     "https://youtu.be/IolHQoQso0c?si=fqx7-8tpzmELfqDe",
#     "https://youtu.be/OMpVji16f2E?si=NpHiPQ-110V4V83J",
# ]

# PAGE_LOAD_WAIT = 8
# EXTENSION_WAIT = 5

# MATCH_CONFIDENCE = 0.3
# RETRIES = 10
# RETRY_DELAY = 0.4

# pyautogui.FAILSAFE = True

# # ================= IMAGE MATCH =================

# def calculate_coords(confidence=MATCH_CONFIDENCE):
   

#     screenshot = pyautogui.screenshot()
#     screen = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

#     template = cv2.imread("target.png", cv2.IMREAD_GRAYSCALE)
#     if template is None:
#         raise FileNotFoundError("target.png not found")

#     screen_gray = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)

#     h, w = template.shape[:2]

#     result = cv2.matchTemplate(screen_gray, template, cv2.TM_CCOEFF_NORMED)
#     _, max_val, _, max_loc = cv2.minMaxLoc(result)

#     print(f"Match confidence: {max_val:.3f}")

#     if max_val < confidence:
#         return None

#     x, y = max_loc

#     screen_x = x + w // 2
#     screen_y = y + h // 2

#     return screen_x, screen_y


# def get_extension_coords():
#     for _ in range(RETRIES):
#         coords = calculate_coords()
#         if coords:
#             return coords
#         time.sleep(RETRY_DELAY)
#     return None

# # ================= FIREFOX SETUP =================

# profile = FirefoxProfile(FIREFOX_PROFILE_PATH)
# options = Options()
# options.profile = profile

# driver = webdriver.Firefox(
#     service=Service(GeckoDriverManager().install()),
#     options=options
# )

# driver.maximize_window()
# time.sleep(2)

# # ================= MAIN LOOP =================

# for index, url in enumerate(URLS, start=1):
#     print(f"\nProcessing {index}/{len(URLS)}")
#     print("Opening:", url)

#     driver.get(url)
#     time.sleep(PAGE_LOAD_WAIT)

#     # Ensure Firefox focus
#     driver.switch_to.window(driver.current_window_handle)
#     time.sleep(0.6)


    
#     EXTENSION_X = 1004
#     EXTENSION_Y = 982

#     print("Clicking at:", EXTENSION_X, EXTENSION_Y)

#     pyautogui.moveTo(EXTENSION_X, EXTENSION_Y, duration=0.3)
#     pyautogui.click()

#     print("Waiting for extension to finish...")
#     time.sleep(EXTENSION_WAIT)

# print("\n✅ All URLs processed")
import time
import pyautogui
import cv2
import numpy as np
import traceback

from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from webdriver_manager.firefox import GeckoDriverManager

# ================= CONFIG =================

FIREFOX_PROFILE_PATH = r"C:\Users\lrraw\AppData\Roaming\Mozilla\Firefox\Profiles\X41F8uLF.Profile 2"

URLS = [
    "https://youtu.be/rkW_0_ZDDw0?si=wg9ksoVpqwzXbFAl",
    "https://youtu.be/TmXL3Ejl9II?si=ipxAAGTspZoHSDgy",
    "https://youtu.be/OK8Vu12zN8A?si=Q-KOyBzga77OG6Jd",
    "https://youtu.be/MVeeRCRw5kM?si=MSEIfsByAMewYiLE",
    "https://youtu.be/QMKPvfNB6l0?si=VgHM91sK1Mur8AUr",
    "https://youtu.be/IolHQoQso0c?si=fqx7-8tpzmELfqDe",
    "https://youtu.be/OMpVji16f2E?si=NpHiPQ-110V4V83J",
]

PAGE_LOAD_WAIT = 8
EXTENSION_WAIT = 6

MATCH_CONFIDENCE = 0.30
IMAGE_RETRIES = 8
RETRY_DELAY = 0.4

# ===== ROI (from your real data) =====
ROI_X_MIN = 920
ROI_X_MAX = 1090
ROI_Y_MIN = 950
ROI_Y_MAX = 1020

# Fallback (center you calculated)
FALLBACK_X = 1004
FALLBACK_Y = 982
SWEEP_OFFSETS = [-40, 0, 40]

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.15

# ================= IMAGE MATCH (ROI ONLY) =================

def find_button_in_roi(confidence=MATCH_CONFIDENCE):
    try:
        screenshot = pyautogui.screenshot()
        screen = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        screen_gray = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)

        roi = screen_gray[
            ROI_Y_MIN:ROI_Y_MAX,
            ROI_X_MIN:ROI_X_MAX
        ]

        template = cv2.imread("target.png", cv2.IMREAD_GRAYSCALE)
        if template is None:
            print("⚠ target.png missing")
            return None

        h, w = template.shape[:2]
        result = cv2.matchTemplate(roi, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)

        print(f"🔍 ROI match confidence: {max_val:.3f}")

        if max_val < confidence:
            return None

        x, y = max_loc

        screen_x = ROI_X_MIN + x + w // 2
        screen_y = ROI_Y_MIN + y + h // 2

        return screen_x, screen_y

    except Exception as e:
        print("⚠ ROI image error:", e)
        return None


def get_button_coords():
    for _ in range(IMAGE_RETRIES):
        coords = find_button_in_roi()
        if coords:
            return coords
        time.sleep(RETRY_DELAY)
    return None

# ================= CLICK LOGIC =================

def safe_click(x, y):
    pyautogui.moveTo(x, y, duration=0.25)
    pyautogui.click()


def sweep_click():
    print("🧭 Using sweep fallback")
    for offset in SWEEP_OFFSETS:
        safe_click(FALLBACK_X + offset, FALLBACK_Y)
        time.sleep(0.4)

# ================= FIREFOX =================

def start_firefox():
    profile = FirefoxProfile(FIREFOX_PROFILE_PATH)
    options = Options()
    options.profile = profile

    driver = webdriver.Firefox(
        service=Service(GeckoDriverManager().install()),
        options=options
    )

    driver.maximize_window()
    time.sleep(2)
    return driver

# ================= MAIN =================

def main():
    driver = start_firefox()

    try:
        for idx, url in enumerate(URLS, start=1):
            print(f"\n📺 [{idx}/{len(URLS)}] {url}")
            driver.get(url)

            time.sleep(PAGE_LOAD_WAIT)
            driver.switch_to.window(driver.current_window_handle)
            time.sleep(0.5)

            print("🔎 Searching download button in ROI...")
            coords = get_button_coords()

            if coords:
                print("✅ Image hit:", coords)
                safe_click(*coords)
            else:
                print("⚠ Image failed → fallback sweep")
                sweep_click()

            time.sleep(EXTENSION_WAIT)

        print("\n✅ ALL URLS DONE")

    except pyautogui.FailSafeException:
        print("\n🛑 FAILSAFE triggered")
    except Exception:
        traceback.print_exc()
    finally:
        # driver.quit()
        print("🧹 Firefox closed")

# ================= ENTRY =================

if __name__ == "__main__":
    main()
