import time
import cv2
import numpy as np
import pyautogui

IMAGE = "target.png"
WAIT_TIME = 4        # seconds
CONFIDENCE = 0.85

print(f"Waiting {WAIT_TIME} seconds for screen to load...")
time.sleep(WAIT_TIME)

# Load template
template = cv2.imread(IMAGE, cv2.IMREAD_GRAYSCALE)
if template is None:
    raise FileNotFoundError("target.png not found")

w, h = template.shape[::-1]

# Take ONE screenshot
screenshot = pyautogui.screenshot()
screen = cv2.cvtColor(np.array(screenshot), cv2.COLOR_BGR2GRAY)

# Template matching
result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

if max_val >= CONFIDENCE:
    center_x = max_loc[0] + w // 2
    center_y = max_loc[1] + h // 2
    print(f"FOUND ✔  X={center_x}, Y={center_y}, confidence={max_val:.2f}")
else:
    print(f"NOT FOUND ✖  best confidence={max_val:.2f}")
