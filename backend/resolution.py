import math

from shapes import Position


class Resolution:
    '''
    the following constants scale from this resolution
    - 3840x2160 (4k)
    - UI scale 100
    '''
    __width = 3840
    __height = 2160
    __ui_scale = 100

    # node sizes
    __threshold_radius = 69
    __large_node_outer_radius = 82
    __large_node_inner_radius = 69
    __small_node_outer_radius = 62
    __small_node_inner_radius = 52

    # origin
    __origin_dim = 96
    __origin_prestige_dim = 265

    # vector circles (relative to origin
    __circles_old = {
        # row 1
        1: Position(0, -252),
        2: Position(213, -125),
        3: Position(213, 125),
        4: Position(0, 252),
        5: Position(-213, 125),
        6: Position(-213, -125),

        # row 2
        7: Position(-126, -474),
        8: Position(126, -474),
        9: Position(352, -352),
        10: Position(482, -126),
        11: Position(482, 126),
        12: Position(360, 360),
        13: Position(126, 477),
        14: Position(-126, 477),
        15: Position(-352, 352),
        16: Position(-482, 126),
        17: Position(-482, -126),
        18: Position(-360, -360),

        # row 3
        19: Position(0, -713),
        20: Position(360, -612),
        21: Position(625, -357),
        22: Position(713, -0),
        23: Position(625, 357),
        24: Position(360, 612),
        25: Position(0, 713),
        26: Position(-360, 612),
        27: Position(-625, 357),
        28: Position(-713, -0),
        29: Position(-625, -357),
        30: Position(-360, -612),
    }
    __circles = {
        1: Position(0, -246),
        2: Position(210, -126),
        3: Position(210, 123),
        4: Position(0, 245),
        5: Position(-210, 123),
        6: Position(-210, -126),
        7: Position(-123, -468),
        8: Position(125, -468),
        9: Position(356, -346),
        10: Position(482, -123),
        11: Position(482, 120),
        12: Position(357, 342),
        13: Position(125, 468),
        14: Position(-123, 468),
        15: Position(-357, 342),
        16: Position(-481, 120),
        17: Position(-481, -123),
        18: Position(-357, -346),
        19: Position(0, -708),
        20: Position(360, -612),
        21: Position(623, -349),
        22: Position(720, 0),
        23: Position(623, 347),
        24: Position(360, 609),
        25: Position(0, 704),
        26: Position(-360, 609),
        27: Position(-621, 347),
        28: Position(-720, 0),
        29: Position(-621, -349),
        30: Position(-360, -612),
    }



    __unlockable_radius = 100
    __detect_radius = 70

    # hough circles
    __gaussian_c = 10
    __bilateral_c = 14
    __min_dist = 160
    __min_radius = 40
    __max_radius = 105

    # hough lines
    __gaussian_l = 10
    __canny_min = 42
    __canny_max = 20
    __line_length = 54

    # template matching
    __mystery_box = 200
    __items_addons = 115
    __offerings = 144
    __perks = 144

    def __init__(self, width, height, ui_scale):
        self.width = width
        self.height = height
        self.ui_scale = ui_scale

    def print(self):
        print(f"{self.width}x{self.height} @ {self.ui_scale}% UI Scale")

    def ratio(self):
        return self.width / Resolution.__width * self.ui_scale / Resolution.__ui_scale

    # screenshot dimensions and points
    # https://www.desmos.com/calculator/4psfavvzoz
    # https://www.desmos.com/calculator/hcxllwtp44 6.1.0
    def top_left(self):
        return self.top_left_x(), self.top_left_y()

    def top_left_x(self):
        return round(7 + 0.13 * self.width * self.ui_scale / 100)

    def top_left_y(self):
        return round(29 - 0.345 * self.ui_scale + 0.485 * self.height - 0.188 * self.width * self.ui_scale / 100)

    def cap_dim(self):
        return round(10 + 0.441 * self.width * self.ui_scale / 100)

    # node sizes
    @staticmethod
    def additional_radius(radius):
        return round(1.2 * (Resolution.__large_node_outer_radius / Resolution.__large_node_inner_radius * radius - radius))

    def threshold_radius(self):
        return round(Resolution.__threshold_radius * self.ratio())

    def large_node_inner_radius(self):
        return round(Resolution.__large_node_inner_radius * self.ratio())

    def small_node_inner_radius(self):
        return round(Resolution.__small_node_inner_radius * self.ratio())

    # vector circles
    def circles(self):
        scaled = {}
        ratio = self.ratio()
        for circle_num, position in self.__circles.items():
            scaled[circle_num] = position.scale(ratio)
        return scaled

    def unlockable_radius(self):
        return round(Resolution.__unlockable_radius * self.ratio())

    def detect_radius(self):
        return round(Resolution.__detect_radius * self.ratio())

    # hough circles
    def gaussian_c(self):
        c = (Resolution.__gaussian_c * self.ratio())
        ceil = math.ceil(c)
        floor = math.floor(c)
        if ceil % 2 == 1:
            return ceil
        if floor % 2 == 1:
            return floor
        return floor + 1

    def bilateral_c(self):
        return round(Resolution.__bilateral_c * self.ratio())

    def min_dist(self):
        return round(Resolution.__min_dist * self.ratio())

    def min_radius(self):
        return round(Resolution.__min_radius * self.ratio())

    def max_radius(self):
        return round(Resolution.__max_radius * self.ratio())

    # origin
    def origin_dim(self, file):
        return round((Resolution.__origin_prestige_dim if file == "origin_prestige.png" else Resolution.__origin_dim) *
                     self.ratio())

    # hough lines
    def gaussian_l(self):
        c = (Resolution.__gaussian_l * self.ratio())
        ceil = math.ceil(c)
        floor = math.floor(c)
        if ceil % 2 == 1:
            return ceil
        if floor % 2 == 1:
            return floor
        return floor + 1

    def canny_min(self):
        return round(Resolution.__canny_min / self.ratio())

    def canny_max(self):
        return round(Resolution.__canny_max / self.ratio())

    def line_length(self):
        return round(Resolution.__line_length * self.ratio())

    # template matching
    def mystery_box(self):
        return round(Resolution.__mystery_box * self.ratio())

    def items_addons(self):
        return round(Resolution.__items_addons * self.ratio())

    def offerings(self):
        return round(Resolution.__offerings * self.ratio())

    def perks(self):
        return round(Resolution.__perks * self.ratio())
