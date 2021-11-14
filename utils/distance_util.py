# TODO these numbers will need to scale from UI size
import math


def circles_are_overlapping(a, b):
    '''
    used for proximity between centres of two circles
    '''
    x1 = a[0]
    y1 = a[1]
    x2 = b[0]
    y2 = b[1]
    return abs(x1 - x2) < 30 and abs(y1 - y2) < 30 # 4k TODO

def line_close_to_circle(a, b, res):
    '''
    used for line endpoint proximity to centre of circle
    '''
    x1 = a[0]
    y1 = a[1]
    x2 = b[0]
    y2 = b[1]
    return pow(x1 - x2, 2) + pow(y1 - y2, 2) < 20000 * math.pow(res.ratio(), 2)

def line_is_valid(line, circles, res):
    circle1, circle2 = get_endpoints(line, circles, res)
    return circle1 is not None and circle2 is not None

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

    return circle1, circle2