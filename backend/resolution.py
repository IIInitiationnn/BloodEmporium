import math


class Resolution:
    """
    the following constants scale from this resolution
    - 3840x2160 (4k)
    - UI scale 100
    """
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
    __origin_prestige_small_dim = 168

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
        return self.height / Resolution.__height * self.ui_scale / Resolution.__ui_scale

    # screenshot dimensions and points
    # https://www.desmos.com/calculator/4psfavvzoz
    # https://www.desmos.com/calculator/hcxllwtp44 6.1.0
    # https://www.desmos.com/calculator/p3bqkbaiod widescreen support
    # https://www.desmos.com/calculator/otc52rt6wy squarescreen support
    def top_left(self):
        return self.top_left_x(), self.top_left_y()

    def top_left_x(self):
        return round(0.000139595 * self.width * self.ui_scale +
                     0.00205159 * self.height * self.ui_scale +
                     7.8899)

    def top_left_y(self):
        return round(0.000116994 * self.width * self.ui_scale -
                     0.00377624 * self.height * self.ui_scale +
                     0.504239 * self.height)

    def cap_dim(self):
        return round(0.00788788 * self.height * self.ui_scale)

    # node sizes
    @staticmethod
    def additional_radius(radius):
        return round(1.2 * (Resolution.__large_node_outer_radius / Resolution.__large_node_inner_radius * radius - radius))

    # origin
    def origin_dim(self, file):
        if file == "origin_prestige.png":
            return round(Resolution.__origin_prestige_dim * self.ratio())

        if file == "origin_prestige_small.png":
            return round(Resolution.__origin_prestige_small_dim * self.ratio())

        return round(Resolution.__origin_dim * self.ratio())

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
