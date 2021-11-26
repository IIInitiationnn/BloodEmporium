import json
import math
import os
import time
from pathlib import Path, PurePosixPath
from pprint import pprint

import cv2
import networkx as nx
import numpy as np
import pyautogui
from pynput.mouse import Button, Controller
from pynput import keyboard

from config import Config
from matcher import Matcher, HoughTransform
from mergedbase import MergedBase
from node import Node
from optimiser import Optimiser
from resolution import Resolution
from simulation import Simulation
from utils.network_util import NetworkUtil

# TODO immediate priorities
#   - improve line accuracy, then do testing, then match for vanilla icons, then optimise, then config
#   - calibrate brightness of neutral using shaders
#   - calibrate brightness of background of default pack
#   - improve colour detection (occasional misidentified neutral and red nodes causes attempt to select invalid node)

''' timeline
    - [DONE] backend with algorithm
    - [DONE] openCV icon recognition
    - desire values from config file
        - can have multiple profiles of desire values and can switch
    - frontend with GUI
        - debug mode using pyvis showing matched unlockables, paths and selected nodes
    - for higher matching accuracy, enable manual category selection in frontend
        to only select nurse unlockables, or survivor unlockables for instance
    - icon with entity hand (like EGC) grasping a glowing shard
    
    - if p1, p2 or p3, stop processing
        - options for each prestige to continue unlocking in the bloodweb
    
    process:
    1. setup
        - using packs for which items? those which aren't need to be stored in assets
        - calibration with resolution
    
    on program launch:
    2. initialisation
    -> merger for template matching
    
    3. screen capture
    -> reads "click to continue" ? click anywhere
    -> identify lines and circles
        - circle: id, centre, color
        - line: circles it joins
        - origin
            - if prestige, pause
    -> matching circles to unlockable
        - networkx graph of nodes
    -> optimiser
        - optimal unlockable
    -> mouse
        - hold on position
    
'''

terminate = False
def on_press(key):
    if key == keyboard.Key.end:
        global terminate
        terminate = True

if __name__ == '__main__':
    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    # read config settings
    config = Config().config

    production_mode = False
    if production_mode:
        # resolution
        resolution = Resolution(config["resolution"]["width"],
                                config["resolution"]["height"],
                                config["resolution"]["ui_scale"])

        ratio = 1
        if not math.isclose(resolution.aspect_ratio(), 16 / 9, abs_tol=0.01):
            pass # TODO stretched res support in the future...?
        elif resolution.width > 2560:
            ratio = resolution.width / 2560 * resolution.ui_scale / 100
            resolution = Resolution(2560, 1440, 100)

        # initialisation: merged base for template matching
        print("initialisation, merging")
        merged_base = MergedBase(resolution, "nurse") # TODO
        mouse = Controller()
        mouse.position = (0, 0)

        i = 0
        while not terminate:
            # screen capture
            print("capturing screen")
            x = config["capture"]["top_left_x"]
            y = config["capture"]["top_left_y"]
            width = config["capture"]["width"]
            height = config["capture"]["height"]
            path_to_image = f"output/pic{i}.png"
            image = pyautogui.screenshot(path_to_image, region=(x, y, width, height))

            # TODO move this to a util class
            image_bgr = cv2.imread(path_to_image, cv2.IMREAD_UNCHANGED)
            image_gray = cv2.imread(path_to_image, cv2.IMREAD_GRAYSCALE)

            if ratio != 1:
                height, width = image_gray.shape
                new_height, new_width = round(height / ratio), round(width / ratio)
                image_bgr = cv2.resize(image_bgr, (new_width, new_height))
                image_gray = cv2.resize(image_gray, (new_width, new_height))

            images = {"bgr": image_bgr, "gray": image_gray}

            # click and continue if text TODO

            # hough transform: detect circles and lines
            print("hough transform")
            nodes_connections = HoughTransform(images, resolution)

            # match circles to unlockables: create networkx graph of nodes
            print("match to unlockables")
            matcher = Matcher(image_gray, nodes_connections, merged_base)
            base_bloodweb = matcher.graph # all 9999
            NetworkUtil.write_to_html(base_bloodweb, "output/matcher")

            # correct reachable nodes
            for node_id, data in base_bloodweb.nodes.items():
                if any([base_bloodweb.nodes[neighbour]["is_user_claimed"] for neighbour in base_bloodweb.neighbors(node_id)]) \
                        and not data["is_accessible"]:
                    nx.set_node_attributes(base_bloodweb, Node.from_dict(data, is_accessible=True).get_dict())

            # run through optimiser
            print("optimiser")
            optimiser = Optimiser(base_bloodweb)
            optimiser.run()
            optimal_unlockable = optimiser.select_best()
            pprint(optimal_unlockable.get_tuple())
            NetworkUtil.write_to_html(optimiser.dijkstra_graph, f"output/dijkstra{i}")

            # select perk
            # hold on the perk for 0.5s
            mouse.position = (x + round(optimal_unlockable.x * ratio), y + round(optimal_unlockable.y * ratio))
            mouse.press(Button.left)
            time.sleep(0.1)
            mouse.position = (0, 0)
            time.sleep(0.4)
            mouse.release(Button.left)

            # TODO temp click, should record and check clicking time intervals with boxes / new levels
            time.sleep(1)
            mouse.click(Button.left)
            time.sleep(1)

            i += 1

        time.sleep(30)
    else:
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
                if not math.isclose(res.aspect_ratio(), 16 / 9, abs_tol=0.01):
                    pass # TODO stretched res support in the future...?
                elif res.width > 2560:
                    ratio = res.width / 1920 * res.ui_scale / 100
                    res = Resolution(1920, 1080, 100)

                path_to_image = os.path.join(subdir, file)
                image_bgr = cv2.imread(path_to_image, cv2.IMREAD_UNCHANGED)
                image_gray = cv2.imread(path_to_image, cv2.IMREAD_GRAYSCALE)

                if ratio != 1:
                    height, width = image_gray.shape
                    new_height, new_width = round(height / ratio), round(width / ratio)
                    image_bgr = cv2.resize(image_bgr, (new_width, new_height))
                    image_gray = cv2.resize(image_gray, (new_width, new_height))

                images = {"bgr": image_bgr, "gray": image_gray}

                # sim = Simulation(os.path.join(subdir, file), res, False)
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

    cv2.destroyAllWindows()