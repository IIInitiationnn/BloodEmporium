import cv2
import numpy as np

from utils.image_util import ImageUtil

"""
Offerings | Killer + Survivor | Hexagon | C:/Program Files (x86)/Steam/steamapps/common/Dead by Daylight/DeadByDaylight/Content/UI/Icons/Favors
Addons    | Killer + Survivor | Square  | C:/Program Files (x86)/Steam/steamapps/common/Dead by Daylight/DeadByDaylight/Content/UI/Icons/ItemAddons
Items     | Survivor          | Square  | C:/Program Files (x86)/Steam/steamapps/common/Dead by Daylight/DeadByDaylight/Content/UI/Icons/Items
Perks     | Killer + Survivor | Diamond | C:/Program Files (x86)/Steam/steamapps/common/Dead by Daylight/DeadByDaylight/Content/UI/Icons/Perks
"""

"""
cv2.IMREAD_COLOR
cv2.IMREAD_GRAYSCALE
cv2.IMREAD_UNCHANGED
"""

class Matcher:
    def __init__(self, debugger, cv_images, res):
        self.debugger = debugger
        self.cv_images = cv_images
        self.res = res

    @staticmethod
    def get_circle_properties(debugger, image_gray, image_bgr, image_filtered, merged_base, abs_position, res):
        ur = res.unlockable_radius()

        square = image_filtered[abs_position.y-ur:abs_position.y+ur, abs_position.x-ur:abs_position.x+ur]

        # identify if large (unclaimed) node exists
        circles = cv2.HoughCircles(square, cv2.HOUGH_GRADIENT, dp=1, minDist=res.min_dist(), param1=10,
                                   param2=45, minRadius=res.detect_radius(), maxRadius=res.detect_radius() + 20)
        if circles is None:
            x, y, r = abs_position.x, abs_position.y, res.small_node_inner_radius()

            # identify color
            unlockable = ImageUtil.cut_circle(image_bgr, (x, y), r)
            color = ImageUtil.dominant_color(unlockable)
            if color != "red":
                return None, None, None
            return r, color, "CLAIMED"
        else:
            # convert the (x, y) coordinates and radius of the circles to integers
            circles = np.round(circles[0, :]).astype("int")
            if len(circles) > 1 or circles[0][2] < res.threshold_radius():
                pass # TODO throw error
            r = res.large_node_inner_radius()
            # cv2.circle(square, (circles[0][0], circles[0][1]), r, 255, thickness=1)
            # cv2.imshow("square", square) # hhhhh
            # cv2.waitKey(0)

            # identify color
            unlockable = ImageUtil.cut_circle(image_bgr, (abs_position.x, abs_position.y), r)
            color = ImageUtil.dominant_color(unlockable)
            if color != "taupe" and color != "neutral":
                return None, None, None # TODO threw error

            # identify unlockable
            r_small = r * 2 // 3
            unlockable = image_gray[abs_position.y-r_small:abs_position.y+r_small,
                                    abs_position.x-r_small:abs_position.x+r_small]
            height, width = unlockable.shape

            # only need radius and color
            if merged_base is None:
                return r, color, None

            names = merged_base.names
            images = merged_base.images

            # apply template matching
            base = images.copy()
            result = cv2.matchTemplate(base, unlockable, cv2.TM_CCOEFF_NORMED)
            # result = cv2.matchTemplate(base, unlockable, cv2.TM_CCORR_NORMED)

            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

            top_left = max_loc
            bottom_right = (top_left[0] + width, top_left[1] + height)
            match = base[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]

            if debugger is not None:
                debugger.add_icon(unlockable, match)

            match_unique_id = names[round((bottom_right[1] - merged_base.full_dim / 2) / merged_base.full_dim)]
            return r, color, match_unique_id