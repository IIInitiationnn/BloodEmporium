import math

import cv2
import cv2.cv2
import networkx as nx
import numpy as np
from pyvis.network import Network

from mergedbase import MergedBase
from node import Node
from utils.distance_util import circles_are_overlapping, line_close_to_circle, get_endpoints

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

# TODO mystery boxes in assets folder

# noinspection PyUnresolvedReferences
class HoughTransform:
    def __init__(self, image, c_blur=11, param1=10, param2=45, l_blur=5,
                 canny_min=85, canny_max=40, threshold=30, max_line_length=25):
        '''
        identifies all the nodes and connections in the image, as well as the origin
        '''
        self.image = image
        self.__output = image.copy()

        self.__run_hough_circle(c_blur, param1, param2)
        self.__run_hough_line(l_blur, canny_min, canny_max, threshold, max_line_length)

        cv2.imshow("output", self.__output)
        cv2.imshow("edges", self.edges)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def get_circles(self):
        '''
        :return: [(x, y), r, colour]
        '''
        return self.circles

    def get_lines(self):
        '''
        :return: [(x1, y1), (x2, y2)]
        '''
        return self.lines

    def get_origin(self):
        '''
        :return: (x, y)
        '''
        return self.origin_position

    def __run_hough_circle(self, c_blur, param1, param2):
        '''
        identify all nodes (circles) in image
        '''

        blurred_image = cv2.GaussianBlur(self.image, (c_blur, c_blur), sigmaX=0, sigmaY=0) # circles

        # TODO minDist, minRadius and maxRadius will need to scale from UI size

        # detect circles in the image
        circles = cv2.HoughCircles(blurred_image, cv2.HOUGH_GRADIENT, dp=1, minDist=80,
                                   param1=param1, param2=param2, minRadius=7, maxRadius=50)

        # TODO need to add origin: use asset and template matching for origin

        self.circles = [] # ((x, y), r, colour)
        if circles is not None:
            # convert the (x, y) coordinates and radius of the circles to integers
            circles = np.round(circles[0, :]).astype("int")

            # loop over the (x, y) coordinates and radius of the circles
            for (x, y, r) in circles:
                # draw the circle in the output image, then draw a rectangle
                # corresponding to the center of the circle
                cv2.circle(self.__output, (x, y), r, 255, 4)
                cv2.rectangle(self.__output, (x - 5, y - 5), (x + 5, y + 5), 255, -1)

                # remove the node from the edges graph
                self.circles.append(((x, y), r, "yellow")) # need to read colour from image

        # origin: manual for now for base.png
        cv2.circle(self.__output, (650, 773), 23, 255, 4)
        self.circles.append(((650, 773), 23, "yellow"))
        self.origin_position = (650, 773)

    def __run_hough_line(self, l_blur, canny_min, canny_max, threshold, max_line_length):
        '''
        identify all connections (lines) in image
        '''

        base_l = cv2.GaussianBlur(self.image, (l_blur, l_blur), sigmaX=0, sigmaY=0) # lines
        edges = cv2.Canny(base_l, canny_min, canny_max)

        for (x, y), r, colour in self.circles:
            # remove the node from the edges graph
            cv2.circle(edges, (x, y), 1, 0, math.floor(r / 1.9) + 55) # tweak size of circle removal

        # TODO minLineLength will need to scale from UI size

        lines = cv2.HoughLinesP(edges, rho=1, theta=np.pi / 180, threshold=threshold, minLineLength=25, maxLineGap=max_line_length)

        self.lines = []
        for line in lines:
            x1, y1, x2, y2 = line[0]
            if any([line_close_to_circle((x, y), (x1, y1)) for (x, y), _, _ in self.circles]) and\
                    any([line_close_to_circle((x, y), (x2, y2)) for (x, y), _, _ in self.circles]):
                # TODO move to matcher: remove lines not in prox to circles, remove circles not in prox to lines
                #   then match circles, then lines
                # TODO evaluate which nodes it is joining in matcher

                cv2.line(self.__output, (x1, y1), (x2, y2), 255, 5)
                self.lines.append(((x1, y1), (x2, y2)))

        self.edges = edges


class Matcher:
    def __init__(self, image, nodes_connections, merged_base):
        # match each node of graph to an unlockable
        # TODO: if red or black we need to brighten it and enlarge by ~1.3333

        circles = nodes_connections.get_circles()
        lines = nodes_connections.get_lines()
        origin = nodes_connections.get_origin()


        # validate lines by removing those that do not join two circles; add the connected nodes to edge list
        # validate circles by removing those which are not joined by lines
        connections = []
        valid_circles = {}
        for line in lines:
            circle1, circle2 = get_endpoints(line, circles)
            if circle1 is not None and circle2 is not None and \
                    (circle1, circle2) not in connections and (circle2, circle1) not in connections:
                connections.append((circle1, circle2))
                valid_circles[circle1] = "unassigned"
                valid_circles[circle2] = "unassigned"

        # match circles
        names = merged_base.names
        images = merged_base.images

        i = 0
        nodes = []
        for circle in valid_circles.keys():
            (x, y), r, colour = circle
            if (x, y) == origin:
                valid_circles[circle] = "ORIGIN"
                continue

            unlockable = image[y-r:y+r, x-r:x+r]

            height, width = unlockable.shape

            # apply template matching
            output = images.copy()
            result = cv2.matchTemplate(output, unlockable, cv2.TM_CCORR_NORMED)

            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

            top_left = max_loc
            bottom_right = (top_left[0] + width, top_left[1] + height)

            output = output[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]

            match_name = names[math.floor((bottom_right[1] - 50) / 100)]
            node_id = f"{i}_{match_name}"
            nodes.append(Node(node_id, match_name, 9999, (x, y), True, False, False).get_tuple())
            valid_circles[circle] = node_id

            i += 1

            # cv2.imshow("unlockable from screen", unlockable)
            # cv2.imshow(f"matched unlockable", output)
            # cv2.waitKey(0)

        # cv2.destroyAllWindows()

        nodes.append(Node("ORIGIN", "ORIGIN", 9999, origin, True, False, False).get_tuple())

        # actual edges joining circles
        edges = []
        for (circle1, circle2) in connections:
            edges.append((valid_circles[circle1], valid_circles[circle2]))

        # construct networkx graph
        self.graph = nx.Graph()
        self.graph.add_nodes_from(nodes)
        self.graph.add_edges_from(edges)

        net = Network(notebook=True, height=1080, width=1920)
        net.from_nx(self.graph)

        net.show("matcher.html")



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
        cv2.waitKey(0)
        cv2.destroyAllWindows()'''

class CircleMatcher:
    def __init__(self, path_base, circle_blur, hough_1, hough_2):
        path_base = "training_data/bases/" + path_base
        base = cv2.imread(path_base, cv2.IMREAD_GRAYSCALE)
        base_c = cv2.GaussianBlur(base, (circle_blur, circle_blur), sigmaX=0, sigmaY=0) # circles
        output = base_c.copy()

        np.set_printoptions(threshold=np.inf)

        # detect circles in the image
        circles = cv2.HoughCircles(base_c, cv2.HOUGH_GRADIENT, dp=1, minDist=80, param1=hough_1, param2=hough_2,
                                   minRadius=7, maxRadius=50)

        self.circles = []
        if circles is not None:
            circles = np.round(circles[0, :]).astype("int")
            for (x, y, r) in circles:
                cv2.circle(output, (x, y), r, 255, 4)
                self.circles.append((x, y, r))

        self.output = output
