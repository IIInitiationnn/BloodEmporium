import math

import numpy as np
# TODO delete this file
def line_close_to_circle(a, b, res):
    '''
    used for line endpoint proximity to centre of circle
    '''
    x1 = a[0]
    y1 = a[1]
    x2 = b[0]
    y2 = b[1]
    return pow(x1 - x2, 2) + pow(y1 - y2, 2) < 15000 * math.pow(res.ratio(), 2)

def get_endpoints(line, circles, res):
    (x1, y1), (x2, y2) = line

    circle1 = None
    for circle in circles:
        (x, y), _, _ = circle
        if line_close_to_circle((x, y), (x1, y1), res):
            circle1 = circle
            break

    circle2 = None
    for circle in circles:
        (x, y), _, _ = circle
        if line_close_to_circle((x, y), (x2, y2), res) and circle != circle1:
            circle2 = circle
            break

    # checking line vector passes near centre of circles
    if circle1 is not None and circle2 is not None:
        line_p1 = np.array([x1, y1])
        line_p2 = np.array([x2, y2])
        circle_p1 = np.array([circle1[0][0], circle1[0][1]])
        circle_p2 = np.array([circle2[0][0], circle2[0][1]])

        dist_c1 = np.abs(np.cross(line_p2 - line_p1, line_p1 - circle_p1)) / np.linalg.norm(line_p2 - line_p1)
        dist_c2 = np.abs(np.cross(line_p2 - line_p1, line_p1 - circle_p2)) / np.linalg.norm(line_p2 - line_p1)

        max_dist = 30 * res.ratio()
        if dist_c1 > max_dist or dist_c2 > max_dist:
            circle1 = None
            circle2 = None

    return circle1, circle2