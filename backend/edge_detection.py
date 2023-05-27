import os
import sys
from typing import List

import numpy as np
import torch

from backend.shapes import LinkedEdge, MatchedNode
from backend.util.timer import Timer

sys.path.append(os.path.dirname(os.path.realpath("yolov5_obb/models")))

from yolov5_obb.models.common import DetectMultiBackend
from yolov5_obb.utils.augmentations import letterbox
from yolov5_obb.utils.general import check_img_size, scale_polys, non_max_suppression_obb
from yolov5_obb.utils.rboxs_utils import rbox2poly

class EdgeDetection:
    def __init__(self):
        # load model on init
        self.model = DetectMultiBackend("assets/models/edges v2.pt")
        self.model.float()

        # get custom names from custom model
        self.CLASS_NAMES_DICT = self.model.names

    def predict(self, img_original):
        stride = self.model.stride
        image_size = check_img_size(1024, s=stride)

        img_rescaled = letterbox(img_original, image_size, stride=stride, auto=True)[0]

        img_rescaled = img_rescaled.transpose((2, 0, 1))[::-1] # HWC to CHW, BGR to RGB
        img_rescaled = np.ascontiguousarray(img_rescaled)

        img_rescaled = torch.from_numpy(img_rescaled)
        img_rescaled = img_rescaled.float()
        if len(img_rescaled.shape) == 3:
            img_rescaled = img_rescaled[None] # expand for batch dim
        img_rescaled /= 255  # 0 - 255 to 0.0 - 1.0

        results = self.model(img_rescaled)
        # confidence threshold is 2nd parameter in this
        results = non_max_suppression_obb(results, 0.6, 0.45, None, False, multi_label=True, max_det=100)
        results = results[0] # only one image

        pred_poly = rbox2poly(results[:, :5]) # (n, [x1 y1 x2 y2 x3 y3 x4 y4])

        processed_results = []
        if len(results) > 0:
            # scale rescaled to original
            pred_poly = scale_polys(img_rescaled.shape[2:], pred_poly, img_original.shape)
            processed_results = torch.cat((pred_poly, results[:, -2:]), dim=1) # (n, [poly conf cls])

        return processed_results

    # TODO maybe also return unlinked edges
    def link_edges(self, results, matched_nodes: List[MatchedNode], avg_diameter) -> List[LinkedEdge]:
        timer = Timer("link_edges")
        edges = []
        for x1, y1, x2, y2, x3, y3, x4, y4, confidence, cls in results: # cls not useful
            closests = []
            for (x, y) in [(x1, y1), (x2, y2), (x3, y3), (x4, y4)]:
                closest = min(matched_nodes, key=lambda node: node.box.centre().distance_xy(x, y))
                if closest not in closests and closest.box.centre().distance_xy(x, y) < avg_diameter:
                    closests.append(closest)
                if len(closests) > 2:
                    continue
            if len(closests) == 2:
                new_edge = LinkedEdge(*closests)
                if not any([new_edge == edge for edge in edges]):
                    edges.append(new_edge)
        timer.update()
        return edges
