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



FIREFOX_PROFILE_PATH = r"C:\Users\lrraw\AppData\Roaming\Mozilla\Firefox\Profiles\X41F8uLF.Profile 2"

URLS = [
    "https://www.youtube.com/watch?v=JrOiJJQnnsM",
"https://www.youtube.com/watch?v=SdfipypqcsM",
"https://www.youtube.com/watch?v=lexgFTZ6Wi4",
"https://www.youtube.com/watch?v=gM5JYzyksOI",
"https://www.youtube.com/watch?v=vUKQHLkgUqQ"
]

PAGE_LOAD_WAIT = 8
EXTENSION_WAIT = 6


ROI_X_MIN = 880
ROI_X_MAX = 1150
ROI_Y_MIN = 900
ROI_Y_MAX = 1080


TARGET_RGB = np.array([0, 183, 90])

COLOR_TOLERANCE = 20   


FALLBACK_X = 1004
FALLBACK_Y = 982
SWEEP_OFFSETS = [-40, 0, 40]

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.15


def find_color_in_roi():
    screenshot = pyautogui.screenshot()
    screen = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    roi = screen[
        ROI_Y_MIN:ROI_Y_MAX,
        ROI_X_MIN:ROI_X_MAX
    ]

   
    roi_rgb = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)

    lower = np.clip(TARGET_RGB - COLOR_TOLERANCE, 0, 255)
    upper = np.clip(TARGET_RGB + COLOR_TOLERANCE, 0, 255)

    mask = cv2.inRange(roi_rgb, lower, upper)

    points = cv2.findNonZero(mask)

    if points is None:
        return None

    avg = np.mean(points, axis=0)[0]
    x, y = int(avg[0]), int(avg[1])

    screen_x = ROI_X_MIN + x
    screen_y = ROI_Y_MIN + y

    return screen_x, screen_y




def safe_click(x, y):
    pyautogui.moveTo(x, y, duration=0.25)
    pyautogui.click()


def sweep_click():
    print("Color not found → fallback sweep")
    for off in SWEEP_OFFSETS:
        safe_click(FALLBACK_X + off, FALLBACK_Y)
        time.sleep(0.4)



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



def main():
    driver = start_firefox()

    try:
        for idx, url in enumerate(URLS, start=1):
            print(f"\n[{idx}/{len(URLS)}] {url}")
            driver.get(url)

            time.sleep(PAGE_LOAD_WAIT)
            driver.switch_to.window(driver.current_window_handle)
            time.sleep(0.5)

            print("Searching target color in ROI...")
            coords = find_color_in_roi()

            if coords:
                print(f"Color hit at {coords}")
                safe_click(*coords)
            else:
                sweep_click()

            print("Waiting for extension...")
            time.sleep(EXTENSION_WAIT)

        print("\nAll URLs done")

    except pyautogui.FailSafeException:
        print("\nFAILSAFE triggered")
    except Exception:
        traceback.print_exc()
    finally:
        # driver.quit()
        print("Completed")



if __name__ == "__main__":
    main()
