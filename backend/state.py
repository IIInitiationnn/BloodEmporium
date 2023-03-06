import logging
import os
import sys
import time
import traceback
from datetime import datetime
from multiprocessing import Process, Pipe
from typing import List

import pyautogui
from numpy import mean

from backend.data import Data
from backend.edge_detection import EdgeDetection
from backend.node_detection import NodeDetection
from backend.shapes import UnmatchedNode
from backend.util.node_util import NodeType
from config import Config
from debugger import Debugger
from functions import screen_capture
from grapher import Grapher
from mergedbase import MergedBase
from optimiser import Optimiser
from resolution import Resolution

"""
PATHS
Offerings | Killer + Survivor | Hexagon | C:/Program Files (x86)/Steam/steamapps/common/Dead by Daylight/DeadByDaylight/Content/UI/Icons/Favors
Addons    | Killer + Survivor | Square  | C:/Program Files (x86)/Steam/steamapps/common/Dead by Daylight/DeadByDaylight/Content/UI/Icons/ItemAddons
Items     | Survivor          | Square  | C:/Program Files (x86)/Steam/steamapps/common/Dead by Daylight/DeadByDaylight/Content/UI/Icons/Items
Perks     | Killer + Survivor | Diamond | C:/Program Files (x86)/Steam/steamapps/common/Dead by Daylight/DeadByDaylight/Content/UI/Icons/Perks

MODULE PATCHES
venv/Lib/site-packages/ultralytics/hub/utils.py Class Traces early return on __init__ and __call__
venv/Lib/site-packages/ultralytics/yolo/engine/predictor.py Class BasePredictor self.args.verbose = False

https://github.com/ultralytics/yolov5/issues/6948#issuecomment-1075528897
venv/Lib/site-packages/torch/nn/modules/upsampling.py Class BasePredictor self.args.verbose = False

TRAINING
yolov8 node detection
TODO add new hyperparam file, imgsz = 1024? random resize augmentation?
yolo task=detect mode=train data="datasets/Blood-Emporium-Node-Detection-1/data.yaml" epochs=2000 plots=True device=0

yolov5obb edge detection
python train.py --hyp hyperparameters.yaml --data ../datasets/roboflow/data.yaml --epochs 2000 --batch-size 16 --img 1024 --device 0 --patience 0 --adam

IMMEDIATE PRIORITIES
- reload images in preferences page when path changes
- add background to assets for frontend if using vanilla (so people can see rarity) with the full coloured background

FEATURES TO ADD
- settings: are you using a custom pack (+ "browse for folder")
- notes for each config
- "you have unsaved changes" next to save button - profiles, settings
- import / export profile as string to share with others
- find rarity of items with varying rarity (colour for mystery boxes)
    - configure rarity of different tiers of mystery boxes
        - configure 5 mystery box tiers for preferences
- program termination upon reaching insufficient bloodpoints (bloodpoint tracking should also use nums in top right to verify if item was selected)
- summary on items obtained by the application
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

'''
TODO possible improvements:
- better model
    - more training data
    - more prestige data
    - brightness and saturation preprocessing?
    - add some images containing transitions (new level) to train model to not classify them as prestiges
      may be able to retire the 0.7 arbitrary threshold after this
- if no progress for 5 seconds, need to use failsafe
'''

class StateProcess(Process):
    def __init__(self, pipe: Pipe, args):
        Process.__init__(self)
        self.pipe = pipe
        self.args = args

    # send data to main process via pipe
    def emit(self, signal_name, payload=()):
        self.pipe.send((signal_name, payload))

    # TODO instead of scaling ratio of node centres in this function, just send them rescaled back from the models
    def run(self):
        timestamp = datetime.now()
        try:
            debug, write_to_output, profile_id, character, is_naive_mode, prestige_limit, bp_limit = self.args
            log = logging.getLogger()
            log.setLevel(logging.DEBUG)
            log.handlers = []

            stream_handler = logging.StreamHandler()
            stream_handler.setLevel(logging.DEBUG)
            stream_handler.setFormatter(logging.Formatter("%(message)s"))
            log.addHandler(stream_handler)

            # >= 100 logs, kill until 99
            all_logs = [f"logs/{x}" for x in os.listdir("logs")]
            if len(all_logs) >= 100:
                all_logs.sort(key=os.path.getctime, reverse=True)
                for old_log in all_logs[99:]:
                    os.remove(os.path.abspath(old_log))

            file_handler = logging.FileHandler(f"logs/debug-{timestamp.strftime('%y-%m-%d %H-%M-%S')}.log")
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(logging.Formatter("%(message)s"))
            log.addHandler(file_handler)

            sys.stdout = LoggerWriter(log.debug)
            sys.stderr = LoggerWriter(log.warning)

            pyautogui.FAILSAFE = False

            node_detector = NodeDetection()

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

            debugger = Debugger(timestamp, write_to_output)
            debugger.set_merged_base(merged_base)

            bloodweb_iteration = 0
            if is_naive_mode: # TODO add debugger
                print("running in naive mode")
                while True:
                    if prestige_limit is not None and prestige_total == prestige_limit:
                        print("reached prestige limit. terminating")
                        self.emit("terminate")
                        self.emit("toggle_text", ("Prestige limit reached.", False, False))
                        return

                    # screen capture
                    print("capturing screen")
                    cv_image = screen_capture(base_res, ratio, crop=False)

                    # yolov8: detect accessible nodes
                    print("yolov8: detect accessible nodes")
                    results = node_detector.predict(cv_image.get_bgr())
                    matched_node = node_detector.match_accessible_or_prestige(results, cv_image.get_gray(), merged_base)

                    # nothing detected
                    if matched_node is None:
                        time.sleep(0.5) # try again
                        pyautogui.click()
                        continue

                    centre = matched_node.box.centre()
                    centre.scale(ratio)

                    # prestige
                    if matched_node.cls_name == NodeType.PRESTIGE:
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
                        pyautogui.moveTo(*centre.xy())
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

                    # accessible
                    selected_unlockable = [u for u in unlockables if u.unique_id == matched_node.unique_id][0]
                    bp_total += Data.get_cost(selected_unlockable.rarity)
                    if bp_limit is not None and bp_total > bp_limit:
                        print(f"{matched_node.unique_id}: reached bloodpoint limit. terminating")
                        self.emit("terminate")
                        self.emit("toggle_text", ("Bloodpoint limit reached.", False, False))
                        return

                    print(matched_node.unique_id)
                    self.emit("bloodpoint", (bp_total, bp_limit))

                    # select perk: hold on the perk for 0.3s
                    pyautogui.moveTo(*centre.xy())
                    pyautogui.mouseDown()
                    time.sleep(0.15)
                    pyautogui.moveTo(0, 0)
                    time.sleep(0.15)
                    pyautogui.mouseUp()

                    # mystery box: click
                    if "mysteryBox" in matched_node.unique_id:
                        print("mystery box selected")
                        time.sleep(0.9)
                        pyautogui.click()
                        time.sleep(0.2)

                    # move mouse again in case it didn't the first time
                    pyautogui.moveTo(0, 0)
                    bloodweb_iteration += 1
            else:
                print("running in aware mode")
                edge_detector = EdgeDetection()
                while True:
                    if prestige_limit is not None and prestige_total == prestige_limit:
                        print("reached prestige limit. terminating")
                        self.emit("terminate")
                        self.emit("toggle_text", ("Prestige limit reached.", False, False))
                        return

                    # screen capture
                    print("capturing screen")
                    cv_image = screen_capture(base_res, ratio, crop=False)
                    debugger.set_image(bloodweb_iteration, cv_image)

                    # yolov8: detect and match all nodes
                    print("yolov8: detect and match all nodes")
                    node_results = node_detector.predict(cv_image.get_bgr())
                    matched_nodes = node_detector.match_nodes(node_results, cv_image.get_gray(), merged_base)
                    debugger.set_nodes(bloodweb_iteration, matched_nodes)

                    # nothing detected
                    if len(matched_nodes) == 0:
                        print("nothing detected, trying again...")
                        if debug:
                            debugger.construct_and_show_images(bloodweb_iteration)
                        time.sleep(0.5) # try again
                        pyautogui.click()
                        continue

                    # prestige
                    elif len(matched_nodes) == 1 and matched_nodes[0].cls_name == NodeType.PRESTIGE:
                        prestige_total += 1
                        bp_total += 20000
                        if debug:
                            debugger.construct_and_show_images(bloodweb_iteration)
                        if bp_limit is not None and bp_total > bp_limit:
                            print("prestige level: reached bloodpoint limit. terminating")
                            self.emit("terminate")
                            self.emit("toggle_text", ("Bloodpoint limit reached.", False, False))
                            return

                        print("prestige level: selecting")
                        self.emit("prestige", (prestige_total, prestige_limit))
                        self.emit("bloodpoint", (bp_total, bp_limit))
                        centre = matched_nodes[0].box.centre()
                        centre.scale(ratio)
                        pyautogui.moveTo(*centre.xy())
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

                    # yolov5obb: detect and link all edges
                    print("yolov5obb: detect and link all edges")
                    edge_results = edge_detector.predict(cv_image.get_bgr())
                    avg_diameter = mean([(m.box.diameter()) for m in matched_nodes])
                    linked_edges = edge_detector.link_edges(edge_results, matched_nodes, avg_diameter)
                    debugger.set_edges(bloodweb_iteration, linked_edges)

                    # create networkx graph of nodes
                    print("creating networkx graph")
                    grapher = Grapher(matched_nodes, linked_edges) # all 9999
                    base_bloodweb = grapher.create()
                    debugger.set_base_bloodweb(bloodweb_iteration, base_bloodweb)

                    print("NODES")
                    max_len = max([len(node.unique_id) for node in matched_nodes])
                    for node_id, data in base_bloodweb.nodes.items():
                        print(f"    {str(node_id).ljust(2, ' ')} "
                              f"{str(data['name']).ljust(max_len, ' ')} "
                              f"{data['cls_name']}")
                    print("EDGES")
                    for edge in base_bloodweb.edges:
                        print(f"    {str(edge[0]).ljust(2, ' ')} "
                              f"{base_bloodweb.nodes[edge[0]]['name'].ljust(max_len, ' ')} "
                              f"{str(edge[1]).ljust(2, ' ')} "
                              f"{base_bloodweb.nodes[edge[1]]['name']}")

                    if debug:
                        debugger.construct_and_show_images(bloodweb_iteration)

                    update_iteration = 0
                    updated_nodes: List[UnmatchedNode] = matched_nodes.copy()
                    while True:
                        # new level
                        if not any([node.cls_name in NodeType.MULTI_UNCLAIMED for node in updated_nodes]):
                            print("level cleared")
                            time.sleep(1) # 1 sec to clear out until new level screen
                            pyautogui.click()
                            time.sleep(0.5) # in case of extra information on early level (e.g. lvl 2, 5, 10)
                            pyautogui.click()
                            time.sleep(0.5) # in case of yet more extra information on early level (e.g. lvl 10)
                            pyautogui.click()
                            time.sleep(2) # 2 secs to generate
                            break

                        # run through optimiser
                        print("optimiser")
                        optimiser = Optimiser(base_bloodweb)
                        optimiser.run(profile_id)
                        debugger.set_dijkstra(bloodweb_iteration, update_iteration, optimiser.dijkstra_graph)
                        print("    updated nodes")
                        for node_id, data in optimiser.dijkstra_graph.nodes.items():
                            print(f"        {str(node_id).ljust(2, ' ')} "
                                  f"{str(data['name']).ljust(max_len, ' ')} "
                                  f"{str(data['value']).ljust(10, ' ')} "
                                  f"{data['cls_name']}")

                        optimal_unlockable = optimiser.select_best()
                        selected_unlockable = [u for u in unlockables if u.unique_id == optimal_unlockable.name][0]
                        bp_total += Data.get_cost(selected_unlockable.rarity)
                        if bp_limit is not None and bp_total > bp_limit:
                            print(f"{optimal_unlockable.node_id}: reached bloodpoint limit. terminating")
                            self.emit("terminate")
                            self.emit("toggle_text", ("Bloodpoint limit reached.", False, False))
                            return

                        print(optimal_unlockable.node_id)
                        self.emit("bloodpoint", (bp_total, bp_limit))

                        # select perk: hold on the perk for 0.3s
                        pyautogui.moveTo(optimal_unlockable.x * ratio, optimal_unlockable.y * ratio)
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

                        # take new picture and update colours
                        print("updating bloodweb")
                        updated_image = screen_capture(base_res, ratio, crop=False)
                        debugger.add_updated_image(bloodweb_iteration, update_iteration, updated_image)

                        print("yolov8: detect all nodes")
                        updated_results = node_detector.predict(updated_image.get_bgr())
                        updated_nodes = node_detector.get_nodes(updated_results)
                        Grapher.update(base_bloodweb, updated_nodes)
                        update_iteration += 1
                    bloodweb_iteration += 1
        except:
            traceback.print_exc()
            self.emit("terminate")
            self.emit("toggle_text", (f"An error occurred. Please check "
                                      f"debug-{timestamp.strftime('%y-%m-%d %H-%M-%S')}.log for additional details.",
                                      True, False))

class State:
    version = "v1.0.0-alpha.1"

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