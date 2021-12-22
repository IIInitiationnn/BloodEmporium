import os

import cv2

from images import Images
from paths import Path
from utils.network_util import NetworkUtil


class Debugger:
    def __init__(self, cv_images, timestamp, i, write_to_output=False):
        self.cv_images = cv_images
        self.write_to_output = write_to_output

        self.i = i
        self.time = timestamp.strftime("%d-%m-%y %H-%M-%S")
        self.all_circles = []
        self.icons = []
        self.edge_images = []
        self.all_lines = {}

        if self.write_to_output:
            if not os.path.isdir(f"output/{self.time}"):
                os.mkdir(f"output/{self.time}")
            if not os.path.isdir(f"output/{self.time}/{i}"):
                os.mkdir(f"output/{self.time}/{i}")
            for j in range(len(self.cv_images)):
                cv2.imwrite(f"output/{self.time}/{i}/initial_image_{j}.png", self.cv_images[j].get_bgr())

    # merger
    def set_merger(self, merger):
        if self.write_to_output:
            cv2.imwrite(f"output/{self.time}/collage.png", merger.images)
        return self

    # match origin
    def set_cropped(self, cropped):
        self.cropped = cropped

    def set_origin_type(self, origin_type):
        self.origin_type = origin_type

    def set_origin(self, origin):
        self.origin = origin

    # match circles
    def set_valid_circles(self, valid_circles):
        self.valid_circles = valid_circles

    # match icons
    def add_icon(self, from_screen, matched):
        self.icons.append((from_screen, matched))

    # match lines
    def add_edge_image(self, edges):
        self.edge_images.append(edges)
        if self.write_to_output:
            index = len(self.edge_images) - 1
            cv2.imwrite(f"output/{self.time}/{self.i}/edges_{index}.png", self.edge_images[index])

    def add_line(self, num, line):
        if self.all_lines.get(num) is None:
            self.all_lines[num] = []
        self.all_lines[num].append(line)

    def set_connections(self, connections):
        self.connections = connections

    # grapher
    def set_base_bloodweb(self, base_bloodweb):
        if self.write_to_output:
            NetworkUtil.write_to_html(base_bloodweb, f"output/{self.time}/{self.i}/base_bloodweb")
        return self

    # optimiser
    def set_dijkstra(self, dijkstra_graph, j):
        if self.write_to_output:
            NetworkUtil.write_to_html(dijkstra_graph, f"output/{self.time}/{self.i}/dijkstra_{j}")
        return self

    # updated image
    def add_updated_image(self, updated_image, j):
        if self.write_to_output:
            cv2.imwrite(f"output/{self.time}/{self.i}/updated_image_{j}.png", updated_image)
        return self

    def show_images(self):
        # hough
        cv2.imshow("cropped for origin matching", self.cropped)
        cv2.imshow("matched origin", cv2.split(cv2.imread(f"{Path.assets_origins}/{self.origin_type}", cv2.IMREAD_UNCHANGED))[2])

        for i in range(len(self.cv_images)):
            raw_output = self.cv_images[i].get_gray().copy()
            cv2.circle(raw_output, (self.origin.x(), self.origin.y()), self.origin.radius, 255, 4)
            for circle in self.valid_circles:
                if circle.is_origin:
                    continue
                x = circle.x()
                y = circle.y()
                r = circle.radius
                cv2.circle(raw_output, (x, y), r, 255, 2)
                cv2.rectangle(raw_output, (x - 5, y - 5), (x + 5, y + 5), 255, -1)
            for line in self.all_lines[i]:
                x1, y1, x2, y2 = line.positions()
                cv2.line(raw_output, (x1, y1), (x2, y2), 255, 2)

            if self.write_to_output:
                cv2.imwrite(f"output/{self.time}/{self.i}/raw_output_{i}.png", raw_output)

            cv2.imshow("unfiltered raw output (r-adjusted)", raw_output)
            cv2.imshow("edges for matching lines", self.edge_images[i])
            cv2.waitKey(0)

        validated_output = self.cv_images[0].get_gray().copy()
        cv2.circle(validated_output, (self.origin.x(), self.origin.y()), self.origin.radius, 255, 4)
        for circle in self.valid_circles:
            if circle.is_origin:
                continue
            x = circle.x()
            y = circle.y()
            r = circle.radius
            cv2.circle(validated_output, (x, y), r, 255, 2)
            cv2.rectangle(validated_output, (x - 5, y - 5), (x + 5, y + 5), 255, -1)
        for connection in self.connections:
            cv2.line(validated_output, (connection.circle1.x(), connection.circle1.y()),
                     (connection.circle2.x(), connection.circle2.y()), 255, 1)
        cv2.imshow("validated & processed output (r-adjusted)", validated_output)
        cv2.waitKey(0)

        # matcher
        for from_screen, matched in self.icons:
            cv2.imshow("unlockable from screen", cv2.resize(from_screen, (200, 200), interpolation=Images.interpolation))
            cv2.imshow(f"matched unlockable", cv2.resize(matched, (200, 200), interpolation=Images.interpolation))
            cv2.waitKey(0)

        cv2.destroyAllWindows()