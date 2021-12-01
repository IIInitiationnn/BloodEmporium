import json
import math
import os
import time
from multiprocessing import Process
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
#   - improve line accuracy, then do testing, then match for vanilla icons, then optimise, then config, then gui
#   - calibrate brightness of neutral using shaders
#   - calibrate brightness of background of default pack
#   - improve colour detection (occasional misidentified neutral and red nodes causes attempt to select invalid node)
#   - 2 layers of priority:
#       - tier for multiples e.g. tier 2 equivalent to 2 tier 1, tier -2 equally unlikeable as 2 tier -1
#       - subtier to order in these tiers, non negative
#   - slow mode: more accurate, slower (take pic each time)
#   - fast mode: takes one picture, clears out entire bloodweb, may not prioritise as well

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
def main_loop():
    # read config settings
    config = Config().config

    # resolution
    resolution = Resolution(config["resolution"]["width"], config["resolution"]["height"], config["resolution"]["ui_scale"])

    ratio = 1
    if not math.isclose(resolution.aspect_ratio(), 16 / 9, abs_tol=0.01):
        pass # TODO stretched res support in the future...?
    elif resolution.width > 2560:
        ratio = resolution.width / 2560 * resolution.ui_scale / 100
        resolution = Resolution(2560, 1440, 100)

    # initialisation: merged base for template matching
    print("initialisation, merging")
    merged_base = MergedBase(resolution, "survivor") # TODO
    mouse = Controller()
    mouse.position = (0, 0)

    i = 0
    while True:
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
        time.sleep(0.2)
        mouse.position = (0, 0)
        time.sleep(0.3)
        mouse.release(Button.left)

        # mystery box: click
        if optimal_unlockable.name == "iconHelp_mysteryBox.png":
            print("mystery box selected")
            time.sleep(0.9)
            mouse.click(Button.left)

        # new level
        if optimiser.num_left() <= 2:
            print("level cleared")
            time.sleep(1.5) # 1 sec to clear out until new level screen # TODO test when have more bps
            mouse.click(Button.left)

        time.sleep(2) # 2 secs to generate
        i += 1

thread = None

def on_press(key):
    global thread
    if key == keyboard.Key.end:
        thread.terminate()
        print("thread terminated")
    elif key == keyboard.Key.delete:
        thread = Process(target=main_loop)
        thread.start()
        print("thread started")

if __name__ == '__main__':
    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    time.sleep(300)

    cv2.destroyAllWindows()