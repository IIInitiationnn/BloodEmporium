import math

import cv2
import cv2.cv2
import numpy as np

from utils.distance_util import close_proximity_circle_to_circle, close_proximity_line_to_circle

'''
Offerings | Killer + Survivor | Hexagon | C:/Program Files (x86)/Steam/steamapps/common/Dead by Daylight/DeadByDaylight/Content/UI/Icons/Favors
Addons    | Killer + Survivor | Square  | C:/Program Files (x86)/Steam/steamapps/common/Dead by Daylight/DeadByDaylight/Content/UI/Icons/ItemAddons
Items     | Survivor          | Square  | C:/Program Files (x86)/Steam/steamapps/common/Dead by Daylight/DeadByDaylight/Content/UI/Icons/Items
Perks     | Killer + Survivor | Diamond | C:/Program Files (x86)/Steam/steamapps/common/Dead by Daylight/DeadByDaylight/Content/UI/Icons/Perks
'''

'''
cv2.IMREAD_COLOR
cv2.IMREAD_GRAYSCALE
cv2.IMREAD_UNCHANGED
'''

# TODO mystery boxes in assets folder

class Matcher:
    image_path = "/mnt/c/Program Files (x86)/Steam/steamapps/common/Dead by Daylight/DeadByDaylight/Content/UI/Icons" # diff for win and mac, but in development we use linux
    offerings_path = image_path + "/Favors" # 70, 50
    addons_path = image_path + "/ItemAddons" # 50, 40
    items_path = image_path + "/Items" # 50, 40
    perks_path = image_path + "/Perks" # 67, 51

    def __init__(self):
        # path_example = Matcher.offerings_path + "/iconFavors_jarOfSaltyLips.png"
        # path_example = Matcher.items_path + "/iconItems_firstAidKit.png"
        # path_example = Matcher.offerings_path + "/iconFavors_bogLaurelSachet.png"
        path_example = Matcher.offerings_path + "/Yemen/iconFavors_annotatedBlueprint.png"
        # path_example = Matcher.offerings_path + "/iconFavors_spottedOwlWreath.png"
        # path_example = Matcher.offerings_path + "/iconFavors_scratchedCoin.png"
        # path_example = Matcher.addons_path + "/iconAddon_metalSpoon.png"
        # path_example = Matcher.addons_path + "/iconAddon_butterflyTape.png"
        # path_example = Matcher.offerings_path + "/Anniversary/iconsFavors_5thAnniversary.png"
        # path_example = Matcher.perks_path + "/Qatar/iconPerks_camaraderie.png"
        # path_example = Matcher.perks_path + "/Qatar/iconPerks_babySitter.png"
        # path_example = Matcher.items_path + "/iconItems_toolbox.png"
        path_base = "training_data/bases/"
        path_base += "base.png"
        # path_base += "base_larger.png"
        # path_base += "base_claud.png"

        dim = 50

        np.set_printoptions(threshold=np.inf)
        template = cv2.imread(path_example, cv2.IMREAD_GRAYSCALE)
        template = cv2.resize(template, (dim, dim), interpolation=cv2.INTER_AREA) # configure in config, should be some default according to resolutions; diff for square vs hexagon vs diamond
        template_alpha = cv2.resize(cv2.split(cv2.imread(path_example, cv2.IMREAD_UNCHANGED))[3], (dim, dim), interpolation=cv2.INTER_AREA) # for masking

        base = cv2.imread(path_base, cv2.IMREAD_GRAYSCALE)

        height, width = template.shape

        # apply template matching
        output = base.copy()
        method = "cv2.TM_CCORR_NORMED"
        result = cv2.matchTemplate(output, template, eval(method), mask=template_alpha)

        single_match = True

        if single_match:
            # single match
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

            top_left = max_loc
            bottom_right = (top_left[0] + width, top_left[1] + height)
            cv2.rectangle(output, top_left, bottom_right, 255, 2) # 255 = white; 2 = thickness
        else:
            # multiple matches
            threshold = 0.95 # larger value = better match / fit
            loc = np.where(result >= threshold)

            matches = []
            for top_left in zip(*loc[::-1]):
                bottom_right = (top_left[0] + width, top_left[1] + height)
                if not any([close_proximity_circle_to_circle(tl, top_left) and close_proximity_circle_to_circle(br, bottom_right) for (tl, br) in matches]):
                    matches.append((top_left, bottom_right))
                    cv2.rectangle(output, top_left, bottom_right, 255, 2) # 255 = white; 2 = thickness

        cv2.imshow(method, output)
        cv2.waitKey(0)

        cv2.imshow('Image', template)
        cv2.imshow('Base', base)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

class GraphMatcher:
    def __init__(self):
        path_base = "training_data/bases/"
        path_base += "base.png"
        # path_base += "base_claud.png"
        # path_base += "base_larger.png"
        base = cv2.imread(path_base, cv2.IMREAD_GRAYSCALE)

        base_c = cv2.GaussianBlur(base, (11, 11), sigmaX=0, sigmaY=0) # circles
        base_l = cv2.GaussianBlur(base, (5, 5), sigmaX=0, sigmaY=0) # lines
        # base_l = cv2.GaussianBlur(cv2.split(cv2.imread(path_base, cv2.IMREAD_COLOR))[0], (5, 5), sigmaX=0, sigmaY=0) # lines
        output = base.copy()

        np.set_printoptions(threshold=np.inf)

        edges = cv2.Canny(base_l, 85, 40)

        # detect circles in the image
        circles = cv2.HoughCircles(base_c, cv2.HOUGH_GRADIENT, dp=1, minDist=80, param1=10, param2=45, minRadius=7, maxRadius=50)

        # TODO need to add origin: use asset and template matching for origin

        centres = []
        if circles is not None:
            # convert the (x, y) coordinates and radius of the circles to integers
            circles = np.round(circles[0, :]).astype("int")

            # loop over the (x, y) coordinates and radius of the circles
            for (x, y, r) in circles:
                # draw the circle in the output image, then draw a rectangle
                # corresponding to the center of the circle
                cv2.circle(output, (x, y), r, 255, 4)
                cv2.rectangle(output, (x - 5, y - 5), (x + 5, y + 5), 255, -1)

                # remove the node from the edges graph
                cv2.circle(edges, (x, y), 1, 0, math.floor(r / 1.9) + 55) # tweak size of circle removal
                centres.append((x, y, r))

        # origin: manual for now for base.png
        cv2.circle(output, (650, 773), 23, 255, 4)
        cv2.circle(edges, (650, 773), 1, 0, math.floor(23 / 1.9) + 55) # tweak size of circle removal
        centres.append((650, 773, 23))

        lines = cv2.HoughLinesP(edges, rho=1, theta=np.pi / 180, threshold=30, minLineLength=25, maxLineGap=25)
        # lines = cv2.HoughLinesP(edges, rho=1, theta=np.pi / 180, threshold=55, minLineLength=25, maxLineGap=30) # tinkering to get base working

        ''' parameters that can be tweak to improve line detection:
            threshold
            maxlinegap
            canny params (first is minimum, second is maximum)
            gaussian blur'''

        self.lines = []
        for line in lines:
            x1, y1, x2, y2 = line[0]
            if any([close_proximity_line_to_circle(centre, (x1, y1)) for centre in centres]) and\
                    any([close_proximity_line_to_circle(centre, (x2, y2)) for centre in centres]):
                # TODO evaluate which nodes it is joining

                cv2.line(output, (x1, y1), (x2, y2), 255, 5)
                self.lines.append(((x1, y1), (x2, y2)))

        cv2.imshow("edges", edges)
        cv2.imshow("output", output)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        self.circles = centres # list of (x, y, r)

class CircleMatcher:
    def __init__(self, path_base, circle_blur, hough_1, hough_2):
        path_base = "training_data/bases/" + path_base
        base = cv2.imread(path_base, cv2.IMREAD_GRAYSCALE)
        base_c = cv2.GaussianBlur(base, (circle_blur, circle_blur), sigmaX=0, sigmaY=0) # circles
        output = base_c.copy()

        np.set_printoptions(threshold=np.inf)

        # detect circles in the image
        circles = cv2.HoughCircles(base_c, cv2.HOUGH_GRADIENT, dp=1, minDist=80, param1=hough_1, param2=hough_2,
                                   minRadius=7, maxRadius=50)

        self.circles = []
        if circles is not None:
            circles = np.round(circles[0, :]).astype("int")
            for (x, y, r) in circles:
                cv2.circle(output, (x, y), r, 255, 4)
                self.circles.append((x, y, r))

        self.output = output
