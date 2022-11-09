import logging
import sys
import time
from datetime import datetime
from multiprocessing import Process, Pipe

import networkx as nx
import pyautogui

from backend.data import Data
from capturer import Capturer
from config import Config
from debugger import Debugger
from grapher import Grapher
from matcher import Matcher
from mergedbase import MergedBase
from optimiser import Optimiser
from resolution import Resolution

'''
0.3.0:
- [DONE] filter options collapse / expand
- [DONE, pending feedback] update cheapskate, with and without perks
- [DONE] run certain number of prestige levels
- [DONE] bloodpoint spend limit (always show regardless of whether user has limit selected, show a instead of a / b)
- [DONE] print nodes and edges in logs
- hotkeys
- add any missing properties (hotkeys) to config from default_config instead of raising error
- instant claim for early levels
'''

'''
immediate priorities
- tweak hough line parameters
    - if lines are invalidated from not being in the majority of images, print which nodes it connects
        - can determine whether it's hough or some other kind of invalidation
    - AI for hough parameters using target data
- try sum of several images to cancel out background noise instead of taking "majority" lines

features to add
- "you have unsaved changes" next to save button - profiles, settings
- ability to auto-update software
    - maybe ability to update default config presets as well? may not be desired by people who have overridden
- import / export profile as string to share with others
- find rarity of items with varying rarity (colour for mystery boxes, template match number of ticks for perks)
    - configure rarity of different tiers of mystery boxes and perks (1, 2, 3, teachable)
        - configure 5 mystery box tiers for preferences, but not 3 tiers for perks
        - type of unlockable in db: item, perk etc

timeline
- above new features and TODOs
- josh feedback
- optimisation and accuracy guarantees
- finalise -> 1.0.0
'''

# https://stackoverflow.com/questions/19425736/how-to-redirect-stdout-and-stderr-to-logger-in-python
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

class StateProcess(Process):
    def __init__(self, pipe: Pipe, args):
        Process.__init__(self)
        self.pipe = pipe
        self.args = args

    # send data to main process via pipe
    def emit(self, signal_name, payload=()):
        self.pipe.send((signal_name, payload))

    def run(self):
        timestamp = datetime.now()
        try:
            debug, write_to_output, profile_id, character, prestige_limit, bp_limit = self.args
            log = logging.getLogger()
            log.setLevel(logging.DEBUG)
            log.handlers = []

            stream_handler = logging.StreamHandler()
            stream_handler.setLevel(logging.DEBUG)
            stream_handler.setFormatter(logging.Formatter("%(message)s"))
            log.addHandler(stream_handler)

            file_handler = logging.FileHandler(f"logs/debug-{timestamp.strftime('%y-%m-%d %H-%M-%S')}.log")
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(logging.Formatter("%(message)s"))
            log.addHandler(file_handler)

            sys.stdout = LoggerWriter(log.debug)
            sys.stderr = LoggerWriter(log.warning)

            pyautogui.FAILSAFE = False

            prestige_total = 0
            bp_total = 0
            self.emit("prestige", (prestige_total, prestige_limit))
            self.emit("bloodpoint", (bp_total, bp_limit))

            base_res = resolution = Config().resolution()
            x, y = base_res.top_left()

            ratio = 1
            if base_res.height != 1080 or base_res.ui_scale != 100:
                ratio = base_res.height / 1080 * base_res.ui_scale / 100
                resolution = Resolution(1080 * base_res.width / base_res.height, 1080, 100)

            # initialisation: merged base for template matching
            print("initialisation, merging")
            unlockables = Data.get_unlockables()
            merged_base = MergedBase(resolution, character)
            pyautogui.moveTo(0, 0)

            i = 0
            while True:
                if prestige_limit is not None and prestige_total == prestige_limit:
                    print("reached prestige limit. terminating")
                    self.emit("terminate")
                    self.emit("toggle_text", ("Prestige limit reached.", False, False))
                    return

                # screen capture
                print("capturing screen")
                cv_images = Capturer(base_res, ratio, 3).output
                debugger = Debugger(cv_images, timestamp, i, write_to_output).set_merger(merged_base)

                matcher = Matcher(debugger, cv_images, resolution)
                origin, origin_type = matcher.match_origin()

                print(f"matched origin: {origin_type}")

                # vectors: detect circles and match to unlockables
                print("vector: circles and match to unlockables")
                circles = matcher.vector_circles(origin, merged_base)

                # prestige level: proceed to next level
                if origin_type == "origin_prestige.png" or origin_type == "origin_prestige_small.png":
                    if debug:
                        debugger.show_images()
                    prestige_total += 1
                    bp_total += 20000
                    if bp_limit is not None and bp_total > bp_limit:
                        print("prestige level: reached bloodpoint limit. terminating")
                        self.emit("terminate")
                        self.emit("toggle_text", ("Bloodpoint limit reached.", False, False))
                        return

                    print("prestige level: selecting")
                    self.emit("prestige", (prestige_total, prestige_limit))
                    self.emit("bloodpoint", (bp_total, bp_limit))
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
                print("NODES")
                for node in base_bloodweb.nodes:
                    print(f"    {node}")
                print("EDGES")
                max_len = max([str_len for edge in base_bloodweb.edges for str_len in [len(edge[0]), len(edge[1])]])
                for edge in base_bloodweb.edges:
                    print(f"    {str(edge[0]).ljust(max_len, ' ')} {edge[1]}")

                if debug:
                    debugger.show_images()

                j = 1
                run = True
                while run:
                    # run through optimiser
                    print("optimiser")
                    optimiser = Optimiser(base_bloodweb)
                    optimiser.run(profile_id)
                    optimal_unlockable = optimiser.select_best()
                    selected_unlockable = [u for u in unlockables if u.unique_id == optimal_unlockable.name][0]
                    bp_total += Data.get_cost(selected_unlockable.rarity)
                    if bp_limit is not None and bp_total > bp_limit:
                        print(f"{optimal_unlockable.node_id}: reached bloodpoint limit. terminating")
                        self.emit("terminate")
                        self.emit("toggle_text", ("Bloodpoint limit reached.", False, False))
                        return

                    print(optimal_unlockable.node_id)
                    debugger.set_dijkstra(optimiser.dijkstra_graph, j)
                    self.emit("bloodpoint", (bp_total, bp_limit))
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
                    if "mysteryBox" in optimal_unlockable.name:
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
                    optimiser_test.run(profile_id)
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
        except:
            self.emit("terminate")
            self.emit("toggle_text", (f"An error occurred. Please check "
                                      f"debug-{timestamp.strftime('%y-%m-%d %H-%M-%S')}.log for additional details.",
                                      True, False))

class State:
    version = "v0.3.0"

    def __init__(self, pipe):
        self.process = None
        self.pipe = pipe

    def is_active(self):
        return self.process is not None

    def run(self, args):
        if not self.is_active():
            self.process = StateProcess(self.pipe, args)
            self.process.start()
            print("process started without debugging")

    def terminate(self):
        if self.is_active():
            self.process.terminate()
            self.process = None
            print("process terminated")