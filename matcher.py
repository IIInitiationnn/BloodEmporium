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
from utils.distance_util import get_endpoints
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

    def match_circles(self, param1=10, param2=45):
        """
        deprecated method using hough transform
        """
        output = []
        for i in range(len(self.cv_images)):
            # detect circles in the image
            image_filtered = self.cv_images[i].get_gray()

            image_filtered = cv2.convertScaleAbs(image_filtered, alpha=1.4, beta=0)
            image_filtered = cv2.fastNlMeansDenoising(image_filtered, None, 3, 7, 21)
            image_filtered = cv2.GaussianBlur(image_filtered, (self.res.gaussian_c(), self.res.gaussian_c()), sigmaX=0, sigmaY=0)
            image_filtered = cv2.bilateralFilter(image_filtered, self.res.bilateral_c(), 200, 200)

            circles = cv2.HoughCircles(image_filtered, cv2.HOUGH_GRADIENT, dp=1, minDist=self.res.min_dist(), param1=param1,
                                       param2=param2, minRadius=self.res.min_radius(), maxRadius=self.res.max_radius())

            if circles is not None:
                circles_for_this_image = []
                # convert the (x, y) coordinates and radius of the circles to integers
                circles = np.round(circles[0, :]).astype("int")

                for (x, y, r) in circles:
                    # standardise radius
                    if r > self.res.threshold_radius():
                        # unconsumed: taupe / neutral
                        r = self.res.large_node_inner_radius()
                    else:
                        # consumed: red
                        r = self.res.small_node_inner_radius()

                    # remove the node from the edges graph
                    c = Circle(Position(x, y), r, None, "")
                    output.append(c)
                    circles_for_this_image.append(c)

        validated_output = []
        while len(output) > 0:
            check = output.pop(0)
            circles = [check]
            for circle in output.copy():
                if Position.points_are_close(check.position, circle.position, self.res):
                    output.remove(circle)
                    circles.append(circle)

            if len(circles) > math.floor(len(self.cv_images) / 2):
                mean_x = mean([circle.x() for circle in circles])
                mean_y = mean([circle.y() for circle in circles])
                mode_r = mode([circle.radius for circle in circles])

                # identify color
                test_r = [circle.radius for circle in circles if circle.radius != mode_r]
                if len(test_r) > 0 and test_r[0] > mode_r:
                    # check the larger circle
                    unlockable = ImageUtil.cut_circle(self.cv_images[0].get_bgr(), (mean_x, mean_y), test_r[0])
                    color = ImageUtil.dominant_color(unlockable)
                    if color is None:
                        unlockable = ImageUtil.cut_circle(self.cv_images[0].get_bgr(), (mean_x, mean_y), mode_r)
                        color = ImageUtil.dominant_color(unlockable)
                    else:
                        mode_r = test_r[0]
                else:
                    unlockable = ImageUtil.cut_circle(self.cv_images[0].get_bgr(), (mean_x, mean_y), mode_r)
                    color = ImageUtil.dominant_color(unlockable)

                # black means node is taken; don't add to nodes
                if color != "black":
                    validated_output.append(Circle(Position(mean_x, mean_y), mode_r, color, ""))
                # else:
                #     print((mean_x, mean_y), mode_r, color)

        self.debugger.set_valid_circles(validated_output)
        return validated_output

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

    def match_icons(self, circles, lines, origin, merged_base):
        """
        deprecated method
        """
        image = self.cv_images[0].get_gray()

        # match circles
        names = merged_base.names
        images = merged_base.images

        i = 0
        nodes = []
        valid_circles = {}
        (x_origin, y_origin), _, _ = origin
        for circle in circles:
            (x, y), r, color = circle
            if (x, y) == (x_origin, y_origin):
                valid_circles[circle] = "ORIGIN"
                continue

            r_small = r * 7 // 9
            unlockable = image[y-r_small:y+r_small, x-r_small:x+r_small]
            height, width = unlockable.shape

            if color == "neutral":
                # brighten the image slightly since it's darker: alpha=contrast=[1,3] beta=brightness=[0,100]
                unlockable = cv2.convertScaleAbs(unlockable, alpha=1, beta=20)
            elif color == "red":
                # brighten and resize the claimed perk (matching correctly is not as important here)
                unlockable = cv2.convertScaleAbs(unlockable, alpha=1, beta=20)
                unlockable = cv2.resize(unlockable, (height * 4 // 3, width * 4 // 3), interpolation=Images.interpolation)

            # do NOT resize unlockable for the base, only resize the base for the unlockable
            # using radius to resize instead of the color would cause a potential mismatch in template matching
            # at least the template match can be correct using a cropped template, but a resized may not be

            height, width = unlockable.shape

            # apply template matching
            output = images.copy()
            result = cv2.matchTemplate(output, unlockable, cv2.TM_CCORR_NORMED)

            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

            top_left = max_loc
            bottom_right = (top_left[0] + width, top_left[1] + height)

            output = output[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]

            match_name = names[round((bottom_right[1] - merged_base.full_dim / 2) / merged_base.full_dim)]
            node_id = f"{i}_{match_name}"

            is_accessible, is_user_claimed = Node.state_from_color(color)
            nodes.append(Node(node_id, match_name, 9999, (x, y), is_accessible, is_user_claimed).get_tuple())
            valid_circles[circle] = node_id

            i += 1

            self.debugger.add_icon(unlockable, output)

        nodes.append(Node("ORIGIN", "ORIGIN", 9999, (x_origin, y_origin), True, True).get_tuple())

        # actual edges joining circles
        edges = []
        for (circle1, circle2) in lines:
            edges.append((valid_circles[circle1], valid_circles[circle2]))

        # construct networkx graph
        graph = nx.Graph()
        graph.add_nodes_from(nodes)
        graph.add_edges_from(edges)
        return graph

# TODO delete this
class HoughTransform:
    def __init__(self, images, res, c_blur=5, bilateral_blur=7, param1=10, param2=45, l_blur=5,
                 canny_min=85, canny_max=40, threshold=30):
        '''
        identifies all the nodes and connections in the image, as well as the origin
        '''
        self.res = res
        self.image_bgr = images["bgr"]
        self.image_gray = images["gray"]
        self.image_r = cv2.split(self.image_bgr)[2]

        self.output = self.image_gray.copy()
        self.output_validated = self.image_gray.copy()

        self.__run_hough_circle(param1, param2)
        self.__match_origin()
        self.__run_hough_line(l_blur, canny_min, canny_max, threshold)
        self.__validate_all()

    def get_valid_circles(self):
        '''
        :return: {((x, y), r, color): id}
        '''
        return self.valid_circles

    def get_connections(self):
        '''
        :return: [circle, circle]
        '''
        return self.connections

    def get_origin(self):
        '''
        :return: (x, y)
        '''
        return self.origin_position

    def __run_hough_circle(self, param1, param2):
        '''
        identify all nodes (circles) in image
        '''

        # detect circles in the image
        circles = self.image_gray.copy()

        #circles = cv2.convertScaleAbs(circles, alpha=1.4, beta=0)
        circles = cv2.normalize(circles, np.zeros((circles.shape[1], circles.shape[0])), 0, 255, cv2.NORM_MINMAX)
        circles = cv2.fastNlMeansDenoising(circles, None, 3, 7, 21)
        circles = cv2.GaussianBlur(circles, (self.res.gaussian_c(), self.res.gaussian_c()), sigmaX=0, sigmaY=0)
        circles = cv2.bilateralFilter(circles, self.res.bilateral_c(), 200, 200)
        self.hhhhh = circles

        circles = cv2.HoughCircles(circles, cv2.HOUGH_GRADIENT, dp=1, minDist=self.res.min_dist(), param1=param1,
                                   param2=param2, minRadius=self.res.min_radius(), maxRadius=self.res.max_radius())

        self.circles = [] # ((x, y), r, color)
        if circles is not None:
            # convert the (x, y) coordinates and radius of the circles to integers
            circles = np.round(circles[0, :]).astype("int")

            for (x, y, r) in circles:
                # standardise radius
                if r > self.res.threshold_radius():
                    # unconsumed: taupe / neutral
                    r = self.res.large_node_inner_radius()
                else:
                    # consumed: red
                    r = self.res.small_node_inner_radius()

                # identify color
                unlockable = ImageUtil.cut_circle(self.image_bgr, (x, y), r)
                color = ImageUtil.dominant_color(unlockable)
                if r == self.res.small_node_inner_radius() and color != "red":
                    # likely the circle was misidentified as small; if it were small, it should be red: evaluate it again
                    r = self.res.large_node_inner_radius()
                    unlockable = ImageUtil.cut_circle(self.image_bgr, (x, y), r)
                    color = ImageUtil.dominant_color(unlockable)

                cv2.circle(self.output, (x, y), r, 255, 2)
                cv2.rectangle(self.output, (x - 5, y - 5), (x + 5, y + 5), 255, -1)

                # remove the node from the edges graph
                self.circles.append(((x, y), r, color))

    def __match_origin(self):
        matches = []

        height, width = self.image_r.shape
        crop_ratio = 3
        self.cropped = self.image_r[round(height / crop_ratio):round((crop_ratio - 1) * height / crop_ratio),
                               round(width / crop_ratio):round((crop_ratio - 1) * width / crop_ratio)]

        dim = self.res.origin_dim() # TODO some issues matching origin at different resolutions
        radius = round(dim / 2)
        for subdir, dirs, files in os.walk(Path.assets_origins):
            for file in files:
                origin = cv2.split(cv2.imread(os.path.join(subdir, file), cv2.IMREAD_UNCHANGED))
                template = cv2.resize(origin[2], (dim, dim), interpolation=Images.interpolation)
                template_alpha = cv2.resize(origin[3], (dim, dim), interpolation=Images.interpolation) # for masking
                result = cv2.matchTemplate(self.cropped, template, cv2.TM_CCOEFF_NORMED, mask=template_alpha)

                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                matches.append((file, min_val, max_val, min_loc, max_loc))

        origin_type, _, _, _, top_left = max(matches, key=lambda match: match[2])

        centre = (round(top_left[0] + radius + width / crop_ratio), round(top_left[1] + radius + height / crop_ratio))
        cv2.circle(self.output_validated, centre, radius, 255, 4)
        self.circles.append((centre, radius, "red"))
        self.origin_type = origin_type
        self.origin_position = centre

    def __run_hough_line(self, l_blur, canny_min, canny_max, threshold):
        '''
        identify all connections (lines) in image
        '''

        base_l = self.image_gray
        # base_l = cv2.GaussianBlur(base_l, (self.res.gaussian_l(), self.res.gaussian_l()), sigmaX=0, sigmaY=0) # lines
        # base_l = cv2.GaussianBlur(base_l, (l_blur, l_blur), sigmaX=0, sigmaY=0) # lines
        base_l = cv2.bilateralFilter(base_l, 5, 200, 200)
        base_l = cv2.convertScaleAbs(base_l, alpha=1.3, beta=50)
        self.edges = cv2.Canny(base_l, self.res.canny_min(), self.res.canny_max())

        for (x, y), r, color in self.circles:
            # remove the node's circle from the edges graph (reduces noise)
            cv2.circle(self.edges, (x, y), r + Resolution.additional_radius(r), 0, thickness=-1)

        lines = cv2.HoughLinesP(self.edges, rho=1, theta=np.pi / 180, threshold=threshold,
                                minLineLength=self.res.line_length(), maxLineGap=self.res.line_length())

        self.lines = []
        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                cv2.line(self.output, (x1, y1), (x2, y2), 255, 5)
                self.lines.append(((x1, y1), (x2, y2)))

    def __validate_all(self):
        # validate lines by removing those that do not join two circles; add the connected nodes to edge list
        # validate circles by removing those which are not joined by lines
        self.valid_circles = {}
        self.connections = []
        for line in self.lines:
            circle1, circle2 = get_endpoints(line, self.circles, self.res)
            if circle1 is not None and circle2 is not None and \
                    (circle1, circle2) not in self.connections and (circle2, circle1) not in self.connections:
                # TODO each pair of circles needs 2 joining lines to be valid
                self.connections.append((circle1, circle2))
                self.valid_circles[circle1] = "unassigned"
                self.valid_circles[circle2] = "unassigned"

                # draw the line
                (x1, y1), (x2, y2) = line
                cv2.line(self.output_validated, (x1, y1), (x2, y2), 255, 5)

        for (x, y), r, _ in self.valid_circles.keys():
            # draw the circle in the output image, then draw a rectangle
            # corresponding to the center of the circle
            cv2.circle(self.output_validated, (x, y), r, 255, 1)
            cv2.rectangle(self.output_validated, (x - 5, y - 5), (x + 5, y + 5), 255, -1)

class IconMatcher:
    def __init__(self, image, nodes_connections, merged_base):
        self.output = []

        # match each node of graph to an unlockable
        valid_circles = nodes_connections.get_valid_circles()
        connections = nodes_connections.get_connections()
        origin = nodes_connections.get_origin()

        # validate lines by removing those that do not join two circles; add the connected nodes to edge list
        # validate circles by removing those which are not joined by lines

        # match circles
        names = merged_base.names
        images = merged_base.images

        i = 0
        nodes = []
        for circle in valid_circles.keys():
            (x, y), r, color = circle
            if (x, y) == origin:
                valid_circles[circle] = "ORIGIN"
                continue

            r_small = r * 7 // 9
            unlockable = image[y-r_small:y+r_small, x-r_small:x+r_small]
            height, width = unlockable.shape

            if color == "neutral":
                # brighten the image slightly since it's darker: alpha=contrast=[1,3] beta=brightness=[0,100]
                unlockable = cv2.convertScaleAbs(unlockable, alpha=1, beta=20)
            elif color == "red":
                # brighten and resize the claimed perk (matching correctly is not as important here)
                unlockable = cv2.convertScaleAbs(unlockable, alpha=1, beta=20)
                unlockable = cv2.resize(unlockable, (height * 4 // 3, width * 4 // 3), interpolation=Images.interpolation)

            # do NOT resize unlockable for the base, only resize the base for the unlockable
            # using radius to resize instead of the color would cause a potential mismatch in template matching
            # at least the template match can be correct using a cropped template, but a resized may not be

            height, width = unlockable.shape

            # apply template matching
            output = images.copy()
            result = cv2.matchTemplate(output, unlockable, cv2.TM_CCORR_NORMED)

            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

            top_left = max_loc
            bottom_right = (top_left[0] + width, top_left[1] + height)

            output = output[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]

            match_name = names[round((bottom_right[1] - merged_base.full_dim / 2) / merged_base.full_dim)]
            node_id = f"{i}_{match_name}"

            is_accessible, is_user_claimed = Node.state_from_color(color)
            nodes.append(Node(node_id, match_name, 9999, (x, y), is_accessible, is_user_claimed).get_tuple())
            valid_circles[circle] = node_id

            i += 1

            self.output.append((cv2.resize(unlockable, (250, 250)), cv2.resize(output, (250, 250))))

        nodes.append(Node("ORIGIN", "ORIGIN", 9999, origin, True, True).get_tuple())

        # actual edges joining circles
        edges = []
        for (circle1, circle2) in connections:
            edges.append((valid_circles[circle1], valid_circles[circle2]))

        # construct networkx graph
        self.graph = nx.Graph()
        self.graph.add_nodes_from(nodes)
        self.graph.add_edges_from(edges)
        '''dim = 50

        np.set_printoptions(threshold=np.inf)
        template = cv2.imread(path_example, cv2.IMREAD_GRAYSCALE)
        template = cv2.resize(template, (dim, dim), interpolation=cv2.INTER_AREA) # configure in config, should be some default according to resolutions; diff for square vs hexagon vs diamond
        template_alpha = cv2.resize(cv2.split(cv2.imread(path_example, cv2.IMREAD_UNCHANGED))[3], (dim, dim), interpolation=cv2.INTER_AREA) # for masking

        base = cv2.imread(path_base, cv2.IMREAD_GRAYSCALE)

        height, width = template.shape

        # apply template matching
        output = base.copy()
        method = "cv2.TM_CCORR_NORMED"
        result = cv2.matchTemplate(output, template, eval(method), mask=template_alpha)

        single_match = True

        if single_match:
            # single match
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

            top_left = max_loc
            bottom_right = (top_left[0] + width, top_left[1] + height)
            cv2.rectangle(output, top_left, bottom_right, 255, 2) # 255 = white; 2 = thickness
        else:
            # multiple matches
            threshold = 0.95 # larger value = better match / fit
            loc = np.where(result >= threshold)

            matches = []
            for top_left in zip(*loc[::-1]):
                bottom_right = (top_left[0] + width, top_left[1] + height)
                if not any([close_proximity_circle_to_circle(tl, top_left) and close_proximity_circle_to_circle(br, bottom_right) for (tl, br) in matches]):
                    matches.append((top_left, bottom_right))
                    cv2.rectangle(output, top_left, bottom_right, 255, 2) # 255 = white; 2 = thickness

        cv2.imshow(method, output)
        cv2.waitKey(0)

        cv2.imshow('Image', template)
        cv2.imshow('Base', base)
        cv2.waitKey(0)'''

class CircleMatcher:
    @staticmethod
    def match(path_base, c_blur, param1, param2):
        base = cv2.imread(path_base, cv2.IMREAD_GRAYSCALE)
        base_c = cv2.GaussianBlur(base, (c_blur, c_blur), sigmaX=0, sigmaY=0) # circles

        height, width = base.shape
        output = np.zeros((height, width), np.uint8)

        # detect circles in the image
        circles = cv2.HoughCircles(base_c, cv2.HOUGH_GRADIENT, dp=1, minDist=80, param1=param1, param2=param2,
                                   minRadius=7, maxRadius=50)

        # circles = []
        if circles is not None:
            circles = np.round(circles[0, :]).astype("int")
            for (x, y, r) in circles:
                cv2.circle(output, (x, y), r, 255, 10)
                # circles.append((x, y, r))

        return output
