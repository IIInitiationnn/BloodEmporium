import logging
import sys
import time
import traceback
from datetime import datetime
from multiprocessing import Process, Pipe

import networkx as nx
import pyautogui

from backend.data import Data
from backend.node import Node
from functions import screen_capture, match_origin, vector_circles, match_lines
from config import Config
from debugger import Debugger
from grapher import Grapher
from mergedbase import MergedBase
from optimiser import Optimiser
from resolution import Resolution

"""
bugs to fix
- squarescreen support

immediate priorities
- reload images in preferences page when path changes
- add background to assets for frontend if using vanilla (so people can see rarity) with the full coloured background
- tweak hough line parameters
    - if lines are invalidated from not being in the majority of images, print which nodes it connects
        - can determine whether it's hough or some other kind of invalidation
    - AI for hough parameters using target data
- try sum of several images to cancel out background noise instead of taking "majority" lines

features to add
- blind mode
- delete oldest logs once there are more than 100 (allowing retention for greater detail)
- "you have unsaved changes" next to save button - profiles, settings
- import / export profile as string to share with others
- find rarity of items with varying rarity (colour for mystery boxes)
    - configure rarity of different tiers of mystery boxes
        - configure 5 mystery box tiers for preferences

timeline
- above new features and TODOs
- josh feedback
- optimisation and accuracy guarantees
- finalise -> 1.0.0
"""

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

            # TODO >= 100 logs, kill until 99
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
            cap_dim = base_res.cap_dim()

            ratio = 1
            if base_res.height != 1080 or base_res.ui_scale != 100:
                ratio = base_res.height / 1080 * base_res.ui_scale / 100
                resolution = Resolution(1080 * base_res.width / base_res.height, 1080, 100)

            # initialisation: merged base for template matching
            print(f"initialisation at {base_res.width} x {base_res.height} @ {base_res.ui_scale}; merging")
            print(f"region: ({x}, {y}) to ({x + cap_dim}, {y + cap_dim})")
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
                cv_images = screen_capture(base_res, ratio)
                debugger = Debugger(cv_images, timestamp, i, write_to_output)
                debugger.set_merger(merged_base)

                print("matching origin")
                origin, origin_type, cropped = match_origin(cv_images[0], resolution)
                debugger.set_origin(origin)
                debugger.set_origin_type(origin_type)
                debugger.set_cropped(cropped)
                print(f"matched origin: {origin_type} ({x + origin.x() * ratio}, {y + origin.y() * ratio})")

                # vectors: detect circles and match to unlockables
                print("vector: circles and match to unlockables")
                circles = vector_circles(cv_images[0], resolution, origin, merged_base, debugger)
                debugger.set_valid_circles(circles)

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
                    time.sleep(1.5)
                    pyautogui.mouseUp()
                    time.sleep(4) # 4 sec to clear out until new level screen
                    pyautogui.click()
                    time.sleep(0.5) # prestige 1-3 => teachables, 4-6 => cosmetics, 7-9 => charms
                    pyautogui.click()
                    time.sleep(0.5) # 1 sec to generate
                    pyautogui.moveTo(0, 0)
                    time.sleep(0.5) # 1 sec to generate
                    continue

                # hough transform: detect lines
                print("hough transform: lines")
                edge_images, raw_lines, connections = match_lines(cv_images, resolution, circles)
                debugger.set_edge_images(edge_images)
                debugger.set_raw_lines(raw_lines)
                debugger.set_connections(connections)

                # create networkx graph of nodes
                print("creating networkx graph")
                grapher = Grapher(circles, connections) # all 9999
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

                # fast-forward levels with <= 6 nodes (excl. origin) and none yet claimed
                fast = len(base_bloodweb.nodes) <= 7 and all([not data["is_user_claimed"]
                                                              for node_id, data in base_bloodweb.nodes.items()
                                                              if node_id != "ORIGIN"])
                j = 1
                run = True
                while run:
                    # correct reachable nodes
                    # print("pre-correction")
                    # for node_id, data in base_bloodweb.nodes.items():
                    #     if any([base_bloodweb.nodes[neighbour]["is_user_claimed"] for neighbour in
                    #             base_bloodweb.neighbors(node_id)]) and not data["is_accessible"]:
                    #         print(f"    corrected {node_id}")
                    #         nx.set_node_attributes(base_bloodweb, Node.from_dict(data, is_accessible=True).get_dict())

                    # run through optimiser
                    print("optimiser")
                    optimiser = Optimiser(base_bloodweb)
                    optimiser.run(profile_id)
                    print("    updated nodes")
                    for node_id, data in optimiser.dijkstra_graph.nodes.items():
                        print(f"        {node_id.ljust(max_len, ' ')} "
                              f"value {str(data['value']).ljust(10, ' ')} "
                              f"accessible {str(data['is_accessible']).ljust(5, ' ')} "
                              f"claimed {data['is_user_claimed']}")

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
                    if fast:
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

                    if fast:
                        # correct reachable nodes
                        print("post-correction")
                        for node_id, data in base_bloodweb.nodes.items():
                            if any([base_bloodweb.nodes[neighbour]["is_user_claimed"] for neighbour in
                                    base_bloodweb.neighbors(node_id)]) and not data["is_accessible"]:
                                print(f"    corrected {node_id}")
                                nx.set_node_attributes(base_bloodweb, Node.from_dict(data, is_accessible=True).get_dict())
                    else:
                        # time for bloodweb to update
                        time.sleep(0.3)

                        # take new picture and update colours
                        print("updating bloodweb")
                        updated_image = screen_capture(base_res, ratio, 1)[0]
                        Grapher.update(base_bloodweb, updated_image, resolution)
                        debugger.add_updated_image(updated_image.get_bgr(), j)

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
            traceback.print_exc()
            self.emit("terminate")
            self.emit("toggle_text", (f"An error occurred. Please check "
                                      f"debug-{timestamp.strftime('%y-%m-%d %H-%M-%S')}.log for additional details.",
                                      True, False))

class State:
    version = "v1.0.0"

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