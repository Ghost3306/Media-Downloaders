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

MATCH_CONFIDENCE = 0.45
LOW_CONFIDENCE_THRESHOLD = 0.70

IMAGE_RETRIES = 6
RETRY_DELAY = 0.4

# ROI (derived from your real data)
ROI_X_MIN = 880
ROI_X_MAX = 1150
ROI_Y_MIN = 900
ROI_Y_MAX = 1080

# Fallback center (your averaged value)
FALLBACK_X = 1004
FALLBACK_Y = 982
SWEEP_OFFSETS = [-40, 0, 40]

# Micro verification offsets
MICRO_OFFSET = 5
MICRO_CLICK_DELAY = 0.35

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.15

# ================= IMAGE MATCH =================

def find_button_in_roi(confidence_threshold=MATCH_CONFIDENCE):
    screenshot = pyautogui.screenshot()
    screen_gray = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY)

    roi = screen_gray[
        ROI_Y_MIN:ROI_Y_MAX,
        ROI_X_MIN:ROI_X_MAX
    ]

    template = cv2.imread("target.png", cv2.IMREAD_GRAYSCALE)
    if template is None:
        print("⚠ target.png not found")
        return None

    rh, rw = roi.shape[:2]
    th, tw = template.shape[:2]

    # HARD SAFETY CHECK
    if rh < th or rw < tw:
        print(f"⚠ ROI ({rw}x{rh}) smaller than template ({tw}x{th})")
        return None

    result = cv2.matchTemplate(roi, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)

    print(f"🔍 ROI match confidence: {max_val:.3f}")

    if max_val < confidence_threshold:
        return None

    x, y = max_loc
    screen_x = ROI_X_MIN + x + tw // 2
    screen_y = ROI_Y_MIN + y + th // 2

    return screen_x, screen_y, max_val


def get_button_coords():
    for _ in range(IMAGE_RETRIES):
        result = find_button_in_roi()
        if result:
            return result
        time.sleep(RETRY_DELAY)
    return None

# ================= CLICK LOGIC =================

def safe_click(x, y):
    pyautogui.moveTo(x, y, duration=0.25)
    pyautogui.click()


def micro_verify_click(x, y):
    print("🟡 Low confidence → micro left/right verification")
    for off in [0, -MICRO_OFFSET, MICRO_OFFSET]:
        pyautogui.moveTo(x + off, y, duration=0.15)
        pyautogui.click()
        time.sleep(MICRO_CLICK_DELAY)


def sweep_click():
    print("🧭 Image failed → fallback sweep")
    for off in SWEEP_OFFSETS:
        safe_click(FALLBACK_X + off, FALLBACK_Y)
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
            result = get_button_coords()

            if result:
                x, y, conf = result
                print(f"✅ Image hit: ({x}, {y}) | conf={conf:.3f}")

                if conf < LOW_CONFIDENCE_THRESHOLD:
                    micro_verify_click(x, y)
                else:
                    safe_click(x, y)
            else:
                sweep_click()

            print("⏳ Waiting for extension...")
            time.sleep(EXTENSION_WAIT)

        print("\n✅ ALL URLS DONE")

    except pyautogui.FailSafeException:
        print("\n🛑 FAILSAFE triggered (mouse to corner)")
    except Exception:
        traceback.print_exc()
    finally:
        #driver.quit()
        print("🧹 Firefox closed safely")

# ================= ENTRY =================

if __name__ == "__main__":
    main()
