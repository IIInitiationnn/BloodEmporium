import math
import random
from math import floor
from statistics import mode
from typing import List, Optional

import cv2
from ultralytics import YOLO
from ultralytics.yolo.engine.results import Results

from backend.image import Image
from backend.mergedbase import MergedBase
from backend.shapes import UnmatchedNode, MatchedNode, Box
from backend.util.node_util import NodeType
from backend.util.timer import Timer


class NodeDetection:
    def __init__(self):
        # loads model on init
        self.model = YOLO("assets/models/nodes v3.pt")
        self.model.fuse()

        # gets custom names from custom model
        self.CLASS_NAMES_DICT = self.model.names

    def predict(self, img_original) -> Results:
        return self.model.predict(img_original)[0]

    def any_left_after(self, results):
        num = 0
        for result in results:
            if self.CLASS_NAMES_DICT[result.boxes.cls.numpy()[0]] in NodeType.MULTI_UNCLAIMED:
                num += 1
        return num > 1

    def filter_by_class(self, results, classes):
        filtered = []
        for result in results:
            if self.CLASS_NAMES_DICT[result.boxes.cls.numpy()[0]] in classes:
                filtered.append((result.boxes.xyxy.numpy()[0],
                                 result.boxes.conf.numpy()[0],
                                 result.boxes.cls.numpy()[0]))
        return filtered

    def preprocess_unlockable(self, xyxy, screenshot, size):
        x1, y1, x2, y2 = xyxy
        x1, y1, x2, y2 = round(x1), round(y1), round(x2), round(y2)
        height, width = y2 - y1, x2 - x1 # original dim

        # cut out border
        margin_fraction = 4.5 # (1 / margin_fraction) around each side cut out
        margin_y, margin_x = round(height / margin_fraction), round(width / margin_fraction)
        height, width = height - 2 * margin_y, width - 2 * margin_x # dim after removing margins
        unlockable = screenshot[(y1 + margin_y):(y2 - margin_y), (x1 + margin_x):(x2 - margin_x)]

        # (assuming size = 64) resize to (64, x) or (x, 64) where x <= 64
        size = (size, round(size / height * width)) if height > width else \
            (round(size / width * height), size)
        return cv2.resize(unlockable, size, interpolation=Image.interpolation)

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

    def match_unlockable_template(self, xyxy, screenshot, merged_base: MergedBase):
        size = merged_base.size
        unlockable = self.preprocess_unlockable(xyxy, screenshot, merged_base.size)

        overall_max_val = -math.inf
        overall_max_loc = None
        tried_shapes = []
        # apply template matching
        for ratio in [0.8, 1, 0.9, 0.95, 0.85, 0.875, 0.975, 0.925, 0.825]: # TODO accuracy isnt perfect
            h, w = unlockable.shape
            h, w = round(ratio * h), round(ratio * w)
            if (h, w) in tried_shapes:
                continue
            result = cv2.matchTemplate(merged_base.images, cv2.resize(unlockable, (h, w)), cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            tried_shapes.append((h, w))
            if max_val > overall_max_val:
                overall_max_val = max_val
                overall_max_loc = max_loc
            if overall_max_val > 0.8:
                break

        index = floor(overall_max_loc[1] / size)
        match_unique_id = merged_base.names[index]

        # matched_unlockable = merged_base.images[(index * size):(index * size + size)]
        # cv2.imshow("unlockable from screen", unlockable)
        # cv2.imshow("matched unlockable", matched_unlockable)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
        return match_unique_id

    def match_accessible_or_prestige(self, results, screenshot, merged_base: MergedBase) -> Optional[MatchedNode]:
        timer = Timer()
        filtered = self.filter_by_class(results, [NodeType.ACCESSIBLE, NodeType.PRESTIGE])
        if len(filtered) > 0:
            (x1, y1, x2, y2), confidence, cls = random.choice(filtered)
            x1, y1, x2, y2 = round(x1), round(y1), round(x2), round(y2)
            cls_name = self.CLASS_NAMES_DICT[cls]

            if self.CLASS_NAMES_DICT[cls] == NodeType.ACCESSIBLE:
                match_unique_id = self.match_unlockable_template((x1, y1, x2, y2), screenshot, merged_base)
                timer.update("match_accessible_or_prestige")
                return MatchedNode(Box(x1, y1, x2, y2), confidence, cls_name, match_unique_id)
            else:
                timer.update("match_accessible_or_prestige")
                return MatchedNode(Box(x1, y1, x2, y2), confidence, cls_name) if confidence > 0.7 else None
        else:
            return None

    # TODO ensure there is origin of highest conf if output is > 1 and is not prestige
    def get_nodes(self, results) -> List[UnmatchedNode]:
        timer = Timer()
        nodes = []
        for result in results:
            (x1, y1, x2, y2), confidence, cls = result.boxes.xyxy.numpy()[0], result.boxes.conf.numpy()[0], \
                                                result.boxes.cls.numpy()[0]
            cls_name = self.CLASS_NAMES_DICT[cls]

            # filter only those with sufficiently high confidence until more robust model
            box = Box(round(x1), round(y1), round(x2), round(y2))
            if cls_name in [NodeType.ORIGIN, NodeType.CLAIMED, NodeType.ACCESSIBLE,
                            NodeType.INACCESSIBLE, NodeType.STOLEN, NodeType.VOID]:
                for node in nodes:
                    if box.close_to(node.box): # new node close to any existing nodes
                        if confidence > node.confidence: # if this node is more likely to be correct than existing
                            nodes.remove(node)
                            nodes.append(UnmatchedNode(box, confidence, cls_name))
                        break # close to existing node: exit out of loop and do not enter else
                else: # new node not close to any existing nodes
                    nodes.append(UnmatchedNode(box, confidence, cls_name))
            else: # prestige
                if confidence > 0.7:
                    nodes = [UnmatchedNode(box, confidence, cls_name)]
                    break
        timer.update("get_nodes")
        return nodes

    def match_nodes(self, results, screenshot, merged_base) -> List[MatchedNode]:
        timer = Timer()
        matched = []
        for unmatched_node in self.get_nodes(results):
            box = unmatched_node.box
            x1, y1, x2, y2 = box.xyxy()
            if unmatched_node.cls_name in NodeType.MULTI_UNCLAIMED:
                match_unique_id = self.match_unlockable_template((x1, y1, x2, y2), screenshot, merged_base)
                matched.append(MatchedNode(box, unmatched_node.confidence, unmatched_node.cls_name, match_unique_id))
            else:
                matched.append(MatchedNode(box, unmatched_node.confidence, unmatched_node.cls_name))
        timer.update("match_nodes")
        return matched