import numpy as np
import pyautogui

from cvimage import CVImage


# TODO move to util?
def screen_capture() -> CVImage:
    screenshot = pyautogui.screenshot()
    screenshot = np.array(screenshot)[:, :, :: -1].copy()
    return CVImage(screenshot)