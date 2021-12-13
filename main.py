import time
from datetime import datetime
from multiprocessing import Process, freeze_support, Event

import networkx as nx
import pyautogui
from pynput import keyboard

from capturer import Capturer
from config import Config
from debugger import Debugger
from grapher import Grapher
from matcher import Matcher
from mergedbase import MergedBase
from optimiser import Optimiser
from resolution import Resolution

# TODO immediate priorities
#   - stdout -> log
#   - exe working
#   - create a default config file if deleted, then when adding gui also make a function to create one from user input
#   - search perks / addons on GUI, sort by categories like character, rarity (may need unlockable class)

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
    pyautogui.FAILSAFE = False

    # read config settings
    config = Config()

    base_res = resolution = config.resolution()
    x, y = base_res.top_left()

    ratio = 1
    if base_res.width != 1920 or base_res.ui_scale != 100:
        ratio = base_res.width / 1920 * base_res.ui_scale / 100
        resolution = Resolution(1920, 1080, 100)

    # initialisation: merged base for template matching
    print("initialisation, merging")
    merged_base = MergedBase(resolution, config.character())
    pyautogui.moveTo(0, 0)

    i = 0
    timestamp = datetime.now()
    while True:
        # screen capture
        print("capturing screen")
        cv_images = Capturer(base_res, ratio, 3).output
        debugger = Debugger(cv_images, True, timestamp, i).set_merger(merged_base)

        matcher = Matcher(debugger, cv_images, resolution)
        origin = matcher.match_origin()

        # vectors: detect circles and match to unlockables
        print("vector: circles and match to unlockables")
        circles = matcher.vector_circles(origin, merged_base)

        # hough transform: detect lines
        print("hough transform: lines")
        connections = matcher.match_lines(circles)

        # create networkx graph of nodes
        print("creating networkx graph")
        grapher = Grapher(debugger, circles, connections) # all 9999
        base_bloodweb = grapher.create()
        debugger.set_base_bloodweb(base_bloodweb)

        if debug:
            debugger.show_images()

        j = 1
        run = True
        while run:
            # run through optimiser
            print("optimiser")
            optimiser = Optimiser(base_bloodweb)
            optimiser.run()
            optimal_unlockable = optimiser.select_best()
            print(optimal_unlockable.node_id)
            debugger.set_dijkstra(optimiser.dijkstra_graph, j)

            optimal_unlockable.set_user_claimed(True)
            optimal_unlockable.set_value(9999)
            nx.set_node_attributes(base_bloodweb, optimal_unlockable.get_dict())

            # select perk
            # hold on the perk for 0.5s
            pyautogui.moveTo(x + round(optimal_unlockable.x * ratio), y + round(optimal_unlockable.y * ratio))
            pyautogui.mouseDown()
            time.sleep(0.25)
            pyautogui.moveTo(0, 0)
            time.sleep(0.25)
            pyautogui.mouseUp()

            # mystery box: click
            if optimal_unlockable.name == "iconHelp_mysteryBox":
                print("mystery box selected")
                time.sleep(0.9)
                pyautogui.click()
                time.sleep(0.2)

            time.sleep(0.3) # time for bloodweb to update

            # take new picture and update colours
            print("updating bloodweb")
            updated_images = Capturer(ratio, 1).output[0]
            Grapher.update(base_bloodweb, updated_images, resolution)
            debugger.add_updated_image(updated_images.get_bgr(), j)

            # new level
            optimiser_test = Optimiser(base_bloodweb)
            optimiser_test.run()
            optimal_test = optimiser_test.select_best()
            num_left = sum([1 for data in base_bloodweb.nodes.values() if not data["is_user_claimed"]])
            if optimal_test.node_id == "ORIGIN" or num_left == 0:
                # TODO verify that .node_id == "ORIGIN" will still happen if >1 item gets chomped by entity on last click
                print("level cleared")
                run = False
                time.sleep(2) # 2 sec to clear out until new level screen
                pyautogui.click()
                time.sleep(2) # 2 secs to generate
            j += 1
        i += 1

thread = None

def on_press(key):
    global thread
    if str(format(key)) == "'8'":
        # debug mode
        if thread is None:
            thread = Process(target=main_loop, args=(True,))
            thread.start()
            print("thread started with debugging")
    elif str(format(key)) == "'9'":
        # no debug mode
        if thread is None:
            thread = Process(target=main_loop, args=(False,))
            thread.start()
            print("thread started without debugging")
    elif str(format(key)) == "'0'":
        if thread is not None:
            thread.terminate()
            thread = None
            print("thread terminated")

if __name__ == '__main__':
    freeze_support() # --onedir

    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    # wait until termination
    dummy_event = Event()
    dummy_event.wait()