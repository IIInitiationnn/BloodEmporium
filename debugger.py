import os
from datetime import datetime

import cv2

from paths import Path
from utils.network_util import NetworkUtil

class Debugger:
    def __init__(self, cv_images, write_to_output):
        self.cv_images = cv_images
        self.write_to_output = write_to_output

        self.iteration = 0
        self.time = datetime.now().strftime("%d-%m-%y %H-%M-%S")
        self.all_lines = []

        if self.write_to_output:
            os.mkdir(f"output/{self.time}")
            for i in range(len(self.cv_images)):
                cv2.imwrite(f"output/{self.time}/image_{i}.png", self.cv_images[i].get_bgr())

    # match origin
    def set_cropped(self, cropped):
        self.cropped = cropped

    def set_origin_type(self, origin_type):
        self.origin_type = origin_type

    def set_origin(self, origin):
        self.origin = origin # (x, y), r, color

    # match circles
    def set_all_circles(self, all_circles):
        self.all_circles = all_circles # (x, y), r

    def set_valid_circles(self, valid_circles):
        self.valid_circles = valid_circles # (x, y), r, color

    # match lines
    def set_edges(self, edges):
        self.edges = edges

    def add_line(self, line):
        self.all_lines.append(line)

    def set_valid_lines(self, valid_lines):
        self.valid_lines = valid_lines

    def set_merger(self, merger):
        self.merger = merger
        if self.write_to_output:
            cv2.imwrite(f"output/{self.time}/collage.png", self.merger.images)
        return self

    def set_hough(self, hough):
        self.hough = hough
        if self.write_to_output:
            cv2.imwrite(f"output/{self.time}/edges_{self.iteration}.png", self.hough.edges)
        self.iteration += 1
        return self

    def set_matcher(self, matcher):
        self.matcher = matcher
        if self.write_to_output:
            NetworkUtil.write_to_html(self.matcher.graph, f"output/{self.time}/base_bloodweb_{self.iteration}.png")
        return self

    def set_optimiser(self, optimiser, j):
        self.optimiser = optimiser
        if self.write_to_output:
            NetworkUtil.write_to_html(optimiser.dijkstra_graph, f"output/{self.time}/dijkstra_{self.iteration}_{j}.png")
        return self

    def show_images(self):
        # hough
        cv2.imshow("cropped for origin matching", self.cropped)
        cv2.imshow("matched origin", cv2.split(cv2.imread(f"{Path.assets_origins}/{self.origin_type}", cv2.IMREAD_UNCHANGED))[2])
        cv2.imshow("edges for matching lines", self.edges)

        # TODO one for each image: show each one individually & same with writing images
        raw_output = self.cv_images[0].get_gray().copy()
        cv2.circle(raw_output, self.origin[0], self.origin[1], 255, 4)
        for (x, y), r in self.all_circles:
            cv2.circle(raw_output, (x, y), r, 255, 2)
            cv2.rectangle(raw_output, (x - 5, y - 5), (x + 5, y + 5), 255, -1)
        for (x1, y1), (x2, y2) in self.all_lines:
            cv2.line(raw_output, (x1, y1), (x2, y2), 255, 2)
        cv2.imshow("unfiltered raw output (r-adjusted)", raw_output)

        validated_output = self.cv_images[0].get_gray().copy()
        cv2.circle(validated_output, self.origin[0], self.origin[1], 255, 4)
        for (x, y), r, _ in self.valid_circles:
            cv2.circle(validated_output, (x, y), r, 255, 2)
            cv2.rectangle(validated_output, (x - 5, y - 5), (x + 5, y + 5), 255, -1)
        for circle1, circle2 in self.valid_lines:
            cv2.line(validated_output, circle1[0], circle2[0], 255, 2)
        cv2.imshow("validated & processed output (r-adjusted)", validated_output)

        cv2.waitKey(0)

        # matcher
        '''for screen, matched in self.matcher.output:
            cv2.imshow("unlockable from screen", screen)
            cv2.imshow(f"matched unlockable", matched)
            cv2.waitKey(0)'''
