import logging
import os
import sys
import time
import traceback
from datetime import datetime
from multiprocessing import Process, Pipe

import pyautogui
from numpy import mean

from backend.config import Config
from backend.data import Data
from backend.edge_detection import EdgeDetection
from backend.image import CVImage
from backend.node_detection import NodeDetection
from backend.util.node_util import NodeType
from backend.util.text_util import TextUtil
from backend.util.timer import Timer
from debugger import Debugger
from grapher import Grapher
from mergedbase import MergedBase
from optimiser import Optimiser

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
yolo cfg="hyperparameters nodes v3.yaml"

yolov5obb edge detection
cd yolov5_obb
python train.py --hyp "../hyperparameters edges v2.yaml" --data ../datasets/roboflow/data.yaml --epochs 2000 --batch-size 16 --img 1024 --device 0 --patience 300 --adam 

POST 1.0.0
- preferences page: changing profile maintains tier order (need to refresh sort when sorting by tier)
- moris, reagents getting confused?
- backup configs every time they are written to, max of 100?
- log for main process
- tier slider
- shift selection and unselection
- maybe undo and redo last selection buttons at bottom
- "you have unsaved changes" next to save button - profiles, settings
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
hhh for new images (90% train, 10% val):
    - 1920 x 2160 (8:9 high)
    - 1280 x 1024 (5:4 low)
    - 2700 x 2160 (5:4 high)
    - 1280 x 960 (4:3 low)
    - 2880 x 2160 (4:3 high)
    - 1280 x 800 (8:5 low)
    - 2560 x 1600 (8:5 high)
    - 1280 x 720 (16:9 low)
    - 1920 x 1080 (16:9 mid)
    - 2560 x 1440 (16:9 high)
    - diff icon packs
    - with bloodpoints vs broke
    - diff bgs if possible
TODO
    - clean up edges
'''

class StateProcess(Process):
    def __init__(self, pipe: Pipe, args):
        Process.__init__(self)
        self.pipe = pipe
        self.args = args

    def mouse_click(self, primary_mouse, interaction):
        pyautogui.mouseDown(button=primary_mouse)
        if interaction == "press":
            pyautogui.moveTo(0, 0)
        else: # hold
            time.sleep(0.15)
            pyautogui.moveTo(0, 0)
            time.sleep(0.15)
        pyautogui.mouseUp(button=primary_mouse)

    def prestige_hold(self, primary_mouse):
        pyautogui.mouseDown(button=primary_mouse)
        time.sleep(1.5)
        pyautogui.mouseUp(button=primary_mouse)
        time.sleep(4) # 4 sec to clear out until new level screen
        pyautogui.click(button=primary_mouse)
        time.sleep(0.5) # prestige 1-3 => teachables, 4-6 => cosmetics, 7-9 => charms
        pyautogui.click(button=primary_mouse)
        time.sleep(0.5) # 1 sec to generate
        pyautogui.moveTo(0, 0)
        time.sleep(0.5) # 1 sec to generate

    # send data to main process via pipe
    def emit(self, signal_name, payload=()):
        self.pipe.send((signal_name, payload))

    def run(self):
        timestamp = datetime.now()
        config = Config()
        interaction = config.interaction()
        primary_mouse = config.primary_mouse()
        try:
            dev_mode, write_to_output, profile_id, character, is_naive_mode, prestige_limit, bp_limit = self.args
            Timer.PRINT = dev_mode
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

            # initialisation: merged base for template matching
            print(f"merging")
            unlockables = Data.get_unlockables()
            num_custom = len([u for u in unlockables if u.is_custom_icon])
            print(f"using {num_custom} custom icons and {len(unlockables) - num_custom} vanilla icons")
            print(f"using profile: {profile_id}")
            merged_base = MergedBase(character)
            pyautogui.moveTo(0, 0)

            debugger = Debugger(timestamp, write_to_output)
            debugger.set_merged_base(merged_base)

            bloodweb_iteration = 0
            if is_naive_mode:
                print("running in naive mode")
                while True:
                    if prestige_limit is not None and prestige_total == prestige_limit:
                        print("reached prestige limit. terminating")
                        self.emit("terminate")
                        self.emit("toggle_text", ("Prestige limit reached.", False, False))
                        return

                    # screen capture
                    print("capturing screen")
                    cv_image = CVImage.screen_capture()
                    debugger.set_image(bloodweb_iteration, cv_image)

                    # yolov8: detect accessible nodes
                    print("yolov8: detect accessible nodes")
                    results = node_detector.predict(cv_image.get_bgr())
                    matched_node = node_detector.match_accessible_or_prestige(results, cv_image.get_gray(), merged_base)
                    debugger.set_nodes(bloodweb_iteration, [matched_node])

                    # nothing detected
                    if matched_node is None:
                        time.sleep(0.5) # try again
                        pyautogui.click(button=primary_mouse)
                        continue

                    centre = matched_node.box.centre()

                    # prestige
                    if matched_node.cls_name == NodeType.PRESTIGE:
                        prestige_total += 1
                        bp_total += 20000
                        if dev_mode:
                            debugger.construct_and_show_images(bloodweb_iteration)
                        if bp_limit is not None and bp_total > bp_limit:
                            print("prestige level: reached bloodpoint limit. terminating")
                            self.emit("terminate")
                            self.emit("toggle_text", ("Bloodpoint limit reached.", False, False))
                            return

                        print("prestige level: selecting")
                        self.emit("prestige", (prestige_total, prestige_limit))
                        self.emit("bloodpoint", (bp_total, bp_limit))
                        pyautogui.moveTo(*centre.xy())
                        self.prestige_hold(primary_mouse)
                        continue

                    # accessible
                    best_unlockable = [u for u in unlockables if u.unique_id == matched_node.unique_id][0]
                    bp_total += Data.get_cost(best_unlockable.rarity)
                    if bp_limit is not None and bp_total > bp_limit:
                        if dev_mode:
                            debugger.construct_and_show_images(bloodweb_iteration)
                        print(f"{matched_node.unique_id}: reached bloodpoint limit. terminating")
                        self.emit("terminate")
                        self.emit("toggle_text", ("Bloodpoint limit reached.", False, False))
                        return

                    if dev_mode:
                        debugger.construct_and_show_images(bloodweb_iteration)

                    print(matched_node.unique_id)
                    self.emit("bloodpoint", (bp_total, bp_limit))

                    # select perk: hold on the perk for 0.3s
                    pyautogui.moveTo(*centre.xy())
                    self.mouse_click(primary_mouse, interaction)

                    # mystery box: click
                    if "mysteryBox" in matched_node.unique_id:
                        print("mystery box selected")
                        time.sleep(0.9)
                        pyautogui.click(button=primary_mouse)
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
                    cv_image = CVImage.screen_capture()
                    debugger.set_image(bloodweb_iteration, cv_image)

                    # yolov8: detect and match all nodes
                    print("yolov8: detect and match all nodes")
                    node_results = node_detector.predict(cv_image.get_bgr())
                    matched_nodes = node_detector.match_nodes(node_results, cv_image.get_gray(), merged_base)
                    debugger.set_nodes(bloodweb_iteration, matched_nodes)

                    # nothing detected
                    if len(matched_nodes) == 0:
                        print("nothing detected, trying again...")
                        if dev_mode:
                            debugger.construct_and_show_images(bloodweb_iteration)
                        time.sleep(0.5) # try again
                        pyautogui.click(button=primary_mouse)
                        continue

                    # prestige
                    elif len(matched_nodes) == 1 and matched_nodes[0].cls_name == NodeType.PRESTIGE:
                        prestige_total += 1
                        bp_total += 20000
                        if dev_mode:
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
                        pyautogui.moveTo(*centre.xy())
                        self.prestige_hold(primary_mouse)
                        continue

                    # yolov5obb: detect and link all edges
                    print("yolov5obb: detect and link all edges")
                    edge_results = edge_detector.predict(cv_image.get_bgr())
                    avg_diameter = mean([(m.box.diameter()) for m in matched_nodes])
                    linked_edges = edge_detector.link_edges(edge_results, matched_nodes, avg_diameter) # TODO maybe also return unlinked edges
                    debugger.set_edges(bloodweb_iteration, linked_edges)

                    # create networkx graph of nodes
                    print("creating networkx graph")
                    grapher = Grapher(matched_nodes, linked_edges) # all 9999
                    base_bloodweb = grapher.create()
                    debugger.set_base_bloodweb(bloodweb_iteration, base_bloodweb)

                    print("NODES")
                    print(TextUtil.justify(4, [[node_id, data["name"], data["cls_name"]]
                                               for node_id, data in base_bloodweb.nodes.items()]))
                    print("EDGES")
                    print(TextUtil.justify(4, [[edge[0], base_bloodweb.nodes[edge[0]]["name"], edge[1],
                                                base_bloodweb.nodes[edge[1]]["name"]] for edge in base_bloodweb.edges]))

                    if dev_mode:
                        debugger.construct_and_show_images(bloodweb_iteration)

                    update_iteration = 0
                    dijkstra_graphs = []
                    while True:
                        # run through optimiser
                        print("optimiser")
                        optimiser = Optimiser(base_bloodweb)
                        optimiser.run(profile_id)
                        debugger.set_dijkstra(bloodweb_iteration, update_iteration, optimiser.dijkstra_graph)
                        dijkstra_graphs.append(optimiser.dijkstra_graph)
                        objs = []
                        if update_iteration == 0: # initial dijkstra
                            print("    initial nodes")
                            for node_id, data in optimiser.dijkstra_graph.nodes.items():
                                objs.append([node_id, data["name"], data["value"], data["cls_name"]])
                        else: # updated dijkstra: any changes are shown from previous => current
                            print("    updated nodes")
                            last_graph = dijkstra_graphs[-2].nodes
                            for node_id, data in optimiser.dijkstra_graph.nodes.items():
                                last_data = last_graph[node_id]
                                value_changed = last_data["value"] != data["value"]
                                cls_name_changed = last_data["cls_name"] != data["cls_name"]
                                if value_changed or cls_name_changed:
                                    objs.append([node_id, data["name"],
                                                 (last_data["value"] if value_changed else ""),
                                                 ("=>" if value_changed else ""),
                                                 data["value"],
                                                 (last_data["cls_name"] if cls_name_changed else ""),
                                                 ("=>" if cls_name_changed else ""),
                                                 data["cls_name"]])
                        print(TextUtil.justify(8, objs))

                        best_node = optimiser.select_best()
                        best_unlockable = [u for u in unlockables if u.unique_id == best_node.name][0]
                        bp_total += Data.get_cost(best_unlockable.rarity)
                        if bp_limit is not None and bp_total > bp_limit:
                            print(f"{best_node.node_id} ({best_node.name}): reached bloodpoint limit. terminating")
                            self.emit("terminate")
                            self.emit("toggle_text", ("Bloodpoint limit reached.", False, False))
                            return

                        print(f"{best_node.node_id} ({best_node.name})")
                        self.emit("bloodpoint", (bp_total, bp_limit))

                        # select perk: press OR hold on the perk for 0.3s
                        pyautogui.moveTo(best_node.x, best_node.y)
                        self.mouse_click(primary_mouse, interaction)
                        grab_time = time.time()

                        # mystery box: click
                        if "mysteryBox" in best_node.name:
                            print("mystery box selected")
                            time.sleep(0.9)
                            pyautogui.click(button=primary_mouse)
                            time.sleep(0.2)

                        # move mouse again in case it didn't the first time
                        pyautogui.moveTo(0, 0)

                        # take new picture and update colours
                        print("updating bloodweb")
                        updated_image = CVImage.screen_capture()
                        debugger.add_updated_image(bloodweb_iteration, update_iteration, updated_image)

                        print("yolov8: detect all nodes")
                        updated_results = node_detector.predict(updated_image.get_bgr())
                        updated_nodes = node_detector.get_nodes(updated_results)
                        new_level = Grapher.update(base_bloodweb, updated_nodes, best_node)

                        # new level
                        if new_level:
                            print("level cleared")
                            time.sleep(1) # 1 sec to clear out until new level screen
                            pyautogui.click(button=primary_mouse)
                            time.sleep(0.5) # in case of extra information on early level (e.g. lvl 2, 5, 10)
                            pyautogui.click(button=primary_mouse)
                            time.sleep(0.5) # in case of yet more extra information on early level (e.g. lvl 10)
                            pyautogui.click(button=primary_mouse)
                            time.sleep(2) # 2 secs to generate
                            break
                        # else: # wait for bloodweb to update
                        #     time_since_grab = time.time() - grab_time
                        #     if time_since_grab < 0.75:
                        #         time.sleep(0.75 - time_since_grab)

                        update_iteration += 1
                    bloodweb_iteration += 1
        except:
            traceback.print_exc()
            self.emit("terminate")
            self.emit("toggle_text", (f"An error occurred. Please check "
                                      f"debug-{timestamp.strftime('%y-%m-%d %H-%M-%S')}.log for additional details.",
                                      True, False))

class State:
    version = "v1.1.0"
    pyautogui.FAILSAFE = False

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
            pyautogui.mouseUp(button=Config().primary_mouse()) # release if was held
            self.process.terminate()
            self.process = None
            print("process terminated")