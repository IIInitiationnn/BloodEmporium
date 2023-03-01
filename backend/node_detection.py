import random
from pprint import pprint

import cv2
import numpy as np
import torch
from supervision.draw.color import ColorPalette
from supervision.tools.detections import Detections, BoxAnnotator
from ultralytics import YOLO

from backend.image import Image


class NodeDetection:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Node Detector is going to use device: {self.device}")

        # loads model on init
        self.model = YOLO("assets/models/nodes.pt")
        self.model.fuse()

        # gets custom names from custom model
        self.CLASS_NAMES_DICT = self.model.names

        # self.box_annotator = BoxAnnotator(color=ColorPalette(), thickness=3, text_thickness=1, text_scale=1)

    def predict(self, frame):
        # runs model on frame
        return self.model.predict(frame)

    def any_left_after(self, results):
        num = 0
        for result in results[0]:
            if self.CLASS_NAMES_DICT[result.boxes.cls.cpu().numpy()[0]] in ["accessible", "inaccessible"]:
                num += 1
        return num > 1

    def filter_by_class(self, results, classes):
        filtered = []
        for result in results[0]:
            if self.CLASS_NAMES_DICT[result.boxes.cls.cpu().numpy()[0]] in classes:
                filtered.append((result.boxes.xyxy.cpu().numpy()[0],
                                 result.boxes.conf.cpu().numpy()[0],
                                 result.boxes.cls.cpu().numpy()[0]))
        return filtered

    def get_accessible_or_prestige(self, results, screenshot, merged_base):
        filtered = self.filter_by_class(results, ["accessible", "prestige"])
        if len(filtered) > 0:
            xyxy, confidence, cls = random.choice(filtered)
            x1, y1, x2, y2 = xyxy
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            print(confidence, self.CLASS_NAMES_DICT[cls])
            if self.CLASS_NAMES_DICT[cls] == "accessible":
                unlockable = screenshot[y1:y2, x1:x2]
                height, width = y2 - y1, x2 - x1

                names = merged_base.names
                images = merged_base.images

                # apply template matching
                base = images.copy()
                result = cv2.matchTemplate(base, unlockable, cv2.TM_CCOEFF_NORMED)

                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

                top_left = max_loc
                bottom_right = (top_left[0] + width, top_left[1] + height)
                match_unique_id = names[round((bottom_right[1] - merged_base.full_dim / 2) / merged_base.full_dim)]

                # match = base[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]
                # cv2.imshow("unlockable from screen", cv2.resize(unlockable, (width * 2, height * 2),
                #                                                 interpolation=Image.interpolation))
                # cv2.imshow(f"matched unlockable", cv2.resize(match, (width * 2, height * 2),
                #                                              interpolation=Image.interpolation))
                # cv2.waitKey(0)
                # cv2.destroyAllWindows()
                return (x1, y1, x2, y2), match_unique_id
            else:
                return ((x1, y1, x2, y2), "prestige") if confidence > 0.7 else None
        else:
            return None

    def plot_bboxes(self, results, frame, debug=False):
        xyxys = []
        confidences = []
        class_ids = []

        # loop through all detections in an image
        for result in results[0]:
            # if result.boxes.conf.cpu().numpy()[0] > 0.3:
                xyxys.append(result.boxes.xyxy.cpu().numpy()[0])
                confidences.append(result.boxes.conf.cpu().numpy()[0])
                class_ids.append(result.boxes.cls.cpu().numpy()[0])

        if len(xyxys) == 0:
            xyxys = results[0].boxes.xyxy.cpu().numpy()
            confidences = results[0].boxes.conf.cpu().numpy()
            class_ids = results[0].boxes.cls.cpu().numpy()

        # ALL CODE BELLOW IS USED ONLY FOR DEBUG AND DEV PURPOSES
        if debug:
            # create detections class, used for visualization, can be skipped in final
            # detections = Detections(xyxy=results[0].boxes.xyxy.cpu().numpy(),
            #                         confidence=results[0].boxes.conf.cpu().numpy(),
            #                         class_id=results[0].boxes.cls.cpu().numpy().astype(int))
            detections = Detections(xyxy=np.array(xyxys), confidence=np.array(confidences),
                                    class_id=np.array(class_ids).astype(int))

            # label setup - also for debug
            self.labels = [f"{self.CLASS_NAMES_DICT[class_id]} {confidence:0.2f}"
                           for _, confidence, class_id, tracker_id in detections]

            # apply visualize
            frame = self.box_annotator.annotate(frame=frame, detections=detections, labels=self.labels)

            return frame
        else:

            return frame
