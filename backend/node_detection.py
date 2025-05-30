import math
import os
from math import floor
from statistics import mode
from typing import List, Optional, Tuple

import cv2
import numpy as np
import pytesseract
from ultralytics import YOLO
from ultralytics.yolo.engine.results import Results

from backend.image import Image
from backend.mergedbase import MergedBase
from backend.shapes import UnmatchedNode, MatchedNode, Box
from backend.util.image_util import ImageUtil
from backend.util.node_util import NodeType
from backend.util.timer import Timer


# https://stackoverflow.com/questions/59829470/pyinstaller-and-tesseract-ocr
# https://stackoverflow.com/questions/66470878/tesseract-ocr-doesnt-work-when-python-script-is-converted-to-exe-without-consol
pytesseract.pytesseract.tesseract_cmd = os.getcwd() + r"\tesseract\tesseract.exe"

class NodeDetection:
    NUM_CALIBRATIONS = 25

    def __init__(self):
        # loads model on init
        self.model = YOLO("assets/models/nodes v5.pt")
        self.model.fuse()

        # gets custom names from custom model
        self.CLASS_NAMES_DICT = self.model.names

        # self.reader = easyocr.Reader([])
        self.ratios: List[float] = []

    def predict(self, img_original) -> Results:
        return self.model.predict(img_original)[0]

    def preprocess_unlockable(self, xyxy, screenshot, size):
        x1, y1, x2, y2 = xyxy
        x1, y1, x2, y2 = round(x1), round(y1), round(x2), round(y2)
        height, width = y2 - y1, x2 - x1 # original dim

        # cut out border
        margin_fraction = 4.2 # (1 / margin_fraction) around each side cut out
        margin_y, margin_x = round(height / margin_fraction), round(width / margin_fraction)
        height, width = height - 2 * margin_y, width - 2 * margin_x # dim after removing margins
        unlockable = screenshot[(y1 + margin_y):(y2 - margin_y), (x1 + margin_x):(x2 - margin_x)]

        # (assuming size = 64) resize to (64, x) or (x, 64) where x <= 64
        # if height > width:
        #     ratio = size / height
        #     rescaled = (size, round(ratio * width))
        # else:
        #     ratio = size / width
        #     rescaled = (round(ratio * height), size)
        # return cv2.resize(unlockable, rescaled, interpolation=Image.interpolation)

        return unlockable

    def match_unlockable_sift(self, xyxy, screenshot, merged_base: MergedBase) -> Optional[MatchedNode]:
        size = merged_base.size
        unlockable = self.preprocess_unlockable(xyxy, screenshot, size)

        # find keypoints and descriptors
        sift_extractor = cv2.SIFT_create()
        kp1, des1 = sift_extractor.detectAndCompute(unlockable, None)
        kp2, des2 = merged_base.keypoints, merged_base.descriptors

        flann_index_kdtree = 0
        index_params = dict(algorithm=flann_index_kdtree, trees=5)
        search_params = dict(checks=50)

        # find matches by knn
        flann = cv2.FlannBasedMatcher(index_params, search_params)
        matches: List[cv2.DescriptorMatcher] = flann.knnMatch(des1, des2, k=2)

        # lowe's ratio test
        threshold = 0.75 # the lower, the harsher
        good_matches: List[cv2.DMatch] = [m for m, n in matches if m.distance < threshold * n.distance]

        # [match.trainIdx] indexes keypoints, [1] grabs y-value
        ys = sorted([kp2[match.trainIdx].pt[1] for match in good_matches])
        match_names = [merged_base.names[floor(y / size)] for y in ys]
        match_unique_id = mode(match_names) if len(match_names) > 0 else ""

        # from collections import Counter
        # cv2.imshow("unlockable from screen", unlockable)
        # print(Counter(match_names))
        # if match_unique_id != "":
        #     index = mode([floor(yi / merged_base.size) for yi in y])
        #     matched_unlockable = merged_base.images[(index * size):(index * size + size)]
        #     cv2.imshow("matched unlockable", matched_unlockable)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
        return match_unique_id

    def match_unlockable_template(self, xyxy, screenshot, merged_base: MergedBase) -> Tuple[str, float]:
        size = merged_base.size
        unlockable = self.preprocess_unlockable(xyxy, screenshot, size)

        overall_max_val = -math.inf
        overall_max_loc = None
        best_ratio = None
        best_size = None
        tried_shapes = []

        # apply template matching
        if len(self.ratios) < NodeDetection.NUM_CALIBRATIONS:
            # needs calibration to find best ratio until we have a good sample size
            for ratio in [0.8, 1, 0.9, 0.95, 0.85, 0.875, 0.975, 0.925, 0.825]: # TODO accuracy isnt perfect
                # assuming operating these ratios on (64, x) or (x, 64), ie 0.8 would make it (51, x) or (x, 51)
                # the ratio we are interested in (final_ratio) is the one that gets us from the original size to the best size
                # if it is 128x128 to 64x64, then it will be 96x96 to 48x48

                # (assuming size = 64) resize to (64, x) or (x, 64) where x <= 64
                h, w = unlockable.shape
                if h > w:
                    final_ratio = size / h * ratio
                    rescaled = (round(size * ratio), round(final_ratio * w))
                else:
                    final_ratio = size / w * ratio
                    rescaled = (round(final_ratio * h), round(size * ratio))
                if rescaled in tried_shapes:
                    continue

                rescaled_unlockable = cv2.resize(unlockable, rescaled)

                result = cv2.matchTemplate(merged_base.images, rescaled_unlockable, cv2.TM_CCOEFF_NORMED)
                _, max_val, _, max_loc = cv2.minMaxLoc(result)
                tried_shapes.append((h, w))
                if max_val > overall_max_val:
                    overall_max_val = max_val
                    overall_max_loc = max_loc
                    best_ratio = final_ratio
                    best_size = rescaled

            # print(f"{best_ratio} {best_size} {overall_max_val}")
            self.ratios.append(best_ratio)
        else:
            # use calibrated ratio for rest of runtime until termination
            best_ratio = np.median(self.ratios)
            h, w = unlockable.shape
            rescaled = (round(h * best_ratio), round(w * best_ratio))
            rescaled_unlockable = cv2.resize(unlockable, rescaled)
            result = cv2.matchTemplate(merged_base.images, rescaled_unlockable, cv2.TM_CCOEFF_NORMED)
            _, overall_max_val, _, overall_max_loc = cv2.minMaxLoc(result)

        index = floor(overall_max_loc[1] / size)
        match_unique_id = merged_base.names[index]

        # matched_unlockable = merged_base.images[(index * size):(index * size + size)]
        # cv2.imshow("unlockable from screen", unlockable)
        # cv2.imshow("matched unlockable", matched_unlockable)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
        return match_unique_id, overall_max_val

    # deprecated
    '''
    def match_claimable(self, all_nodes: List[UnmatchedNode], screenshot, merged_base: MergedBase) -> List[MatchedNode]:
        timer = Timer()
        filtered = [node for node in all_nodes if node.cls_name in NodeType.MULTI_CLAIMABLE]

        # none: return empty
        if len(filtered) == 0:
            timer.update("match_claimable")
            return []

        # prestige: return only prestige
        prestige = [node for node in filtered if node.cls_name == NodeType.PRESTIGE]
        if len(prestige) == 1:
            timer.update("match_claimable")
            return [MatchedNode.from_unmatched_node(prestige[0])]

        claimable = []
        for node in filtered: # origin_auto or in/accessible
            if node.cls_name == NodeType.PRESTIGE:
                continue
            if node.cls_name in NodeType.MULTI_ORIGIN_AUTO:
                claimable.append(MatchedNode.from_unmatched_node(node))
            else:
                match_unique_id = self.match_unlockable_template(node.xyxy(), screenshot, merged_base)
                claimable.append(MatchedNode.from_unmatched_node(node, match_unique_id))
        timer.update("match_claimable")
        return claimable
    '''

    # filter only those with sufficiently high confidence until more robust model
    # TODO ensure there is origin of highest conf if output is > 1 and is not prestige
    def get_validate_all_nodes(self, results) -> Tuple[List[UnmatchedNode], UnmatchedNode]:
        timer = Timer("get_nodes")
        nodes = []
        prestige = False
        bp_node = None
        for result in results:
            (x1, y1, x2, y2), confidence, cls = result.boxes.xyxy.numpy()[0], \
                                                result.boxes.conf.numpy()[0], \
                                                result.boxes.cls.numpy()[0]
            cls_name = self.CLASS_NAMES_DICT[cls]
            box = Box(round(x1), round(y1), round(x2), round(y2))
            if cls_name == NodeType.BLOODPOINTS:
                if confidence > 0.3: # TODO hhh set this back to 0.5 or 0.6 after more training on screenshots with low bp
                    if bp_node is None or confidence > bp_node.confidence:
                        bp_node = UnmatchedNode(box, confidence, cls_name)
                        continue

            if prestige: # prestige node has already been found, can ignore everything else except bloodpoint node
                continue

            if cls_name == NodeType.PRESTIGE:
                if confidence > 0.7:
                    nodes = [UnmatchedNode(box, confidence, cls_name)]
                    prestige = True
            else: # all origins, in/accessible, claimed, stolen, void
                if confidence > 0.5: # sometimes junk with ~0.3 confidence slips through
                    for node in nodes:
                        if box.close_to(node.box): # new node close to any existing nodes
                            if confidence > node.confidence: # if this node is more likely to be correct than existing
                                nodes.remove(node)
                                nodes.append(UnmatchedNode(box, confidence, cls_name))
                            break # close to existing node: exit out of loop and do not enter else
                    else: # new node not close to any existing nodes
                        nodes.append(UnmatchedNode(box, confidence, cls_name))

        timer.update()
        return nodes, bp_node

    def __match_nodes(self, all_nodes: List[UnmatchedNode], screenshot, merged_base) -> Tuple[List[MatchedNode], float]:
        matched = []
        accuracies = []
        for unmatched_node in all_nodes:
            if unmatched_node.cls_name in NodeType.MULTI_UNCLAIMED:
                match_unique_id, accuracy = self.match_unlockable_template(unmatched_node.xyxy(), screenshot, merged_base)
                accuracies.append(accuracy)
                matched.append(MatchedNode.from_unmatched_node(unmatched_node, match_unique_id))
            else:
                matched.append(MatchedNode.from_unmatched_node(unmatched_node))
        return matched, (np.median(accuracies) if len(accuracies) > 0 else None)

    def match_nodes(self, all_nodes: List[UnmatchedNode], screenshot, merged_base) -> List[MatchedNode]:
        timer = Timer("match_nodes")

        is_initialisation_run = len(self.ratios) < NodeDetection.NUM_CALIBRATIONS
        matched, accuracy = self.__match_nodes(all_nodes, screenshot, merged_base)
        print(f"accuracy: {accuracy}")
        # need to recalibrate: highly unlikely will ever be necessary but just in case
        if not is_initialisation_run and accuracy is not None and accuracy < 0.7:
            self.ratios.clear()
            matched, accuracy = self.__match_nodes(all_nodes, screenshot, merged_base)
            print(f"recalibration accuracy: {accuracy}")

        timer.update()
        return matched

    def calculate_bloodpoints(self, bp_node: UnmatchedNode, screenshot):
        timer = Timer("calculate_bloodpoints")
        x1, y1, x2, y2 = bp_node.xyxy()
        x1, y1, x2, y2 = round(x1), round(y1), round(x2), round(y2)
        bp_image = screenshot[y1:y2, x1:x2]

        bp_image = ImageUtil.resize(bp_image, new_height=30)
        bp_image = cv2.GaussianBlur(bp_image, (3, 3), 0)
        bp_image = 255 - bp_image # pytesseract better to invert, easyocr better to have white text black bg
        _, bp_image = cv2.threshold(bp_image, 50, 255, cv2.THRESH_BINARY)

        try:
            # bp_num = int(self.reader.readtext(bp_image, allowlist="0123456789")[0][1])
            bp_num = int(pytesseract.image_to_string(bp_image, config="-c tessedit_char_whitelist=0123456789"))
        except ValueError:
            bp_num = None # TODO figure out a systematic way of accurately determining bp as failsafe eg blur, resize
        print(bp_num)

        # cv2.imshow("bp", bp_image)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

        timer.update()
        return bp_num