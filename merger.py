import os
from pprint import pprint

import cv2
import numpy
from PIL import Image

from matcher import Matcher

class Merger:
    def __init__(self):
        valid_images = [] # 256 x 256
        valid_images.extend(Merger.__get_valid_images(Matcher.offerings_path, "Favor"))
        valid_images.extend(Merger.__get_valid_images(Matcher.addons_path, "Addon"))
        valid_images.extend(Merger.__get_valid_images(Matcher.items_path, "Items"))
        valid_images.extend(Merger.__get_valid_images(Matcher.perks_path, "Perks"))

        cv2.imwrite("collage.png", cv2.vconcat(valid_images))

    @staticmethod
    def __get_valid_images(path, required_prefix):
        dim = 50

        if required_prefix == "Favor":
            dim = 70
        elif required_prefix == "Perks":
            dim = 67

        ret = {}
        for subdir, dirs, files in os.walk(path):
            for file in files:
                if required_prefix in file:
                    template = cv2.imread(file, cv2.IMREAD_GRAYSCALE)
                    template = cv2.resize(template, (dim, dim), interpolation=cv2.INTER_AREA) # configure in config, should be some default according to resolutions; diff for square vs hexagon vs diamond
                    ret[file] = template
        return ret