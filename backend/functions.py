import math
import os
import time
from datetime import datetime
from typing import Tuple, List

import cv2
import numpy as np
import pyautogui

from backend.paths import Path
from backend.resolution import Resolution
from backend.shapes import UnmatchedNode, Position, Line, Connection
from cvimage import CVImage
from image import Image


def screen_capture(base_res: Resolution, ratio, iterations=3, interval=0.5, crop=True) -> List[CVImage]:
    """
    Takes several images with some intervening interval.

    Args:
        base_res: the base display resolution
        ratio: the factor by which to downscale the base resolution for the final image (saves computation)
        iterations: the number of images to take
        interval: the number of seconds between each image
        crop: whether to crop the image

    Returns:
        images: a list of images
    """

    # get capture region
    x, y = base_res.top_left()
    width = height = base_res.cap_dim()

    images = []

    previous = datetime.now()
    for i in range(iterations):
        if crop:
            screenshot = pyautogui.screenshot(region=(x, y, width, height))
        else:
            screenshot = pyautogui.screenshot()
        screenshot = np.array(screenshot)[:, :, :: -1].copy()

        if ratio != 1:
            height, width, layers = screenshot.shape
            new_height, new_width = round(height / ratio), round(width / ratio)
            screenshot = cv2.resize(screenshot, (new_width, new_height), interpolation=Image.interpolation)

        images.append(CVImage(screenshot))

        if i != iterations - 1:
            time.sleep(max(interval - (datetime.now() - previous).total_seconds(), 0))
            previous = datetime.now()
    return images

def match_lines(cv_images: [CVImage], res, circles, threshold=30):
    """

    Args:
        cv_images:
        res:
        circles:
        threshold:

    Returns:

    """
    edge_images = []
    raw_lines = []
    validated1_output = []
    for i, cv_image in enumerate(cv_images):
        image_filtered = cv_image.get_red()
        ratio = 3
        image_filtered = cv2.bilateralFilter(image_filtered, ratio, 110, 110)
        image_filtered = cv2.convertScaleAbs(image_filtered, alpha=1.3, beta=50)
        edges = cv2.Canny(image_filtered, res.canny_min(), res.canny_max())
        edge_images.append(edges)

        for circle in circles:
            # remove the node's circle from the edges graph (reduces noise)
            cv2.circle(edges, (circle.x(), circle.y()), circle.radius + Resolution.additional_radius(circle.radius),
                       0, thickness=-1)

        lines = cv2.HoughLinesP(edges, rho=1, theta=np.pi / 180, threshold=threshold,
                                minLineLength=res.line_length(), maxLineGap=res.line_length())

        output = []
        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                output.append(Line(Position(x1, y1), Position(x2, y2)))
        raw_lines.append(output)

        # validate lines by removing those that do not join two circles; add the connected nodes to edge list
        connections = []
        for line in output:
            connection = line.get_endpoints(circles, res)
            if connection is not None and not Connection.list_contains(connections, connection):
                connections.append(connection)
        validated1_output.extend(connections)

    # validate lines across multiple images: lines must exist in the majority of images to be valid
    validated2_output = []
    while len(validated1_output) > 0:
        check = validated1_output.pop(0)
        connections = [check]
        for connection in validated1_output.copy():
            if Connection.is_equal(check, connection):
                validated1_output.remove(connection)
                connections.append(connection)

        if len(connections) > math.floor(len(cv_images) / 2):
            validated2_output.append(check)
    return edge_images, raw_lines, validated2_output