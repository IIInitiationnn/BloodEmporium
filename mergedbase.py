import math
import os

import cv2
import numpy as np

from config import Config
from paths import Path
from categories import Categories
from images import Images


class MergedBase:
    def __init__(self, res, category=None, retired=False):
        '''
        :param category: can be used to reduce the number of valid images needed to be drawn from
                         is one of Categories.killers or "survivor"
        '''

        categories = ["universal"]
        if category in Categories.killers:
            # particular killer
            categories.append("killer")
            categories.append(category)
        else:
            # any survivor
            categories.append("survivor")

        if retired:
            categories.append("retired")

        self.res = res
        self.full_dim = round(1 + self.res.mystery_box())

        path = Config().path() # user's default folder for icons; could be custom icons
        all_files = [(subdir, file) for subdir, dirs, files in os.walk(path) for file in files]
        image_paths = []
        for category, unlockable in Categories.categories_as_tuples(categories):
            # search in user's folder
            found = False
            for subdir, file in all_files:
                if unlockable in file:
                    image_paths.append(os.path.join(subdir, file))
                    found = True
                    break
            if found:
                continue

            # search in asset folder
            asset_path = Path.assets_file(category, unlockable)
            if os.path.isfile(asset_path):
                image_paths.append(os.path.abspath(asset_path))
            else:
                print(f"no source found for desired unlockable: {unlockable} under category: {category}")

        valid_names, valid_images = self.__get_valid_images(image_paths)

        self.names = valid_names
        self.images = cv2.vconcat(valid_images)

    def __get_valid_images(self, image_paths):
        ret_names = []
        ret_images = []
        for file in image_paths:
            image_name = file.split("/")[-1]

            if "mysteryBox" in image_name:
                dim = self.res.mystery_box()
            elif "Favors" in image_name:
                dim = self.res.offerings()
            elif "Perks" in image_name:
                dim = self.res.perks()
            elif "Addon" in image_name or "Items" in image_name:
                dim = self.res.items_addons()
            else:
                print(f"error merging base with {file}")
                continue

            template = cv2.imread(file, cv2.IMREAD_UNCHANGED)
            template_alpha = template[:, :, 3] / 255.0
            bg_alpha = 1 - template_alpha

            gray_bg = np.zeros((256, 256, 3), np.uint8)
            color = (125, 125, 125)
            gray_bg[:] = color

            for layer in range(3):
                gray_bg[:, :, layer] = template_alpha * template[:, :, layer] + bg_alpha * gray_bg[:, :, layer]

            template = cv2.cvtColor(gray_bg, cv2.COLOR_BGR2GRAY)
            template = cv2.resize(template, (dim, dim), interpolation=Images.interpolation)

            border1 = math.floor((self.full_dim - dim) / 2)
            border2 = math.ceil((self.full_dim - dim) / 2)
            template = cv2.copyMakeBorder(template, border1, border2, border1, border2, cv2.BORDER_CONSTANT, value=0)

            ret_names.append(file.split("\\")[-1])
            ret_images.append(template)

        """for subdir, dirs, files in os.walk(path):
            for file in files:
                if required_prefix in file:
                    template = cv2.imread(os.path.join(subdir, file), cv2.IMREAD_UNCHANGED)
                    template_alpha = template[:, :, 3] / 255.0
                    bg_alpha = 1 - template_alpha

                    gray_bg = np.zeros((256, 256, 3), np.uint8)
                    color = (125, 125, 125)
                    gray_bg[:] = color

                    for layer in range(3):
                        gray_bg[:, :, layer] = template_alpha * template[:, :, layer] + bg_alpha * gray_bg[:, :, layer]

                    template = cv2.cvtColor(gray_bg, cv2.COLOR_BGR2GRAY)
                    template = cv2.resize(template, (dim, dim), interpolation=Images.interpolation)

                    border1 = math.floor((self.full_dim - dim) / 2)
                    border2 = math.ceil((self.full_dim - dim) / 2)
                    template = cv2.copyMakeBorder(template, border1, border2, border1, border2, cv2.BORDER_CONSTANT, value=0)

                    ret_names.append(file)
                    ret_images.append(template)"""
        return ret_names, ret_images