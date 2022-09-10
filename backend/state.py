import logging
import sys
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
    - new timings??
    - bug where tier and subtier have same colour for positive / negative when one is negative and one is positive?
    - sort by type by default, get rid of "default usually does the job"
    - find rarity of items with varying rarity (colour for mystery boxes, template match number of ticks for perks)
        - configure rarity of different tiers of mystery boxes and perks (1, 2, 3, teachable)
            - configure 5 mystery box tiers for preferences, but not 3 tiers for perks
            - type of unlockable in db: item, perk etc
    - tweak hough line parameters
        - if lines are invalidated from not being in the majority of images, print which nodes it connects
            - can determine whether it's hough or some other kind of invalidation
        - AI for hough parameters using target data

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
    - toggle option for gui: show default (coloured) icons
        - default on, applicable when user has no custom icons; when off use custom icons
        - will naturally revert to default (colourless) icons from assets when no custom icons
    - when clicking run, show prompt for turning shaders off
    - status in run page showing reason for stopping if it does; can also show bp progress if there is a bp cap
    - output log somewhere - maybe in the debug mode
    - ability to auto-update software
        - maybe ability to update default config presets as well? may not be desired by people who have overridden
    - import / export profile as string to share with others

timeline
    - above TODOs incl new features
    - josh feedback
    - optimisation and accuracy guarantees
    - remove output folder and finalise -> 1.0.0

update checklist
    - update state version
new content checklist
    - add assets for new killer + survivor perks, killer addons
    - add into database
        - new killer in killer table
        - new addons in unlockables table
        - new offerings in unlockables table
        - new perks in unlockables table
'''

# from https://stackoverflow.com/questions/19425736/how-to-redirect-stdout-and-stderr-to-logger-in-python
class LoggerWriter(object):
    def __init__(self, writer):
        self._writer = writer
        self._msg = ""

    def write(self, message):
        self._msg = self._msg + message
        while "\n" in self._msg:
            pos = self._msg.find("\n")
            self._writer(self._msg[:pos])
            self._msg = self._msg[pos + 1:]

    def flush(self):
        if self._msg != "":
            self._writer(self._msg)
            self._msg = ""

class State:
    version = "v0.2.7"

    def __init__(self, use_hotkeys=True, hotkey_callback=None):
        self.thread = None
        if use_hotkeys:
            listener = keyboard.Listener(on_press=self.on_press)
            listener.start()
        self.hotkey_callback = hotkey_callback

    def is_active(self):
        return self.thread is not None

    def run_debug_mode(self):
        if not self.is_active():
            self.thread = Process(target=State.main_loop, args=(True, False))
            self.thread.start()
            if self.hotkey_callback is not None:
                self.hotkey_callback()
            print("thread started with debugging")

    def run_regular_mode(self):
        if not self.is_active():
            self.thread = Process(target=State.main_loop, args=(False, False))
            self.thread.start()
            if self.hotkey_callback is not None:
                self.hotkey_callback()
            print("thread started without debugging")

    def terminate(self):
        if self.is_active():
            self.thread.terminate()
            self.thread = None
            if self.hotkey_callback is not None:
                self.hotkey_callback()
            print("thread terminated")

    def on_press(self, key):
        pass
        '''k = str(format(key))
        if k == "'8'":
            self.run_debug_mode()
        elif k == "'9'":
            self.run_regular_mode()
        elif k == "'0'":
            self.terminate()'''

    @staticmethod
    def main_loop(debug, write_to_output):
        log = logging.getLogger()
        log.setLevel(logging.DEBUG)
        log.handlers = []

        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.DEBUG)
        stream_handler.setFormatter(logging.Formatter("%(message)s"))
        log.addHandler(stream_handler)

        file_handler = logging.FileHandler(f"logs/debug-{datetime.now().strftime('%y-%m-%d %H-%M-%S')}.log")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter("%(message)s"))
        log.addHandler(file_handler)

        sys.stdout = LoggerWriter(log.debug)
        sys.stderr = LoggerWriter(log.warning)

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
            origin, origin_type = matcher.match_origin()

            # vectors: detect circles and match to unlockables
            print("vector: circles and match to unlockables")
            circles = matcher.vector_circles(origin, merged_base)

            # prestige level: proceed to next level
            if origin_type == "origin_prestige.png":
                print("prestige level: selecting")
                if debug:
                    debugger.show_images()

                pyautogui.moveTo(x + round(origin.x() * ratio), y + round(origin.y() * ratio))
                pyautogui.mouseDown()
                time.sleep(0.5)
                pyautogui.moveTo(0, 0)
                time.sleep(1)
                pyautogui.mouseUp()
                time.sleep(4) # 4 sec to clear out until new level screen
                pyautogui.click()
                time.sleep(0.5) # prestige 1-3 => teachables
                pyautogui.click()
                time.sleep(1) # 1 sec to generate
                continue

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

                # select perk: hold on the perk for 0.3s
                pyautogui.moveTo(x + round(optimal_unlockable.x * ratio), y + round(optimal_unlockable.y * ratio))
                pyautogui.mouseDown()
                time.sleep(0.15)
                pyautogui.moveTo(0, 0)
                time.sleep(0.15)
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
                    time.sleep(0.5) # 2 sec to clear out until new level screen
                    pyautogui.click()
                    time.sleep(0.5) # in case of extra information on early level (eg. lvl 2 or lvl 5)
                    pyautogui.click()
                    time.sleep(0.5) # in case of yet more extra information on early level (eg. lvl 10)
                    pyautogui.click()
                    time.sleep(2) # 2 secs to generate
                j += 1
            i += 1

if __name__ == '__main__':
    State()