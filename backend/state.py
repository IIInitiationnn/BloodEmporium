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
from backend.runtime import Runtime
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
Compile Pyinstaller: https://python.plainenglish.io/pyinstaller-exe-false-positive-trojan-virus-resolved-b33842bd3184

venv/Lib/site-packages/ultralytics/hub/utils.py Class Traces early return on __init__ and __call__
venv/Lib/site-packages/ultralytics/yolo/engine/predictor.py Class BasePredictor self.args.verbose = False

https://github.com/ultralytics/yolov5/issues/6948#issuecomment-1075528897
venv/Lib/site-packages/torch/nn/modules/upsampling.py Class BasePredictor self.args.verbose = False

TRAINING
yolov8 node detection
yolo cfg="hyperparameters nodes v4.yaml"

yolov5obb edge detection
cd yolov5_obb
python train.py --hyp "../hyperparameters edges v2.yaml" --data ../datasets/roboflow/data.yaml --epochs 2000 --batch-size 16 --img 1024 --device 0 --patience 300 --adam 

TODOs
- included profiles immutable (https://discord.com/channels/1016471051187802333/1205957357763301456)
- issues with black smokey pack (https://discord.com/channels/1016471051187802333/1208286052054470676)
- reorder steve and nancy perks between ash and yui instead of being in generic position
- put path in settings under "custom icons" checkbox so vanilla users dont have to do anything
- train bp balance ocr (maybe easyocr quicker?)
- in future, make a note on which batch each model has been trained on
- timer stops sometimes
- status on progress (starting, detecting bloodweb, optimising)
- systematic failsafe for bp if easyocr fails? (actually verify node region is correct, then verify ocr; diff res/aspect)
- issue 56: velyix pack on zooku's 2nd video
- config backup or some other method of preventing config corruption when reading / writing
- preferences page: changing profile maintains tier order (need to refresh sort when sorting by tier)
- moris, reagents getting confused?
- log for main process
- tier range filter
- shift selection and unselection
- maybe undo and redo last selection buttons at bottom
- "you have unsaved changes" next to save button - profiles, settings
- summary on items obtained by the application (aware only)
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

    def wait_slow(self, grab_time, num_nodes_claimed):
        time_since_grab = time.time() - grab_time
        wait_time = 0.4 + 0.4 * num_nodes_claimed # TODO record footage and test timing
        if time_since_grab < wait_time:
            time.sleep(wait_time - time_since_grab)

    def wait_level_cleared(self):
        time.sleep(1) # 1 sec to clear out until new level screen
        pyautogui.click(button=self.primary_mouse)
        time.sleep(0.5) # in case of extra information on early level (e.g. lvl 2, 5, 10)
        pyautogui.click(button=self.primary_mouse)
        time.sleep(0.5) # in case of yet more extra information on early level (e.g. lvl 10)
        pyautogui.click(button=self.primary_mouse)
        time.sleep(2) # 2 secs to generate

    def click_node(self):
        pyautogui.mouseDown(button=self.primary_mouse)
        if self.interaction == "press":
            pyautogui.moveTo(0, 0)
        else: # hold
            time.sleep(0.15)
            pyautogui.moveTo(0, 0)
            time.sleep(0.15)
        pyautogui.mouseUp(button=self.primary_mouse)

    def click_prestige(self):
        pyautogui.mouseDown(button=self.primary_mouse)
        if self.interaction == "hold":
            time.sleep(1.5)
        pyautogui.mouseUp(button=self.primary_mouse)
        time.sleep(4) # 4 sec to clear out until new level screen
        pyautogui.click(button=self.primary_mouse)
        time.sleep(0.5) # prestige 1-3 => teachables, 4-6 => cosmetics, 7-9 => charms
        pyautogui.click(button=self.primary_mouse)
        time.sleep(0.5) # 1 sec to generate
        pyautogui.moveTo(0, 0)
        time.sleep(0.5) # 1 sec to generate

    def click_origin(self, num_nodes):
        pyautogui.mouseDown(button=self.primary_mouse)
        if self.interaction == "hold":
            time.sleep(0.5)
        pyautogui.mouseUp(button=self.primary_mouse)
        time.sleep(2 + num_nodes / 13)

        pyautogui.click(button=self.primary_mouse)
        time.sleep(0.5) # in case of extra information on early level (e.g. lvl 2, 5, 10)
        pyautogui.click(button=self.primary_mouse)
        time.sleep(0.5) # in case of yet more extra information on early level (e.g. lvl 10)
        pyautogui.click(button=self.primary_mouse)
        pyautogui.moveTo(0, 0)
        time.sleep(2) # 2 secs to generate

    # send data to main process via pipe
    def emit(self, signal_name, payload=()):
        self.pipe.send((signal_name, payload))

    def run(self):
        timestamp = datetime.now()
        config = Config()
        self.interaction = config.interaction()
        self.primary_mouse = config.primary_mouse()

        runtime = Runtime()
        profile_id = runtime.profile()
        character = runtime.character()
        run_mode = runtime.mode()
        speed = runtime.speed()
        try:
            dev_mode, write_to_output, self.threshold_tier, self.threshold_subtier, \
                self.prestige_limit, self.bp_limit = self.args
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

            self.prestige_total = 0
            self.bp_total = 0
            self.emit("prestige", (self.prestige_total, self.prestige_limit))
            self.emit("bloodpoint", (self.bp_total, self.bp_limit))

            # initialisation: merged base for template matching
            print(f"initialising ({State.version})")
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
            # initial_bp_balance = 0
            print(f"run mode: {run_mode}")
            print(f"speed: {speed}")
            if run_mode == "naive":
                while True:
                    if self.prestige_limit is not None and self.prestige_total == self.prestige_limit:
                        print("reached prestige limit. terminating")
                        self.emit("terminate")
                        self.emit("toggle_text", ("Prestige limit reached.", False, False))
                        return

                    # screen capture
                    print("capturing screen")
                    cv_img = CVImage.screen_capture()
                    image_gray = cv_img.get_gray()
                    debugger.set_image(bloodweb_iteration, cv_img)

                    # yolov8: detect claimable nodes
                    print("yolov8: detect claimable nodes")
                    results = node_detector.predict(cv_img.get_bgr())
                    all_nodes, bp_node = node_detector.get_validate_all_nodes(results)

                    # TODO only match if necessary eg bp balance is much lower than limit
                    #  (use iri cost * number of unclaimed nodes)
                    matched_nodes = node_detector.match_nodes(all_nodes, image_gray, merged_base)
                    matched_claimable_nodes = [node for node in matched_nodes
                                               if node.cls_name in NodeType.MULTI_CLAIMABLE]
                    debugger.set_nodes(bloodweb_iteration, matched_nodes)

                    # nothing detected
                    if len(matched_claimable_nodes) == 0 or \
                            (len(matched_claimable_nodes) == 1 and
                             matched_claimable_nodes[0].cls_name in NodeType.MULTI_ORIGIN):
                        print("nothing detected, trying again...")
                        if dev_mode:
                            debugger.construct_and_show_images(bloodweb_iteration)
                        time.sleep(0.5) # try again
                        pyautogui.click(button=self.primary_mouse)
                        continue

                    # current_bp_balance = node_detector.calculate_bloodpoints(bp_node, image_gray)
                    # if bloodweb_iteration == 0:
                    #     initial_bp_balance = current_bp_balance
                    # self.bp_total = initial_bp_balance - current_bp_balance
                    # self.emit("bloodpoint", (self.bp_total, self.bp_limit))

                    total_bloodweb_cost = 0
                    for node in matched_claimable_nodes:
                        if node.cls_name in NodeType.MULTI_UNCLAIMED:
                            unlockable = [u for u in unlockables if u.unique_id == node.unique_id][0]
                            total_bloodweb_cost += Data.get_cost(unlockable.rarity, unlockable.type)

                    prestige = [node for node in matched_nodes if node.cls_name == NodeType.PRESTIGE]
                    origin_auto_enabled = [node for node in matched_nodes
                                           if node.cls_name == NodeType.ORIGIN_AUTO_ENABLED]

                    if any([node.cls_name == NodeType.ORIGIN_AUTO_DISABLED for node in matched_nodes]):
                        # disabled auto origin found
                        print("bloodpoints depleted. terminating")
                        self.emit("terminate")
                        self.emit("toggle_text", ("Bloodpoints depleted.", False, False))
                        return

                    if len(prestige) > 0:
                        # prestige node found
                        self.prestige_total += 1
                        if dev_mode:
                            debugger.construct_and_show_images(bloodweb_iteration)
                        if self.bp_limit is not None and self.bp_total + 20000 > self.bp_limit:
                            print("prestige level: reached bloodpoint limit. terminating")
                            self.emit("terminate")
                            self.emit("toggle_text", ("Bloodpoint limit reached.", False, False))
                            return
                        # if 20000 > current_bp_balance:
                        #     print("prestige level: bloodpoints depleted. terminating")
                        #     self.emit("terminate")
                        #     self.emit("toggle_text", ("Bloodpoints depleted.", False, False))
                        #     return

                        print("prestige level: selecting")
                        self.bp_total += 20000
                        self.emit("prestige", (self.prestige_total, self.prestige_limit))
                        self.emit("bloodpoint", (self.bp_total, self.bp_limit))

                        centre = prestige[0].box.centre()
                        pyautogui.moveTo(*centre.xy())
                        self.click_prestige()

                        # move mouse again in case it didn't the first time
                        pyautogui.moveTo(0, 0)
                        bloodweb_iteration += 1
                        continue

                    if len(origin_auto_enabled) > 0:
                        # enabled auto origin found
                        if dev_mode:
                            debugger.construct_and_show_images(bloodweb_iteration)

                        if self.bp_limit is not None and total_bloodweb_cost > self.bp_limit - self.bp_total:
                            # manual
                            pass
                        else:
                            print("auto origin (enabled): selecting")
                            self.bp_total += total_bloodweb_cost
                            self.emit("bloodpoint", (self.bp_total, self.bp_limit))
                            centre = origin_auto_enabled[0].box.centre()
                            pyautogui.moveTo(*centre.xy())
                            self.click_origin(len(matched_claimable_nodes))

                            # move mouse again in case it didn't the first time
                            pyautogui.moveTo(0, 0)
                            bloodweb_iteration += 1
                            continue

                    # no auto origin found: must be prestige 0; select manually OR
                    # auto origin found but total bloodweb cost exceeds bp limit

                    # yolov5obb: detect and link all edges
                    print("yolov5obb: detect and link all edges")
                    edge_detector = EdgeDetection()
                    edge_results = edge_detector.predict(cv_img.get_bgr())
                    avg_diameter = mean([(m.box.diameter()) for m in matched_nodes])
                    linked_edges = edge_detector.link_edges(edge_results, matched_nodes, avg_diameter)
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
                    while True:
                        optimiser = Optimiser(base_bloodweb)
                        optimiser.dijkstra_graph = base_bloodweb
                        debugger.set_dijkstra(bloodweb_iteration, update_iteration, optimiser.dijkstra_graph)

                        # prioritise inaccessible (select more than one node)
                        random_node = optimiser.select_random_prioritise_inaccessible()
                        random_unlockable = [u for u in unlockables if u.unique_id == random_node.name][0]
                        cost = Data.get_cost(random_unlockable.rarity, random_unlockable.type) # TODO need to do for entire path
                        if self.bp_limit is not None and self.bp_total + cost > self.bp_limit:
                            print(f"{random_node.node_id} {random_node.name}: reached bloodpoint limit. terminating")
                            self.emit("terminate")
                            self.emit("toggle_text", ("Bloodpoint limit reached.", False, False))
                            return
                        # if cost > current_bp_balance:
                        #     print(f"{random_node.node_id} {random_node.name}: bloodpoints depleted. terminating")
                        #     self.emit("terminate")
                        #     self.emit("toggle_text", ("Bloodpoints depleted.", False, False))
                        #     return

                        print(random_node.name)
                        self.bp_total += cost
                        self.emit("bloodpoint", (self.bp_total, self.bp_limit))

                        # select perk
                        pyautogui.moveTo(random_node.x, random_node.y)
                        self.click_node()
                        grab_time = time.time()

                        # mystery box: click TODO may have to move outside of this branch?
                        # if "mysteryBox" in random_node.name:
                        #     print("mystery box selected")
                        #     time.sleep(0.9)
                        #     pyautogui.click(button=self.primary_mouse)
                        #     time.sleep(0.2)

                        # wait if slow
                        if speed == "slow":
                            # will claim 1 if accessible, 2 or 3 if inaccessible, so wait for 3 to be safe
                            self.wait_slow(grab_time, 3 if random_node.cls_name == NodeType.INACCESSIBLE else 1)
                        # TODO fast speed may also need to wait for nodes to be consumed first, so maybe the wait
                        #  for multiple nodes should be extrapolated outside of this function? ie theres a base time
                        #  that both fast and slow should wait, but slow should wait more

                        # take new picture and update colours
                        print("updating bloodweb")
                        updated_img = CVImage.screen_capture()
                        debugger.add_updated_image(bloodweb_iteration, update_iteration, updated_img)

                        print("yolov8: detect claimable nodes")
                        updated_results = node_detector.predict(updated_img.get_bgr())
                        updated_nodes, updated_bp_node = node_detector.get_validate_all_nodes(updated_results)
                        new_level = Grapher.update(base_bloodweb, updated_nodes, random_node)
                        # current_bp_balance = node_detector.calculate_bloodpoints(updated_bp_node,
                        #                                                          updated_img.get_gray())
                        # self.bp_total = initial_bp_balance - current_bp_balance
                        # self.emit("bloodpoint", (self.bp_total, self.bp_limit))

                        # new level
                        if new_level:
                            print("level cleared")
                            self.wait_level_cleared()
                            break

                        update_iteration += 1

                # move mouse again in case it didn't the first time
                pyautogui.moveTo(0, 0)
                bloodweb_iteration += 1
            else:
                edge_detector = EdgeDetection()
                while True:
                    if self.prestige_limit is not None and self.prestige_total == self.prestige_limit:
                        print("reached prestige limit. terminating")
                        self.emit("terminate")
                        self.emit("toggle_text", ("Prestige limit reached.", False, False))
                        return

                    # screen capture
                    print("capturing screen")
                    cv_img = CVImage.screen_capture()
                    image_gray = cv_img.get_gray()
                    debugger.set_image(bloodweb_iteration, cv_img)

                    # yolov8: detect and match all nodes
                    print("yolov8: detect and match all nodes")
                    node_results = node_detector.predict(cv_img.get_bgr())
                    all_nodes, bp_node = node_detector.get_validate_all_nodes(node_results)
                    matched_nodes = node_detector.match_nodes(all_nodes, image_gray, merged_base)
                    debugger.set_nodes(bloodweb_iteration, matched_nodes)

                    # nothing detected
                    if len(matched_nodes) == 0 or \
                            (len(matched_nodes) == 1 and matched_nodes[0].cls_name in NodeType.MULTI_ORIGIN):
                        print("nothing detected, trying again...")
                        if dev_mode:
                            debugger.construct_and_show_images(bloodweb_iteration)
                        time.sleep(0.5) # try again
                        pyautogui.click(button=self.primary_mouse)
                        continue

                    # current_bp_balance = node_detector.calculate_bloodpoints(bp_node, image_gray)
                    # if bloodweb_iteration == 0:
                    #     initial_bp_balance = current_bp_balance
                    # self.bp_total = initial_bp_balance - current_bp_balance
                    # self.emit("bloodpoint", (self.bp_total, self.bp_limit))

                    prestige = [node for node in matched_nodes if node.cls_name == NodeType.PRESTIGE]
                    origin_auto_enabled = [node for node in matched_nodes
                                           if node.cls_name == NodeType.ORIGIN_AUTO_ENABLED]

                    # fast-forward levels with <= 6 nodes (excl. origin): autobuy if possible
                    fast_forward = len([node for node in matched_nodes
                                        if node.cls_name not in NodeType.MULTI_ORIGIN]) <= 6
                    override_slow = False

                    # prestige
                    if len(prestige) > 0:
                        self.prestige_total += 1
                        if dev_mode:
                            debugger.construct_and_show_images(bloodweb_iteration)
                        if self.bp_limit is not None and self.bp_total + 20000 > self.bp_limit:
                            print("prestige level: reached bloodpoint limit. terminating")
                            self.emit("terminate")
                            self.emit("toggle_text", ("Bloodpoint limit reached.", False, False))
                            return
                        # if 20000 > current_bp_balance:
                        #     print("prestige level: bloodpoints depleted. terminating")
                        #     self.emit("terminate")
                        #     self.emit("toggle_text", ("Bloodpoints depleted.", False, False))
                        #     return

                        print("prestige level: selecting")
                        self.bp_total += 20000
                        self.emit("prestige", (self.prestige_total, self.prestige_limit))
                        self.emit("bloodpoint", (self.bp_total, self.bp_limit))
                        centre = matched_nodes[0].box.centre()
                        pyautogui.moveTo(*centre.xy())
                        self.click_prestige()
                        bloodweb_iteration += 1
                        continue
                    elif fast_forward and len(origin_auto_enabled) > 0:
                        # enabled auto origin found
                        total_bloodweb_cost = 0
                        for node in matched_nodes:
                            if node.cls_name in NodeType.MULTI_UNCLAIMED:
                                unlockable = [u for u in unlockables if u.unique_id == node.unique_id][0]
                                total_bloodweb_cost += Data.get_cost(unlockable.rarity, unlockable.type)
                        if dev_mode:
                            debugger.construct_and_show_images(bloodweb_iteration)

                        if self.bp_limit is not None and total_bloodweb_cost > self.bp_limit - self.bp_total:
                            # manual: start edge detection and optimal non-auto selection but without waiting
                            override_slow = True
                        else:
                            print("auto origin (enabled) from fast forward: selecting")
                            self.bp_total += total_bloodweb_cost
                            self.emit("bloodpoint", (self.bp_total, self.bp_limit))
                            centre = origin_auto_enabled[0].box.centre()
                            pyautogui.moveTo(*centre.xy())
                            self.click_origin(len(matched_nodes))
                            bloodweb_iteration += 1
                            continue
                    elif any([node.cls_name == NodeType.ORIGIN_AUTO_DISABLED for node in matched_nodes]):
                        # disabled auto origin found
                        print("bloodpoints depleted. terminating")
                        self.emit("terminate")
                        self.emit("toggle_text", ("Bloodpoints depleted.", False, False))
                        return

                    # yolov5obb: detect and link all edges
                    print("yolov5obb: detect and link all edges")
                    edge_results = edge_detector.predict(cv_img.get_bgr())
                    avg_diameter = mean([(m.box.diameter()) for m in matched_nodes])
                    linked_edges = edge_detector.link_edges(edge_results, matched_nodes, avg_diameter)
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

                        # auto-purchase from all unlockables same sub/tier OR below threshold (if applicable)
                        remaining_bloodweb_cost = 0
                        num_remaining_nodes = 0
                        for data in base_bloodweb.nodes.values():
                            if data["cls_name"] in NodeType.MULTI_UNCLAIMED:
                                unlockable = [u for u in unlockables if u.unique_id == data["name"]][0]
                                remaining_bloodweb_cost += Data.get_cost(unlockable.rarity, unlockable.type)
                                num_remaining_nodes += 1
                        if len(origin_auto_enabled) > 0 and \
                                optimiser.can_auto_purchase(profile_id, self.threshold_tier,
                                                            self.threshold_subtier) and \
                                (self.bp_limit is None or remaining_bloodweb_cost <= self.bp_limit - self.bp_total):
                            print("auto origin (enabled) from auto purchase: selecting")
                            self.bp_total += remaining_bloodweb_cost
                            self.emit("bloodpoint", (self.bp_total, self.bp_limit))
                            centre = origin_auto_enabled[0].box.centre()
                            pyautogui.moveTo(*centre.xy())
                            self.click_origin(num_remaining_nodes)
                            print("level cleared")
                            break

                        if run_mode == "aware_single":
                            best_node = optimiser.select_best_single()
                            best_nodes = [best_node]
                            u = [u for u in unlockables if u.unique_id == best_node.name][0]
                            cost = Data.get_cost(u.rarity, u.type)
                        else:
                            best_nodes = optimiser.select_best_multi(unlockables) # TODO incorporate into debugging
                            best_node = best_nodes[-1]
                            us = [[u for u in unlockables if u.unique_id == node.name][0] for node in best_nodes]
                            cost = sum([Data.get_cost(u.rarity, u.type) for u in us])
                        if self.bp_limit is not None and self.bp_total + cost > self.bp_limit:
                            print(f"{best_node.node_id} ({best_node.name}): reached bloodpoint limit. terminating")
                            self.emit("terminate")
                            self.emit("toggle_text", ("Bloodpoint limit reached.", False, False))
                            return
                        # if cost > current_bp_balance:
                        #     print(f"{best_node.node_id} ({best_node.name}): bloodpoints depleted. terminating")
                        #     self.emit("terminate")
                        #     self.emit("toggle_text", ("Bloodpoints depleted.", False, False))
                        #     return

                        print(f"{best_node.node_id} ({best_node.name})")
                        self.bp_total += cost
                        self.emit("bloodpoint", (self.bp_total, self.bp_limit))

                        # select perk: press OR hold on the perk for 0.3s
                        pyautogui.moveTo(best_node.x, best_node.y)
                        self.click_node()
                        grab_time = time.time()

                        # mystery box: click
                        # if "mysteryBox" in best_node.name:
                        #     print("mystery box selected")
                        #     time.sleep(0.9)
                        #     pyautogui.click(button=self.primary_mouse)
                        #     time.sleep(0.2)

                        # move mouse again in case it didn't the first time
                        pyautogui.moveTo(0, 0)

                        # wait if slow
                        if speed == "slow" and not override_slow:
                            self.wait_slow(grab_time, len(best_nodes))
                        # TODO fast speed may also need to wait for nodes to be consumed first, so maybe the wait
                        #  for multiple nodes should be extrapolated outside of this function? ie theres a base time
                        #  that both fast and slow should wait, but slow should wait more

                        # take new picture and update colours
                        print("updating bloodweb")
                        updated_img = CVImage.screen_capture()
                        debugger.add_updated_image(bloodweb_iteration, update_iteration, updated_img)

                        print("yolov8: detect all nodes")
                        updated_results = node_detector.predict(updated_img.get_bgr())
                        updated_nodes, updated_bp_node = node_detector.get_validate_all_nodes(updated_results)
                        new_level = Grapher.update(base_bloodweb, updated_nodes, best_node)
                        # current_bp_balance = node_detector.calculate_bloodpoints(updated_bp_node,
                        #                                                          updated_img.get_gray())
                        # self.bp_total = initial_bp_balance - current_bp_balance
                        # self.emit("bloodpoint", (self.bp_total, self.bp_limit))
                        if any([node.cls_name == NodeType.ORIGIN_AUTO_DISABLED for node in updated_nodes]):
                            # disabled auto origin found
                            print("bloodpoints depleted. terminating")
                            self.emit("terminate")
                            self.emit("toggle_text", ("Bloodpoints depleted.", False, False))
                            return

                        # new level
                        if new_level:
                            print("level cleared")
                            self.wait_level_cleared()
                            break

                        update_iteration += 1
                    bloodweb_iteration += 1
        except:
            traceback.print_exc()
            self.emit("terminate")
            self.emit("toggle_text", (f"An error occurred. Please check {os.getcwd()}\\logs\\"
                                      f"debug-{timestamp.strftime('%y-%m-%d %H-%M-%S')}.log for additional details.",
                                      True, False))

class State:
    version = "v1.2.4"
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