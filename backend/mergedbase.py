import cv2
import numpy as np

from backend.resolution import Resolution
from data import Data
from image import Image


class MergedBase:
    def __init__(self, category=None, retired=False):
        """
        :param category: can be used to reduce the number of valid images needed to be drawn from
                         is one of Categories.killers or "survivor"
        """

        categories = ["universal"]
        if category in [killer_id for killer_id, _, _ in Data.get_killers(False)]:
            # particular killer
            categories.append("killer")
            categories.append(category)
        else:
            # any survivor
            categories.append("survivor")

        if retired:
            categories.append("retired")

        unlockables = [unlockable for unlockable in Data.get_unlockables() if unlockable.category in categories]

        self.size = 64
        self.names, self.valid_images = self.__get_valid_images(unlockables)
        self.images = cv2.vconcat(self.valid_images)
        self.keypoints, self.descriptors = None, None
        # sift_extractor = cv2.SIFT_create()
        # self.keypoints, self.descriptors = sift_extractor.detectAndCompute(self.images, None)
        # orb_extractor = cv2.ORB_create()
        # self.keypoints, self.descriptors = orb_extractor.detectAndCompute(self.images, None)

    def __get_valid_images(self, unlockables):
        ret_names = []
        ret_images = []

        colors = {
            "common": (60, 60, 60),
            "uncommon": (100, 100, 100),
            "rare": (75, 75, 75),
            "very_rare": (45, 45, 45),
            "ultra_rare": (40, 40, 40),
            "event": (170, 170, 170),
            "varies": (125, 125, 125),
        }

        for unlockable in unlockables:
            image_path = unlockable.image_path
            image_name = image_path.split("\\")[-1]

            if "mysteryBox" in image_name:
                dim = round(Resolution.mystery_box * self.size)
            elif "Favors" in image_name:
                dim = round(Resolution.offerings * self.size)
            elif "Perks" in image_name:
                dim = round(Resolution.perks * self.size)
            elif "Addon" in image_name or "Items" in image_name:
                dim = round(Resolution.items_addons * self.size)
            else:
                print(f"error merging base with {image_path}")
                continue

            margin = (dim - self.size) // 2

            template = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
            template = cv2.resize(template, (dim, dim), interpolation=Image.interpolation)
            template = template[margin:(margin + self.size), margin:(margin + self.size)]

            # no alpha channel (rgb instead of rgba) - note: alpha=0 denotes full transparency
            template_alpha = template[:, :, 3] / 255.0 if template.shape[2] == 4 else 1 - template[:, :, 0] * 0
            bg_alpha = 1 - template_alpha

            gray_bg = np.zeros((self.size, self.size, 3), np.uint8)
            color = colors[unlockable.rarity]
            gray_bg[:] = color

            for layer in range(3):
                gray_bg[:, :, layer] = template_alpha * template[:, :, layer] + bg_alpha * gray_bg[:, :, layer]

            template = cv2.cvtColor(gray_bg, cv2.COLOR_BGR2GRAY)

            ret_names.append(unlockable.unique_id)
            ret_images.append(template)
        return ret_names, ret_images