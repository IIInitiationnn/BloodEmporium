import math
import sys
from pathlib import Path

import cv2
import os

from images import Images
from resolution import Resolution
from simulation import Simulation

if __name__ == '__main__':
    target = {
        "base_boon.png": 26,
        "base_david_stuart.png": 10,
        "base_dwight_stuart.png": 20,
        "base_feng_stuart.png": 27,
        "base_jill.png": 20,
        "base_leon.png": 20,
        "base_oni.png": 16,
        "base_pinhead.png": 5,
        "base_spirit_stuart.png": 8,
        "base_sussy.png": 7,
        "base_trickster.png": 18,
        "base_wraith_stuart.png": 5,
        "base_yun.png": 20,
        "base_blight.png": 27,
        "base_claud.png": 27,
        "base_jane.png": 27,
        "base_nea.png": 12,
        "base_nurse.png": 27,
        "base_nurse_2.png": 27,
        "base_nurse_default.png": 27,
        "base_pig.png": 27,
        "base_spirit.png": 27,
        "base_trapper_mixed.png": 27,
        "base_billy_4k.png": 27,
        "base_huntress_4k.png": 27,
        "base_myers_4k.png": 27,
        "base_nurse_4k.png": 21,
        "base_nurse_4k_2.png": 17,
        "base_nurse_4k_3.png": 16,
        "base_nurse_4k_4.png": 27,
        "base_nurse_4k_5.png": 26,
        "base_nurse_4k_6.png": 21,
        "base_nurse_4k_7.png": 19,
        "base_nurse_4k_8.png": 16,
        "base_nurse_4k_70_1.png": 18,
        "base_nurse_4k_70_2.png": 17,
        "base_nurse_4k_70_3.png": 27,
        "base_nurse_4k_70_4.png": 14,
        "base_nurse_4k_70_5.png": 27,
        "base_nurse_4k_70_6.png": 27,
        "base_nurse_4k_70_7.png": 26,
        "base_nurse_4k_70_8.png": 22,
        "base_nurse_4k_70_9.png": 21,
        "base_nurse_4k_70_10.png": 18,
        "base_pig_4k.png": 27,
        "base_spirit_4k.png": 27,
        "base_wraith_4k.png": 27,
    }
    num_errors = 0

    for subdir, dirs, files in os.walk("training_data/bases/shaderless"):
        for file in files:
            p = Path(os.path.join(subdir, file)).as_posix()
            s = p.split("/")[3]
            res = Resolution(int(s.split("x")[0]), int(s.split("x")[1].split("_")[0]), int(s.split("_")[-1]))

            ratio = 1

            path_to_image = os.path.join(subdir, file)
            image_bgr = cv2.imread(path_to_image, cv2.IMREAD_COLOR)
            image_gray = cv2.imread(path_to_image, cv2.IMREAD_GRAYSCALE)

            if ratio != 1:
                height, width = image_gray.shape
                new_height, new_width = round(height / ratio), round(width / ratio)
                image_bgr = cv2.resize(image_bgr, (new_width, new_height), interpolation=Images.interpolation)
                image_gray = cv2.resize(image_gray, (new_width, new_height), interpolation=Images.interpolation)

            images = {"bgr": image_bgr, "gray": image_gray}

            sim = Simulation(images, res, False)
            sim.run()
            this_errors = abs(sim.num_circles - target[file])
            res.print()
            if this_errors != 0:
                print(file, this_errors)
                # height, width = sim.image.shape
                # cv2.imshow("out", cv2.resize(sim.image, (width * 2 // 3, height * 2 // 3)))
                # cv2.imshow("hhhhh", cv2.resize(sim.hhhhh, (width * 2 // 3, height * 2 // 3)))
                # cv2.waitKey(0)
            num_errors += this_errors
    print(num_errors)
    """sim = Simulation("output/pic0.png", False)
    sim.run()"""