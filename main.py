import os
import time
from pprint import pprint

import networkx as nx
from pynput.mouse import Button, Controller

import cv2
import numpy as np
import pyautogui

from matcher import Matcher, HoughTransform
from mergedbase import MergedBase
from node import Node
from optimiser import Optimiser

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
from simulation import Simulation
from utils.network_util import NetworkUtil

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
    production_mode = False
    if production_mode:
        # initialisation: merged base for template matching
        print("initialisation, merging")
        merged_base = MergedBase()
        mouse = Controller()
        mouse.position = (0, 0)

        i = 0
        while i < 10:
            # screen capture
            x, y, width, height = 250, 380, 800, 800
            print("capturing screen")
            path_to_image = f"output/pic{i}.png"
            image = pyautogui.screenshot(path_to_image, region=(x, y, width, height))
            image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

            # hough transform: detect circles and lines
            print("hough transform")
            nodes_connections = HoughTransform(path_to_image, 5, 7, 10, 45, 5, 85, 40, 30, 25)

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
        num_errors = 0
        i = 0
        target = [27, 26, 27, 10, 20, 27, 27, 20, 11, 20, 12, 27, 27, 27, 16, 27, 5, 27, 8, 7, 27, 18, 5, 20]
        for subdir, dirs, files in os.walk("training_data/bases/shaderless"):
            for file in files:
                if "target" not in file and "old" not in file:
                # if "target" not in file and ("nurse" in file or "nea" in file):
                    sim = Simulation(os.path.join(subdir, file), False)
                    sim.run()
                    this_errors = abs(sim.num_circles - target[i])
                    if this_errors != 0:
                        print(file, this_errors)
                        cv2.imshow("out", sim.image)
                        cv2.waitKey(0)
                    num_errors += this_errors
                    i += 1
        print(num_errors)