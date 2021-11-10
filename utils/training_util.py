import os
import random

import cv2

from matcher import CircleMatcher
from utils.distance_util import circles_are_overlapping

class CircleTrainer:
    '''to find best parameters for matching circles'''
    def __init__(self):
        targets = {}

        for base in [file for (subdir, dirs, files) in os.walk("training_data/bases") for file in files]:
            target = CircleMatcher(base, 11, 10, 45)
            # TODO use 4 or 5 full-screenshot bases, some sparse, some diff packs
            #  create an output image of black with white circles (no centre) and measure cross correlation against these
            #  target images instead of using CircleMatcher^
            # cv2.imshow(base, target.output)
            # cv2.waitKey(0)
            # cv2.destroyAllWindows()
            targets[base] = target.circles

        for i in range(10000):
            circle_blur = 11
            hough_1 = 8 + random.uniform(0, 4)
            hough_2 = 43 + random.uniform(0, 4)

            print(circle_blur, hough_1, hough_2)

            success = True
            matches = {}
            for base in [file for (subdir, dirs, files) in os.walk("training_data/bases") for file in files]:
                match = CircleMatcher(base, circle_blur, hough_1, hough_2)
                matches[base] = match.output
                circles = match.circles.copy()

                missed = []

                for target_circle in targets[base].copy():
                    success = False
                    for circle in circles:
                        if circles_are_overlapping(target_circle, circle):
                            success = True
                            circles.remove(circle)
                            break

                    if not success:
                        missed.append(target_circle)

                if not success or len(circles) > 10 or len(missed) > 10:
                    success = False
                    break

            if success:
                path = f"circle_trainer/successes/blur={circle_blur}_hough1={hough_1}_hough2={hough_2}/"
                os.mkdir(path)
                for base, match in matches.items():
                    cv2.imwrite(f"{path}/{base}", match)
            else:
                path = f"circle_trainer/failures/blur={circle_blur}_hough1={hough_1}_hough2={hough_2}/"
                os.mkdir(path)
                for base, match in matches.items():
                    cv2.imwrite(f"{path}/{base}", match)

