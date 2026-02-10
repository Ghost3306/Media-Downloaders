import cv2
import numpy as np
import pyautogui
import time
time.sleep(5)
screen = pyautogui.screenshot()
screen = cv2.cvtColor(np.array(screen), cv2.COLOR_RGB2BGR)

template = cv2.imread("target.png")
result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)

min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

h, w = template.shape[:2]
x, y = max_loc

print("Coords:", x, y, w, h)
