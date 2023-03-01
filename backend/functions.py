import math
import os
import time
from datetime import datetime
from typing import Tuple, List

import cv2
import numpy as np
import pyautogui

from backend.matcher import Matcher
from backend.paths import Path
from backend.resolution import Resolution
from backend.shapes import Circle, Position, Line, Connection
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

def match_origin(cv_image: CVImage, res: Resolution) -> Tuple[Circle, str, np.ndarray]:
    """
    Finds the position and type of origin from the image.

    Args:
        cv_image:
        res:

    Returns:
        origin: the matched origin
        origin_type: the type of origin (origin_basic_black, origin_basic_red etc.)
        cropped: the cropped region used to match the origin
    """
    matches = []
    image = cv_image.get_red()

    height, width = image.shape
    crop_ratio = 2.6  # the higher this is, the larger the region; the closer to 2, the smaller (2 is a 0x0 region)
    cropped = image[round(height / crop_ratio):round((crop_ratio - 1) * height / crop_ratio),
                    round(width / crop_ratio):round((crop_ratio - 1) * width / crop_ratio)]

    for subdir, dirs, files in os.walk(Path.assets_origins):
        for file in files:  # origin_basic_black, origin_basic_red etc.
            dim = res.origin_dim(file)
            radius = round(dim / 2)
            origin = cv2.split(cv2.imread(os.path.join(subdir, file), cv2.IMREAD_UNCHANGED))
            template = cv2.resize(origin[2], (dim, dim), interpolation=Image.interpolation)
            template_alpha = cv2.resize(origin[3], (dim, dim), interpolation=Image.interpolation) # for masking
            result = cv2.matchTemplate(cropped, template, cv2.TM_CCOEFF_NORMED, mask=template_alpha)

            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            matches.append((file, min_val, max_val, min_loc, max_loc, radius))

    origin_type, _, _, _, top_left, radius = max(matches, key=lambda match: match[2])

    centre = Position(round(top_left[0] + radius + width / crop_ratio),
                      round(top_left[1] + radius + height / crop_ratio))

    origin = Circle(centre, radius, "red", "ORIGIN", is_origin=True)
    return origin, origin_type, cropped

def vector_circles(cv_image: CVImage, res: Resolution, origin: Circle, merged_base, debugger) -> [Circle]:
    """
    Identifies circles using vectors and matches their icons, including the origin.
    (Feel free to remove the debugger parameter and just return the required information to be shown, then add it
    to the debugger in the main loop state.py).

    Args:
        cv_image:
        res:
        origin:
        merged_base:
        debugger:

    Returns:
        circles

    """
    image_gray = cv_image.get_gray()
    image_filtered = cv_image.get_gray()
    image_filtered = cv2.convertScaleAbs(image_filtered, alpha=1.4, beta=0)
    image_filtered = cv2.fastNlMeansDenoising(image_filtered, None, 3, 7, 21)

    circles = [origin]

    for circle_num, rel_position in res.circles().items():
        abs_position = origin.position.sum(rel_position)
        r, color, match_unique_id = Matcher.get_circle_properties(debugger, image_gray, cv_image.get_bgr(),
                                                                  image_filtered, merged_base, abs_position, res)

        if all(x is None for x in (r, color, match_unique_id)):
            continue

        circles.append(Circle(abs_position, r, color, match_unique_id))

    return circles

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