import time
from datetime import datetime

import cv2
import numpy as np
import pyautogui

from cv_images import CVImages
from images import Images


class Capturer:
    def __init__(self, base_res, ratio, iterations=3):
        # get capture region
        x, y = base_res.top_left()
        width = height = base_res.cap_dim()

        self.output = []

        previous = datetime.now()
        for i in range(iterations):
            screenshot = pyautogui.screenshot(region=(x, y, width, height))
            screenshot = np.array(screenshot)[:, :, :: -1].copy()

            if ratio != 1:
                height, width, layers = screenshot.shape
                new_height, new_width = round(height / ratio), round(width / ratio)
                screenshot = cv2.resize(screenshot, (new_width, new_height), interpolation=Images.interpolation)

            self.output.append(CVImages(screenshot))

            if i != iterations - 1:
                time.sleep(max(0.5 - (datetime.now() - previous).total_seconds(), 0))
                previous = datetime.now()