import cv2
import numpy as np

from utils.distance_util import close_proximity

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
        # path_example = Matcher.offerings_path + "/iconFavors_jarOfSaltyLips.png" # TODO transparency, harder; 70x70
        # path_example = Recogniser.items_path + "/iconItems_firstAidKit.png" # 50x50
        # path_example = Recogniser.offerings_path + "/iconFavors_bogLaurelSachet.png"
        # path_example = Recogniser.offerings_path + "/Yemen/iconFavors_annotatedBlueprint.png"
        # path_example = Recogniser.offerings_path + "/iconFavors_spottedOwlWreath.png"
        # path_example = Recogniser.offerings_path + "/iconFavors_scratchedCoin.png"
        # path_example = Matcher.addons_path + "/iconAddon_metalSpoon.png"
        # path_example = Matcher.addons_path + "/iconAddon_butterflyTape.png"
        # path_example = Matcher.offerings_path + "/Anniversary/iconsFavors_5thAnniversary.png"
        # path_example = Matcher.perks_path + "/Qatar/iconPerks_camaraderie.png"
        # path_example = Matcher.perks_path + "/Qatar/iconPerks_babySitter.png"
        path_example = Matcher.items_path + "/iconItems_toolbox.png"
        # path_base = "base.png"
        # path_base = "base_larger.png"
        path_base = "base_claud.png"

        dim = 50

        np.set_printoptions(threshold=np.inf)
        template = cv2.imread(path_example, cv2.IMREAD_GRAYSCALE)
        template = cv2.resize(template, (dim, dim), interpolation=cv2.INTER_AREA) # configure in config, should be some default according to resolutions; diff for square vs hexagon vs diamond
        template_alpha = cv2.resize(cv2.split(cv2.imread(path_example, cv2.IMREAD_UNCHANGED))[3], (dim, dim), interpolation=cv2.INTER_AREA) # for masking

        base = cv2.imread(path_base, cv2.IMREAD_GRAYSCALE)

        height, width = template.shape

        # apply template matching
        base_copy = base.copy()
        method = "cv2.TM_CCORR_NORMED"
        result = cv2.matchTemplate(base_copy, template, eval(method), mask=template_alpha)

        single_match = True

        if single_match:
            # single match
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

            top_left = max_loc
            bottom_right = (top_left[0] + width, top_left[1] + height)
            cv2.rectangle(base_copy, top_left, bottom_right, 255, 2) # 255 = white; 2 = thickness
        else:
            # multiple matches
            threshold = 0.95 # larger value = better match / fit
            loc = np.where(result >= threshold)

            matches = []
            for top_left in zip(*loc[::-1]):
                bottom_right = (top_left[0] + width, top_left[1] + height)
                if not any([close_proximity(tl, top_left) and close_proximity(br, bottom_right) for (tl, br) in matches]):
                    matches.append((top_left, bottom_right))
                    cv2.rectangle(base_copy, top_left, bottom_right, 255, 2) # 255 = white; 2 = thickness

        cv2.imshow(method, base_copy)
        cv2.waitKey(0)

        cv2.imshow('Image', template)
        cv2.imshow('Base', base)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


    """ old solution using preprocessing (blurring) and canny edge detection, scrapped in favour of masking
    def __init__(self):
        path_example = Recogniser.offerings_path + "/iconFavors_jarOfSaltyLips.png" # TODO transparency, harder; 70x70
        #path_example = Recogniser.items_path + "/iconItems_firstAidKit.png" # 50x50
        #path_example = Recogniser.offerings_path + "/iconFavors_bogLaurelSachet.png"
        #path_example = Recogniser.offerings_path + "/Yemen/iconFavors_annotatedBlueprint.png"

        np.set_printoptions(threshold=np.inf)
        template = cv2.imread(path_example, cv2.IMREAD_GRAYSCALE)
        cv2.imshow('Template', template)
        cv2.waitKey(0)

        template = cv2.resize(template, (70, 70), interpolation=cv2.INTER_AREA) # configure in config, should be some default according to resolutions; diff for square vs hexagon vs diamond
        cv2.imshow('Resized', template)
        cv2.waitKey(0)

        template = cv2.GaussianBlur(template, (3, 3), sigmaX=0, sigmaY=0)
        cv2.imshow('Blur', template)
        cv2.waitKey(0)

        template = cv2.Canny(image=template, threshold1=75, threshold2=100)
        cv2.imshow('Edges', template)
        cv2.waitKey(0)

        base = cv2.imread("base.png", cv2.IMREAD_GRAYSCALE)
        base = cv2.GaussianBlur(base, (3, 3), sigmaX=0, sigmaY=0)
        base = cv2.Canny(image=base, threshold1=50, threshold2=75)

        height, width = template.shape
        # methods = ["cv2.TM_CCOEFF", "cv2.TM_CCOEFF_NORMED", "cv2.TM_CCORR", "cv2.TM_CCORR_NORMED", "cv2.TM_SQDIFF", "cv2.TM_SQDIFF_NORMED"]

        base_copy = base.copy()

        # apply template matching
        method = "cv2.TM_CCORR_NORMED"
        result = cv2.matchTemplate(base_copy, template, eval(method))
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        ''' # if the method is TM_SQDIFF or TM_SQDIFF_NORMED, take minimum
        if method in ["cv2.TM_SQDIFF", "cv2.TM_SQDIFF_NORMED"]:
            top_left = min_loc
        else:
            top_left = max_loc'''
        top_left = max_loc
        bottom_right = (top_left[0] + width, top_left[1] + height)

        cv2.rectangle(base_copy, top_left, bottom_right, 255, 5)
        base_copy = cv2.resize(base_copy, (1920, 1080))
        cv2.imshow(method, base_copy)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        cv2.imshow('Image', template)
        cv2.imshow('Base', base)
        cv2.waitKey(0)
        cv2.destroyAllWindows()"""