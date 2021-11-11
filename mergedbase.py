import math
import os

import cv2

import paths


class MergedBase:
    def __init__(self, category=None):
        '''
        :param category: can be used to reduce the number of valid images needed to be drawn from
        '''

        # TODO implement category

        valid_names = []
        valid_images = [] # 256 x 256

        n, i = MergedBase.__get_valid_images(paths.offerings_path, "Favor")
        valid_names.extend(n)
        valid_images.extend(i)

        n, i = MergedBase.__get_valid_images(paths.addons_path, "Addon")
        valid_names.extend(n)
        valid_images.extend(i)

        n, i = MergedBase.__get_valid_images(paths.items_path, "Items")
        valid_names.extend(n)
        valid_images.extend(i)

        n, i = MergedBase.__get_valid_images(paths.perks_path, "Perks")
        valid_names.extend(n)
        valid_images.extend(i)

        self.names = valid_names
        self.images = cv2.vconcat(valid_images)
        cv2.imwrite("collage.png", self.images)

    @staticmethod
    def __get_valid_images(path, required_prefix):
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

        dim = 54

        if required_prefix == "Favor":
            dim = 68
        elif required_prefix == "Perks":
            dim = 67

        ret_names = []
        ret_images = []
        for subdir, dirs, files in os.walk(path):
            for file in files:
                if required_prefix in file and file not in invalid:
                    template = cv2.imread(os.path.join(subdir, file), cv2.IMREAD_GRAYSCALE)
                    template = cv2.resize(template, (dim, dim), interpolation=cv2.INTER_AREA) # configure in config, should be some default according to resolutions; diff for square vs hexagon vs diamond

                    full_dim = 100
                    border1 = math.floor((full_dim - dim) / 2)
                    border2 = math.ceil((full_dim - dim) / 2)
                    template = cv2.copyMakeBorder(template, border1, border2, border1, border2, cv2.BORDER_CONSTANT, value=0)

                    ret_names.append(file)
                    ret_images.append(template)
        return ret_names, ret_images