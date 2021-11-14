import math
import os

import cv2
import numpy as np

import paths
from images import Images
from resolution import Resolution


class MergedBase:
    def __init__(self, res, category=None):
        '''
        :param category: can be used to reduce the number of valid images needed to be drawn from
        '''

        self.res = res

        # TODO implement category

        valid_names = []
        valid_images = [] # 256 x 256

        n, i = self.__get_valid_images(paths.offerings_path, "Favor")
        valid_names.extend(n)
        valid_images.extend(i)

        n, i = self.__get_valid_images(paths.addons_path, "Addon")
        valid_names.extend(n)
        valid_images.extend(i)

        n, i = self.__get_valid_images(paths.items_path, "Items")
        valid_names.extend(n)
        valid_images.extend(i)

        n, i = self.__get_valid_images(paths.perks_path, "Perks")
        valid_names.extend(n)
        valid_images.extend(i)

        self.names = valid_names
        self.images = cv2.vconcat(valid_images)
        cv2.imwrite("output/collage.png", self.images)

    def __get_valid_images(self, path, required_prefix):
        invalid = ["iconItems_carriedBody.png",
                   "iconFavors_graduationCap.png",
                   "iconFavors_5thAnniversary.png",
                   "iconFavors_StampedPostcard.png",
                   "iconFavors_ThornDoll.png",
                   "iconFavors_WoodenChalice.png",
                   "iconFavors_BlackTea.png",
                   "iconFavors_BlankPostcard.png",
                   "iconFavors_BloodstoneChalice.png",
                   "iconFavors_BoneDoll.png",
                   "iconFavors_BurdockTea.png",
                   "iconFavors_CeramicChalice.png",
                   "iconFavors_ClayDoll.png",
                   "iconFavors_CopperChalice.png",
                   "iconFavors_CrumpledPostcard.png",
                   "iconFavors_FleshDoll.png",
                   "iconFavors_LotusLeafTea.png",
                   "iconFavors_LoversPostcard.png",
                   "iconFavors_MilkTea.png"]

        full_dim = round(1.2 * self.res.perks())
        if required_prefix == "Favor":
            dim = self.res.offerings()
        elif required_prefix == "Perks":
            dim = self.res.perks()
        else:
            dim = self.res.items_addons()

        ret_names = []
        ret_images = []
        for subdir, dirs, files in os.walk(path):
            for file in files:
                if required_prefix in file and file not in invalid:
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

                    border1 = math.floor((full_dim - dim) / 2)
                    border2 = math.ceil((full_dim - dim) / 2)
                    template = cv2.copyMakeBorder(template, border1, border2, border1, border2, cv2.BORDER_CONSTANT, value=0)

                    ret_names.append(file)
                    ret_images.append(template)
        return ret_names, ret_images