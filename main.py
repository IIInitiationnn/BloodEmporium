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

from capturer import Capturer
from config import Config
from debugger import Debugger
from matcher import Matcher, HoughTransform
from mergedbase import MergedBase
from node import Node
from optimiser import Optimiser
from resolution import Resolution
from simulation import Simulation
from utils.network_util import NetworkUtil

# TODO immediate priorities
#   - change from pynput to pyautogui for mouse clicks?? keep pynput for listener?? the lag kills but idk if computer issue
#   - detect when a circle is black - get that alpha stuff going for image!
#   - improve line accuracy, then do testing, then match for vanilla icons, then optimise, then config, then gui
#   - calibrate brightness of background of default pack
#   - improve colour detection (occasional misidentified neutral and red nodes causes attempt to select invalid node)
#   - 2 layers of priority:
#       - tier for multiples e.g. tier 2 equivalent to 2 tier 1, tier -2 equally unlikeable as 2 tier -1
#       - subtier to order in these tiers, non negative
#   - slow mode = fast mode!
#       - use knowledge of which node was last selected, check all other unclaimed nodes if they are now black,
#       update graph using that info. dont need to match, only need to wait 2 secs and check circle colour at position
#       dont need to run hough circle or line!

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
def main_loop(debug):
    # read config settings
    config = Config()

    # resolution
    resolution = config.resolution()

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
        cv_images = Capturer(ratio, 3).output
        debugger = Debugger(cv_images, True).set_merger(merged_base) # hhhhh

        matcher = Matcher(debugger, cv_images, resolution)
        origin = matcher.match_origin()

        # hough transform: detect circles
        circles = matcher.match_circles()
        circles.append(origin)

        # TODO hough transform: detect lines
        lines = matcher.match_lines(circles)

        debugger.show_images() # hhhhh
        return

        # hough transform: detect circles and lines
        print("hough transform")
        nodes_connections = HoughTransform(images, resolution)
        debugger.set_hough(nodes_connections) # hhhhh

        # match circles to unlockables: create networkx graph of nodes
        print("match to unlockables")
        matcher = MatcherOld(image_gray, nodes_connections, merged_base)
        base_bloodweb = matcher.graph # all 9999
        debugger.set_matcher(matcher) # hhhhh

        # correct reachable nodes
        for node_id, data in base_bloodweb.nodes.items():
            if any([base_bloodweb.nodes[neighbour]["is_user_claimed"] for neighbour in base_bloodweb.neighbors(node_id)]) \
                    and not data["is_accessible"]:
                nx.set_node_attributes(base_bloodweb, Node.from_dict(data, is_accessible=True).get_dict())

        if debug:
            debugger.show_images() # hhhhh

        j = 1
        run = True
        while run:
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
            debugger.set_optimiser(optimiser, j) # hhhhh

            # select the node
            optimal_unlockable.set_user_claimed(True)
            optimal_unlockable.set_value(9999)
            nx.set_node_attributes(base_bloodweb, optimal_unlockable.get_dict())
            j += 1

            # select perk
            # hold on the perk for 0.5s
            mouse.position = (x + round(optimal_unlockable.x * ratio), y + round(optimal_unlockable.y * ratio))
            mouse.press(Button.left)
            time.sleep(0.1)
            mouse.position = (0, 0)
            time.sleep(0.4)
            mouse.release(Button.left)

            # mystery box: click
            if optimal_unlockable.name == "iconHelp_mysteryBox.png":
                print("mystery box selected")
                time.sleep(0.9)
                mouse.click(Button.left)

            # new level
            # if optimiser.num_left() <= 2: # TODO change to if no more nodes left
            #     print("level cleared")
            #     time.sleep(2) # 2 sec to clear out until new level screen
            #     mouse.click(Button.left)

            time.sleep(0.5) # "fast" mode - no captures in between generates
            # time.sleep(2) # 2 secs to generate

            if all([data["is_user_claimed"] for data in base_bloodweb.nodes.values()]):
                run = False

        print("level cleared")
        time.sleep(2) # 2 secs to clear out until new level screen
        mouse.click(Button.left)
        time.sleep(2) # 2 secs to generate

        i += 1

thread = None

def on_press(key):
    global thread
    if str(format(key)) == "'8'":
        # dont write to output
        thread = Process(target=main_loop, args=(True,))
        thread.start()
        print("thread started with debugging")
    elif str(format(key)) == "'9'":
        # write to output
        thread = Process(target=main_loop, args=(False,))
        thread.start()
        print("thread started without debugging")
    elif str(format(key)) == "'0'":
        thread.terminate()
        print("thread terminated")

if __name__ == '__main__':
    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    time.sleep(300)

    cv2.destroyAllWindows()