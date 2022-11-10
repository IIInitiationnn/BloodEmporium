import cv2
import numpy as np

from resolution import Resolution
from utils.color_util import ColorUtil


class ImageUtil:
    @staticmethod
    def cut_circle(image, centre, radius):
        """
        :param image: 3 layer bgr image
        :param centre:
        :param radius:
        :return: BGR image
        """
        height, width, _ = image.shape
        masked_data = image.copy()

        # white mask with black center to remove perk information in the centre
        mask = np.zeros((height, width), np.uint8)
        color = 255
        mask[:] = color
        cv2.circle(mask, centre, radius, (0, 0, 0), thickness=-1)
        masked_data[mask == 0] = (255, 255, 255)

        # black mask with white center to remove everything outside
        full_radius = radius + round(Resolution.additional_radius(radius) * 5 / 6)
        mask = np.zeros((height, width), np.uint8)
        cv2.circle(mask, centre, full_radius, (255, 255, 255), thickness=-1)
        masked_data[mask == 0] = (255, 255, 255)

        x, y = centre
        unlockable = masked_data[max(y-full_radius, 0):min(y+full_radius, height),
                                 max(x-full_radius, 0):min(x+full_radius, width)]
        unlockable = cv2.cvtColor(unlockable, cv2.COLOR_BGRA2BGR)

        # cv2.imshow("masked", masked_data)
        # cv2.imshow("color", unlockable)

        return unlockable

    @staticmethod
    def dominant_color(image):
        pixels = np.float32(image.reshape(-1, 3))

        n_colors = 5
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 200, .1)
        flags = cv2.KMEANS_RANDOM_CENTERS

        _, labels, palette = cv2.kmeans(pixels, n_colors, None, criteria, 10, flags)
        _, counts = np.unique(labels, return_counts=True)

        freqs = []
        for i in range(n_colors):
            freqs.append((palette[i].astype(np.int), counts[i]))

        freqs.sort(key=lambda pair: pair[1], reverse=True)

        for color, _ in freqs:
            if sum(color) == 765: # white
                continue

            # display = np.zeros((100, 100, 3), np.uint8)
            # display[:] = tuple(color)
            # cv2.imshow("matched color", display)

            closest = ImageUtil.closest_color(tuple(color)[::-1]) # bgr -> rgb
            if closest is not None:
                return closest

        return None

    @staticmethod
    def closest_color(color):
        taupe_delta = ColorUtil.diff(ColorUtil.taupe_rgb, color)
        red_delta = ColorUtil.diff(ColorUtil.red_rgb, color)
        neutral_delta = ColorUtil.diff(ColorUtil.neutral_rgb, color)
        black_delta = ColorUtil.diff(ColorUtil.black_rgb, color)

        # didnt match any
        if min(taupe_delta, red_delta, neutral_delta, black_delta) > 50000:
            return None

        # cv2.waitKey(0)

        results = {"taupe": taupe_delta, "red": red_delta, "neutral": neutral_delta, "black": black_delta}
        return min(results, key=results.get)