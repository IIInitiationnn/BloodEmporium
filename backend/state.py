import time
from datetime import datetime
from multiprocessing import Process

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

# TODO try catch for threads and terminate if error

'''
immediate priorities
    - find rarity of items with varying rarity (colour for mystery boxes, template match number of ticks for perks)
        - configure rarity of different tiers of mystery boxes and perks (1, 2, 3, teachable)
            - configure 5 mystery box tiers for preferences, but not 3 tiers for perks
            - type of unlockable in db: item, perk etc
    - tweak hough line parameters
        - if lines are invalidated from not being in the majority of images, print which nodes it connects
            - can determine whether it's hough or some other kind of invalidation

features to add
    - frontend with GUI
        - debug mode using pyvis showing matched unlockables, paths and selected nodes
        - create config from user input
        - sort / filter unlockables by rarity, cost, search by name etc
    - icon with entity hand (like EGC) grasping a glowing shard
    - if p1, p2 or p3, stop processing (config option to ignore prestige)
        - options for each prestige to continue unlocking in the bloodweb
    - spend certain amount of bloodpoints (add cost to unlockable class)
    - prioritise perk option (will always path to perks first and ignore perk config)
'''

class State:
    version = "v0.1.1"

    def __init__(self, use_hotkeys=True):
        self.thread = None
        if use_hotkeys:
            listener = keyboard.Listener(on_press=self.on_press)
            listener.start()

    def is_active(self):
        return self.thread is not None

    def run_debug_mode(self):
        if not self.is_active():
            self.thread = Process(target=State.main_loop, args=(True, True))
            self.thread.start()
            print("thread started with debugging")

    def run_regular_mode(self):
        if not self.is_active():
            self.thread = Process(target=State.main_loop, args=(False, True))
            self.thread.start()
            print("thread started without debugging")

    def terminate(self):
        if self.is_active():
            self.thread.terminate()
            self.thread = None
            print("thread terminated")

    def on_press(self, key):
        k = str(format(key))
        if k == "'8'":
            self.run_debug_mode()
        elif k == "'9'":
            self.run_regular_mode()
        elif k == "'0'":
            self.terminate()

    @staticmethod
    def main_loop(debug, write_to_output):
        pyautogui.FAILSAFE = False

        base_res = resolution = Config().resolution()
        x, y = base_res.top_left()

        ratio = 1
        if base_res.width != 1920 or base_res.ui_scale != 100:
            ratio = base_res.width / 1920 * base_res.ui_scale / 100
            resolution = Resolution(1920, 1080, 100)

        # initialisation: merged base for template matching
        print("initialisation, merging")
        merged_base = MergedBase(resolution, Config().character())
        pyautogui.moveTo(0, 0)

        i = 0
        timestamp = datetime.now()
        while True:
            # screen capture
            print("capturing screen")
            cv_images = Capturer(base_res, ratio, 3).output
            debugger = Debugger(cv_images, timestamp, i, write_to_output).set_merger(merged_base)

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

                # select perk: hold on the perk for 0.5s
                pyautogui.moveTo(x + round(optimal_unlockable.x * ratio), y + round(optimal_unlockable.y * ratio))
                pyautogui.mouseDown()
                time.sleep(0.25)
                pyautogui.moveTo(0, 0)
                time.sleep(0.25)
                pyautogui.mouseUp()

                # mystery box: click
                if optimal_unlockable.name == "iconHelp_mysteryBox_universal":
                    print("mystery box selected")
                    time.sleep(0.9)
                    pyautogui.click()
                    time.sleep(0.2)

                # move mouse again in case it didn't the first time
                pyautogui.moveTo(0, 0)

                # time for bloodweb to update
                time.sleep(0.3)

                # take new picture and update colours
                print("updating bloodweb")
                updated_images = Capturer(base_res, ratio, 1).output[0]
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
                    time.sleep(0.5) # in case of extra information on early level (eg. lvl 2 or lvl 5)
                    pyautogui.click()
                    time.sleep(2) # 2 secs to generate
                j += 1
            i += 1

if __name__ == '__main__':
    State()