from datetime import datetime

import cv2
import os

from PIL.Image import Image

from paths import Path
from utils.network_util import NetworkUtil


class Debug:
    def __init__(self, write_to_output=True):
        self.i = 0
        self.time = datetime.now().strftime("%d-%m-%y %H-%M-%S")
        self.write_to_output = write_to_output
        if self.write_to_output:
            os.mkdir(f"output/{self.time}")
        pass

    def set_merger(self, merger):
        self.merger = merger
        if self.write_to_output:
            cv2.imwrite(f"output/{self.time}/collage.png", self.merger.images)
        return self

    def set_image(self, image):
        self.image = image
        if self.write_to_output:
            Image.save(self.image, f"output/{self.time}/image_{self.i}.png")
        return self

    def set_hough(self, hough):
        self.hough = hough
        if self.write_to_output:
            cv2.imwrite(f"output/{self.time}/edges_{self.i}.png", self.hough.edges)
        self.i += 1
        return self

    def set_matcher(self, matcher):
        self.matcher = matcher
        if self.write_to_output:
            NetworkUtil.write_to_html(self.matcher.graph, f"output/{self.time}/base_bloodweb_{self.i}.png")
        return self

    def set_optimiser(self, optimiser, j):
        self.optimiser = optimiser
        if self.write_to_output:
            NetworkUtil.write_to_html(optimiser.dijkstra_graph, f"output/{self.time}/dijkstra_{self.i}_{j}.png")
        return self

    def show_images(self):
        # hough
        cv2.imshow("cropped for origin matching", self.hough.cropped)
        cv2.imshow("matched origin", cv2.split(cv2.imread(f"{Path.assets_origins}/{self.hough.origin_type}", cv2.IMREAD_UNCHANGED))[2])
        cv2.imshow("edges for matching lines", self.hough.edges)
        cv2.imshow("unfiltered raw output (r-adjusted)", self.hough.output)
        cv2.imshow("validated & processed output (r-adjusted)", self.hough.output_validated)
        cv2.waitKey(0)

        # matcher
        '''for screen, matched in self.matcher.output:
            cv2.imshow("unlockable from screen", screen)
            cv2.imshow(f"matched unlockable", matched)
            cv2.waitKey(0)'''
