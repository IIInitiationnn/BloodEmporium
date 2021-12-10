import os.path
import math
import time
from datetime import datetime
from statistics import mean, mode

import cv2
import cv2.cv2
import networkx as nx
import numpy as np
import pyautogui

from config import Config
from cv_images import CVImages
from debugger import Debugger
from images import Images
from node import Node
from paths import Path
from resolution import Resolution
from shapes import Position, Circle, Line, Connection
from utils.image_util import ImageUtil
from utils.network_util import NetworkUtil

'''
Offerings | Killer + Survivor | Hexagon | C:/Program Files (x86)/Steam/steamapps/common/Dead by Daylight/DeadByDaylight/Content/UI/Icons/Favors
Addons    | Killer + Survivor | Square  | C:/Program Files (x86)/Steam/steamapps/common/Dead by Daylight/DeadByDaylight/Content/UI/Icons/ItemAddons
Items     | Survivor          | Square  | C:/Program Files (x86)/Steam/steamapps/common/Dead by Daylight/DeadByDaylight/Content/UI/Icons/Items
Perks     | Killer + Survivor | Diamond | C:/Program Files (x86)/Steam/steamapps/common/Dead by Daylight/DeadByDaylight/Content/UI/Icons/Perks
'''

'''
cv2.IMREAD_COLOR
cv2.IMREAD_GRAYSCALE
cv2.IMREAD_UNCHANGED
'''

class Matcher:
    def __init__(self, debugger, cv_images, res):
        self.debugger = debugger
        self.cv_images = cv_images
        self.res = res

    def match_origin(self):
        matches = []
        image = self.cv_images[0].get_red()

        height, width = image.shape
        crop_ratio = 3
        cropped = image[round(height / crop_ratio):round((crop_ratio - 1) * height / crop_ratio),
                        round(width / crop_ratio):round((crop_ratio - 1) * width / crop_ratio)]
        self.debugger.set_cropped(cropped)

        dim = self.res.origin_dim() # TODO some issues matching origin at different resolutions
        radius = round(dim / 2)
        for subdir, dirs, files in os.walk(Path.assets_origins):
            for file in files:
                origin = cv2.split(cv2.imread(os.path.join(subdir, file), cv2.IMREAD_UNCHANGED))
                template = cv2.resize(origin[2], (dim, dim), interpolation=Images.interpolation)
                template_alpha = cv2.resize(origin[3], (dim, dim), interpolation=Images.interpolation) # for masking
                result = cv2.matchTemplate(cropped, template, cv2.TM_CCOEFF_NORMED, mask=template_alpha)

                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                matches.append((file, min_val, max_val, min_loc, max_loc))

        origin_type, _, _, _, top_left = max(matches, key=lambda match: match[2])
        self.debugger.set_origin_type(origin_type)

        centre = Position(round(top_left[0] + radius + width / crop_ratio),
                  round(top_left[1] + radius + height / crop_ratio))

        origin = Circle(centre, radius, "red", "ORIGIN", is_origin=True)
        self.debugger.set_origin(origin)
        return origin

    def vector_circles(self, origin, merged_base):
        """
        identifies circles using vectors and matches their icons
        includes the origin
        """
        names = merged_base.names
        images = merged_base.images

        output = [origin]
        image = self.cv_images[0].get_gray()

        image_filtered = self.cv_images[0].get_gray()
        image_filtered = cv2.convertScaleAbs(image_filtered, alpha=1.4, beta=0)
        image_filtered = cv2.fastNlMeansDenoising(image_filtered, None, 3, 7, 21)
        #image_filtered = cv2.GaussianBlur(image_filtered, (self.res.gaussian_c(), self.res.gaussian_c()), sigmaX=0, sigmaY=0)
        #image_filtered = cv2.bilateralFilter(image_filtered, self.res.bilateral_c(), 200, 200)

        ur = self.res.unlockable_radius()
        for circle_num, rel_position in self.res.circles().items():
            abs_position = origin.position.sum(rel_position)
            square = image_filtered.copy()[abs_position.y-ur:abs_position.y+ur, abs_position.x-ur:abs_position.x+ur]

            # identify if large (unclaimed) node exists
            circles = cv2.HoughCircles(square, cv2.HOUGH_GRADIENT, dp=1, minDist=self.res.min_dist(), param1=10,
                                       param2=45, minRadius=self.res.detect_radius(), maxRadius=9999)
            if circles is not None:
                # convert the (x, y) coordinates and radius of the circles to integers
                circles = np.round(circles[0, :]).astype("int")
                if len(circles) > 1 or circles[0][2] < self.res.threshold_radius():
                    pass # TODO throw error
                r = self.res.large_node_inner_radius()
                cv2.circle(square, (circles[0][0], circles[0][1]), r, 255, thickness=1)

                # identify color
                unlockable = ImageUtil.cut_circle(self.cv_images[0].get_bgr(), (abs_position.x, abs_position.y), r)
                color = ImageUtil.dominant_color(unlockable)
                if color != "taupe" and color != "neutral":
                    continue

                # identify unlockable
                r_small = r * 2 // 3
                unlockable = image[abs_position.y - r_small:abs_position.y + r_small,
                                   abs_position.x - r_small:abs_position.x + r_small]
                height, width = unlockable.shape

                # apply template matching
                base = images.copy()
                result = cv2.matchTemplate(base, unlockable, cv2.TM_CCORR_NORMED)

                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

                top_left = max_loc
                bottom_right = (top_left[0] + width, top_left[1] + height)
                match = base[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]

                match_name = names[round((bottom_right[1] - merged_base.full_dim / 2) / merged_base.full_dim)]
                output.append(Circle(abs_position, r, color, match_name))

                self.debugger.add_icon(unlockable, match)
            else:
                x, y, r = abs_position.x, abs_position.y, self.res.small_node_inner_radius()

                # identify color
                unlockable = ImageUtil.cut_circle(self.cv_images[0].get_bgr(), (x, y), r)
                color = ImageUtil.dominant_color(unlockable)
                if color != "red":
                    continue
                output.append(Circle(abs_position, r, color, "CLAIMED"))

            # print(circle_num)
            # print(color)
            # cv2.imshow("square", square)
            # cv2.waitKey(0)
        self.debugger.set_valid_circles(output)
        return output

    def match_lines(self, circles, threshold=30):
        validated1_output = []
        for i in range(len(self.cv_images)):
            image_filtered = self.cv_images[i].get_gray()
            image_filtered = cv2.bilateralFilter(image_filtered, 5, 200, 200)
            image_filtered = cv2.convertScaleAbs(image_filtered, alpha=1.3, beta=50)
            edges = cv2.Canny(image_filtered, self.res.canny_min(), self.res.canny_max())
            self.debugger.add_edge_image(edges)

            for circle in circles:
                # remove the node's circle from the edges graph (reduces noise)
                cv2.circle(edges, (circle.x(), circle.y()), circle.radius + Resolution.additional_radius(circle.radius),
                           0, thickness=-1)

            lines = cv2.HoughLinesP(edges, rho=1, theta=np.pi / 180, threshold=threshold,
                                    minLineLength=self.res.line_length(), maxLineGap=self.res.line_length())

            output = []
            if lines is not None:
                for line in lines:
                    x1, y1, x2, y2 = line[0]
                    l = Line(Position(x1, y1), Position(x2, y2))
                    output.append(l)
                    self.debugger.add_line(i, l)

            # validate lines by removing those that do not join two circles; add the connected nodes to edge list
            connections = []
            for line in output:
                connection = line.get_endpoints(circles, self.res)
                if connection is not None and not Connection.list_contains(connections, connection):
                    connections.append(connection)
            validated1_output.extend(connections)

        validated2_output = []
        while len(validated1_output) > 0:
            check = validated1_output.pop(0)
            connections = [check]
            for connection in validated1_output.copy():
                if Connection.is_equal(check, connection):
                    validated1_output.remove(connection)
                    connections.append(connection)

            if len(connections) > math.floor(len(self.cv_images) / 2):
                validated2_output.append(check)
        self.debugger.set_connections(validated2_output)
        return validated2_output