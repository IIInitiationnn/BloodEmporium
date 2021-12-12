import math

import numpy as np


class Position:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def xy(self):
        return self.x, self.y

    def scale(self, ratio):
        return Position(round(self.x * ratio), round(self.y * ratio))

    def sum(self, vector):
        return Position(self.x + vector.x, self.y + vector.y)

    @staticmethod
    def is_equal(position1, position2):
        return position1.x == position2.x and position1.y == position2.y

    @staticmethod
    def points_are_close(position1, position2, res):
        '''
        used for proximity between two points
        '''
        max_dist = res.ratio() * 30
        return abs(position1.x - position2.x) < max_dist and abs(position1.y - position2.y) < max_dist

class Circle:
    def __init__(self, position, radius, color, name, is_origin=False):
        self.position = position
        self.radius = radius
        self.color = color
        self.name = name
        self.is_origin = is_origin

    def x(self):
        return self.position.x

    def y(self):
        return self.position.y

    def xy(self):
        return self.position.xy()

    def set_color(self, color):
        self.color = color

    @staticmethod
    def is_equal(circle1, circle2):
        return Position.is_equal(circle1.position, circle2.position) and \
               circle1.radius == circle2.radius and \
               circle1.color == circle2.color

class Line:
    def __init__(self, position1, position2):
        self.position1 = position1
        self.position2 = position2

    def positions(self):
        return self.position1.x, self.position1.y, self.position2.x, self.position2.y

    def close_to_circle(self, circle, res, which):
        '''
        used for line endpoint proximity to centre of circle
        '''
        if which == 1:
            position = self.position1
        else:
            position = self.position2

        return pow(position.x - circle.x(), 2) + pow(position.y - circle.y(), 2) < 15000 * math.pow(res.ratio(), 2)

    def get_endpoints(self, circles, res):
        x1, y1, x2, y2 = self.position1.x, self.position1.y, self.position2.x, self.position2.y

        circle1 = None
        for circle in circles:
            if self.close_to_circle(circle, res, 1):
                circle1 = circle
                break

        circle2 = None
        for circle in circles:
            if self.close_to_circle(circle, res, 2) and circle != circle1:
                circle2 = circle
                break

        # checking line vector passes near centre of circles
        if circle1 is not None and circle2 is not None:
            line_p1 = np.array([x1, y1])
            line_p2 = np.array([x2, y2])
            circle_p1 = np.array([circle1.x(), circle1.y()])
            circle_p2 = np.array([circle2.x(), circle2.y()])

            dist_c1 = np.abs(np.cross(line_p2 - line_p1, line_p1 - circle_p1)) / np.linalg.norm(line_p2 - line_p1)
            dist_c2 = np.abs(np.cross(line_p2 - line_p1, line_p1 - circle_p2)) / np.linalg.norm(line_p2 - line_p1)

            max_dist = 35 * res.ratio()
            if dist_c1 > max_dist or dist_c2 > max_dist:
                circle1 = None
                circle2 = None

        if circle1 is None or circle2 is None:
            return None
        else:
            return Connection(circle1, circle2)

class Connection:
    def __init__(self, circle1, circle2):
        self.circle1 = circle1
        self.circle2 = circle2

    @staticmethod
    def is_equal(c1, c2):
        return (Circle.is_equal(c1.circle1, c2.circle1) and Circle.is_equal(c1.circle2, c2.circle2)) or \
            (Circle.is_equal(c1.circle1, c2.circle2) and Circle.is_equal(c1.circle2, c2.circle1))

    @staticmethod
    def list_contains(connections, wanted):
        for connection in connections:
            if Connection.is_equal(connection, wanted):
                return True
        return False