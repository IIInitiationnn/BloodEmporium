import cv2
import numpy as np
import pyautogui

from backend.resolution import Resolution
from cvimage import CVImage
from image import Image


def screen_capture(base_res: Resolution, ratio, interval=0.5, crop=True) -> CVImage:
    """
    Takes several images with some intervening interval.

    Args:
        base_res: the base display resolution
        ratio: the factor by which to downscale the base resolution for the final image (saves computation)
        interval: the number of seconds between each image
        crop: whether to crop the image

    Returns:
        images: a list of images
    """

    if crop:
        # get capture region
        x, y = base_res.top_left()
        width = height = base_res.cap_dim()
        screenshot = pyautogui.screenshot(region=(x, y, width, height))
    else:
        screenshot = pyautogui.screenshot()
    screenshot = np.array(screenshot)[:, :, :: -1].copy()

    if ratio != 1:
        height, width, layers = screenshot.shape
        new_height, new_width = round(height / ratio), round(width / ratio)
        screenshot = cv2.resize(screenshot, (new_width, new_height), interpolation=Image.interpolation)

    return CVImage(screenshot)