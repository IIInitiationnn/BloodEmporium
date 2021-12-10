import time
from datetime import datetime

import cv2
import numpy as np
import pyautogui

from config import Config
from cv_images import CVImages

class Capturer:
    def __init__(self, ratio, iterations=3):
        config = Config()

        # get capture region
        x, y = config.top_left()
        width, height = config.width(), config.height()

        self.output = []

        previous = datetime.now()
        for i in range(iterations):
            screenshot = pyautogui.screenshot(region=(x, y, width, height))
            screenshot = np.array(screenshot)[:, :, :: -1].copy()

            if ratio != 1:
                height, width, layers = screenshot.shape
                new_height, new_width = round(height / ratio), round(width / ratio)
                screenshot = cv2.resize(screenshot, (new_width, new_height))

            self.output.append(CVImages(screenshot))

            if i != iterations - 1:
                time.sleep(max(0.5 - (datetime.now() - previous).total_seconds(), 0))
                previous = datetime.now()