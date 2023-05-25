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

1.1.0
- 6.7.0 changes
- bloodpoint spend cost without using item rarity (top right bloodweb balance is more accurate)
- auto buy for early levels IF correct origin
- config backup or some other method of preventing config corruption when reading / writing
- show time elapsed under bp / prestige limit + status on progress (starting, detecting bloodweb, optimising)
- installer + autoupdate
- antivirus false positive

POST 1.0.0
- preferences page: changing profile maintains tier order (need to refresh sort when sorting by tier)
- moris, reagents getting confused?
- backup configs every time they are written to, max of 100?
- log for main process
- tier range filter
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

    def wait_slow(self, grab_time, num_nodes_claimed):
        time_since_grab = time.time() - grab_time
        wait_time = 0.4 + 0.4 * num_nodes_claimed # TODO record footage and test timing
        if time_since_grab < wait_time:
            time.sleep(wait_time - time_since_grab)

    def wait_level_cleared(self, primary_mouse):
        time.sleep(1) # 1 sec to clear out until new level screen
        pyautogui.click(button=primary_mouse)
        time.sleep(0.5) # in case of extra information on early level (e.g. lvl 2, 5, 10)
        pyautogui.click(button=primary_mouse)
        time.sleep(0.5) # in case of yet more extra information on early level (e.g. lvl 10)
        pyautogui.click(button=primary_mouse)
        time.sleep(2) # 2 secs to generate

    def click_node(self, primary_mouse, interaction):
        pyautogui.mouseDown(button=primary_mouse)
        if interaction == "press":
            pyautogui.moveTo(0, 0)
        else: # hold
            time.sleep(0.15)
            pyautogui.moveTo(0, 0)
            time.sleep(0.15)
        pyautogui.mouseUp(button=primary_mouse)

    def click_prestige(self, primary_mouse, interaction):
        pyautogui.mouseDown(button=primary_mouse)
        if interaction == "hold":
            time.sleep(1.5)
        pyautogui.mouseUp(button=primary_mouse)
        time.sleep(4) # 4 sec to clear out until new level screen
        pyautogui.click(button=primary_mouse)
        time.sleep(0.5) # prestige 1-3 => teachables, 4-6 => cosmetics, 7-9 => charms
        pyautogui.click(button=primary_mouse)
        time.sleep(0.5) # 1 sec to generate
        pyautogui.moveTo(0, 0)
        time.sleep(0.5) # 1 sec to generate

    def click_origin(self, primary_mouse, interaction, num_nodes):
        pyautogui.mouseDown(button=primary_mouse)
        if interaction == "hold":
            time.sleep(0.5)
        pyautogui.mouseUp(button=primary_mouse)
        time.sleep(4 + num_nodes / 13)

    # send data to main process via pipe
    def emit(self, signal_name, payload=()):
        self.pipe.send((signal_name, payload))

    def run(self):
        timestamp = datetime.now()
        config = Config()
        interaction = config.interaction()
        primary_mouse = config.primary_mouse()

        runtime = Runtime()
        profile_id = runtime.profile()
        character = runtime.character()
        run_mode = runtime.mode()
        speed = runtime.speed()
        try:
            dev_mode, write_to_output, prestige_limit, bp_limit = self.args
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
            print(f"run mode: {run_mode}")
            if run_mode == "naive":
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

                    # yolov8: detect claimable nodes
                    print("yolov8: detect claimable nodes")
                    results = node_detector.predict(cv_image.get_bgr())
                    all_nodes, bp_node = node_detector.get_validate_all_nodes(results)
                    # TODO bloodpoint balance from all_nodes
                    # TODO only match if necessary eg bp balance is much lower than limit
                    #  (use iri cost * number of unclaimed nodes)
                    matched_nodes = node_detector.match_nodes(all_nodes, cv_image.get_gray(), merged_base)
                    matched_claimable_nodes = [node for node in matched_nodes
                                               if node.cls_name in NodeType.MULTI_CLAIMABLE]
                    debugger.set_nodes(bloodweb_iteration, matched_nodes)

                    # nothing detected
                    if len(matched_claimable_nodes) == 0:
                        print("nothing detected, trying again...")
                        time.sleep(0.5) # try again
                        pyautogui.click(button=primary_mouse)
                        continue

                    prestige = [node for node in matched_claimable_nodes if node.cls_name == NodeType.PRESTIGE]
                    origin_auto_enabled = [node for node in matched_claimable_nodes
                                           if node.cls_name == NodeType.ORIGIN_AUTO_ENABLED]

                    # TODO update bp_total for all branches
                    if len(prestige) > 0:
                        # prestige node found
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

                        centre = prestige[0].box.centre()
                        pyautogui.moveTo(*centre.xy())
                        self.click_prestige(primary_mouse, interaction)
                    elif len(origin_auto_enabled) > 0:
                        # enabled auto origin found
                        total_bloodweb_cost = 0
                        for node in matched_claimable_nodes:
                            if node.cls_name in NodeType.MULTI_UNCLAIMED:
                                unlockable = [u for u in unlockables if u.unique_id == node.unique_id][0]
                                total_bloodweb_cost += Data.get_cost(unlockable.rarity)

                        if dev_mode:
                            debugger.construct_and_show_images(bloodweb_iteration)
                        print("auto origin (enabled): selecting")
                        self.emit("bloodpoint", (bp_total, bp_limit))

                        if total_bloodweb_cost > bp_limit - bp_total:
                            # manual TODO select random node repeatedly until new level, same logic as else branch
                            pass
                        else:
                            centre = origin_auto_enabled[0].box.centre()
                            pyautogui.moveTo(*centre.xy())
                            self.click_origin(primary_mouse, interaction, len(matched_claimable_nodes))
                    elif any([node.cls_name == NodeType.ORIGIN_AUTO_DISABLED for node in matched_claimable_nodes]):
                        # disabled auto origin found
                        print("bloodpoints depleted. terminating")
                        self.emit("terminate")
                        self.emit("toggle_text", ("Bloodpoints depleted.", False, False))
                    else:
                        # no auto origin found: must be prestige 0; select manually
                        # create networkx graph of nodes without edges
                        print("creating networkx graph")
                        grapher = Grapher(matched_nodes, []) # all 9999
                        base_bloodweb = grapher.create()
                        debugger.set_base_bloodweb(bloodweb_iteration, base_bloodweb)

                        print("NODES")
                        print(TextUtil.justify(4, [[node_id, data["name"], data["cls_name"]]
                                                   for node_id, data in base_bloodweb.nodes.items()]))

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
                            bp_total += Data.get_cost(random_unlockable.rarity)
                            if bp_limit is not None and bp_total > bp_limit:
                                print(f"{random_node.name}: reached bloodpoint limit. terminating")
                                self.emit("terminate")
                                self.emit("toggle_text", ("Bloodpoint limit reached.", False, False))
                                return

                            print(random_node.name)
                            self.emit("bloodpoint", (bp_total, bp_limit))

                            # select perk
                            pyautogui.moveTo(random_node.x, random_node.y)
                            self.click_node(primary_mouse, interaction)
                            grab_time = time.time()

                            # mystery box: click TODO may have to move outside of this branch?
                            if "mysteryBox" in random_node.name:
                                print("mystery box selected")
                                time.sleep(0.9)
                                pyautogui.click(button=primary_mouse)
                                time.sleep(0.2)

                            # wait if slow
                            if speed == "slow":
                                # will claim 1 if accessible, 2 or 3 if inaccessible, so wait for 3 to be safe
                                self.wait_slow(grab_time, 3 if random_node.cls_name == NodeType.INACCESSIBLE else 1)
                            # TODO fast speed may also need to wait for nodes to be consumed first, so maybe the wait
                            #  for multiple nodes should be extrapolated outside of this function? ie theres a base time
                            #  that both fast and slow should wait, but slow should wait more

                            # take new picture and update colours
                            print("updating bloodweb")
                            updated_image = CVImage.screen_capture()
                            debugger.add_updated_image(bloodweb_iteration, update_iteration, updated_image)

                            print("yolov8: detect claimable nodes")
                            updated_results = node_detector.predict(updated_image.get_bgr())
                            updated_nodes, bp_node = node_detector.get_validate_all_nodes(updated_results)
                            new_level = Grapher.update(base_bloodweb, updated_nodes, random_node)

                            # new level
                            if new_level:
                                print("level cleared")
                                self.wait_level_cleared(primary_mouse)
                                break

                            update_iteration += 1

                    # move mouse again in case it didn't the first time
                    pyautogui.moveTo(0, 0)
                    bloodweb_iteration += 1
            else:
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
                    all_nodes, bp_node = node_detector.get_validate_all_nodes(node_results)
                    matched_nodes = node_detector.match_nodes(all_nodes, cv_image.get_gray(), merged_base)
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
                        self.click_prestige(primary_mouse, interaction)
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

                        if run_mode == "aware_single":
                            best_node = optimiser.select_best_single()
                            best_nodes = [best_node]
                            u = [u for u in unlockables if u.unique_id == best_node.name][0]
                            bp_total += Data.get_cost(u.rarity)
                        else:
                            best_nodes = optimiser.select_best_multi(unlockables) # TODO incorporate into debugging
                            best_node = best_nodes[-1]
                            us = [[u for u in unlockables if u.unique_id == node.name][0] for node in best_nodes]
                            bp_total += sum([Data.get_cost(u.rarity) for u in us])
                        if bp_limit is not None and bp_total > bp_limit:
                            print(f"{best_node.node_id} ({best_node.name}): reached bloodpoint limit. terminating")
                            self.emit("terminate")
                            self.emit("toggle_text", ("Bloodpoint limit reached.", False, False))
                            return

                        print(f"{best_node.node_id} ({best_node.name})")
                        self.emit("bloodpoint", (bp_total, bp_limit))

                        # select perk: press OR hold on the perk for 0.3s
                        pyautogui.moveTo(best_node.x, best_node.y)
                        self.click_node(primary_mouse, interaction)
                        grab_time = time.time()

                        # mystery box: click
                        if "mysteryBox" in best_node.name:
                            print("mystery box selected")
                            time.sleep(0.9)
                            pyautogui.click(button=primary_mouse)
                            time.sleep(0.2)

                        # move mouse again in case it didn't the first time
                        pyautogui.moveTo(0, 0)

                        # wait if slow
                        if speed == "slow":
                            self.wait_slow(grab_time, len(best_nodes))
                        # TODO fast speed may also need to wait for nodes to be consumed first, so maybe the wait
                        #  for multiple nodes should be extrapolated outside of this function? ie theres a base time
                        #  that both fast and slow should wait, but slow should wait more

                        # take new picture and update colours
                        print("updating bloodweb")
                        updated_image = CVImage.screen_capture()
                        debugger.add_updated_image(bloodweb_iteration, update_iteration, updated_image)

                        print("yolov8: detect all nodes")
                        updated_results = node_detector.predict(updated_image.get_bgr())
                        updated_nodes, updated_bp_node = node_detector.get_validate_all_nodes(updated_results)
                        new_level = Grapher.update(base_bloodweb, updated_nodes, best_node)

                        # new level
                        if new_level:
                            print("level cleared")
                            self.wait_level_cleared(primary_mouse)
                            break

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