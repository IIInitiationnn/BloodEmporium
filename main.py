import os
import time
from pprint import pprint

import cv2
import networkx as nx
import numpy as np
import pyautogui
from pynput.mouse import Button, Controller

import json
from matcher import Matcher, HoughTransform
from mergedbase import MergedBase
from node import Node
from optimiser import Optimiser
from resolution import Resolution
from simulation import Simulation
from utils.network_util import NetworkUtil

# TODO immediate priorities
#   -!!!!!!! more debugging tools! for each iteration, write to a folder containing all colors, masks etc.
#   - simulation class: model what happens without needing to spend bloodpoints (just modify the graph)
#       - useful for tweaking optimiser if needed
#   - try thresholding+contour detection; contour fitting for higher accuracy
#   - if inconsistent, consider hardcoding relative positions of nodes
#   - calibrate brightness of neutral using shaders
#   - calibrate brightness of background of default pack
#   - working with different UI scales -> adjust constants
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

if __name__ == '__main__':
    # read config settings
    with open("config.json") as f:
        config = json.load(f)

    production_mode = False
    if production_mode:
        # resolution
        resolution = Resolution(config["resolution"]["width"],
                                config["resolution"]["height"],
                                config["resolution"]["ui_scale"])

        # initialisation: merged base for template matching
        print("initialisation, merging")
        merged_base = MergedBase(resolution)
        mouse = Controller()
        mouse.position = (0, 0)

        i = 0
        while i < 10:
            # screen capture
            print("capturing screen")
            x = config["capture"]["top_left_x"]
            y = config["capture"]["top_left_y"]
            width = config["capture"]["width"]
            height = config["capture"]["height"]
            path_to_image = f"output/pic{i}.png"
            image = pyautogui.screenshot(path_to_image, region=(x, y, width, height))
            image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

            # hough transform: detect circles and lines
            print("hough transform")
            nodes_connections = HoughTransform(path_to_image, resolution)

            # match circles to unlockables: create networkx graph of nodes
            print("match to unlockables")
            matcher = Matcher(cv2.imread(path_to_image, cv2.IMREAD_GRAYSCALE), nodes_connections, merged_base)
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
            mouse.position = (x + optimal_unlockable.x, y + optimal_unlockable.y)
            mouse.press(Button.left)
            time.sleep(0.1)
            mouse.position = (0, 0)
            time.sleep(0.4)
            mouse.release(Button.left)

            # TODO temp click
            time.sleep(1)
            mouse.click(Button.left)
            time.sleep(1)

            i += 1

        time.sleep(30)
    else:
        alpha = 0.6
        while alpha <= 1.4:
            beta = -50
            while beta <= 50:



                num_errors = 0
                i = 0
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
                    "base_pig_4k.png": 27,
                    "base_spirit_4k.png": 27,
                    "base_wraith_4k.png": 27,
                }
                for subdir, dirs, files in os.walk("training_data/bases/shaderless"):
                    for file in files:
                        if "target" not in file and "old" not in file:
                            r = subdir.split("\\")[1]
                            res = Resolution(int(r.split("x")[0]), int(r.split("x")[1].split("_")[0]), int(r.split("_")[1]))
                            # res.print()

                            sim = Simulation(os.path.join(subdir, file), res, False, alpha, beta)
                            sim.run()
                            this_errors = abs(sim.num_circles - target[file])
                            # if this_errors != 0:
                                # print(file, this_errors)
                                # cv2.imshow("out", sim.image)
                                # cv2.waitKey(0)
                            num_errors += this_errors
                            i += 1
                print(alpha, beta, num_errors)



                beta += 25
            alpha += 0.05


        """sim = Simulation("output/pic0.png", False)
        sim.run()"""

    cv2.destroyAllWindows()