import time
from pprint import pprint

import networkx as nx
from pynput.mouse import Button, Controller

import cv2
import numpy as np
import pyautogui

from matcher import Matcher, HoughTransform
from mergedbase import MergedBase
from node import Node
from optimiser import Optimiser

# TODO immediate priorities
#  - calibrate brightness of neutral using shaders
#  - calibrate brightness of background of default pack
#  - working with different UI scales -> adjust constants
#  - improve colour detection (occasional misidentified neutral and red nodes causes attempt to select invalid node)
from utils.network_util import NetworkUtil

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

'''
def main():
    all_unlockables = [("battery", False),
                       ("annotated_blueprint", False),
                       ("deja_vu", False),
                       ("sacrificial_cake", False),
                       ("butterfly_tape", True),
                       ("rubber_grip", True),
                       ("odd_stamp", False),
                       ("cutting_wire", True),
                       ("first_aid_kit", True),
                       ("vigos_jar_of_salty_lips", False),
                       ("bog_laurel_sachet", False)]
    edges = [("annotated_blueprint", "battery"),
             ("annotated_blueprint", "deja_vu"),
             ("annotated_blueprint", "sacrificial_cake"),
             ("annotated_blueprint", "butterfly_tape"),
             ("deja_vu", "sacrificial_cake"),
             ("butterfly_tape", "sacrificial_cake"),
             ("ORIGIN", "butterfly_tape"),
             ("ORIGIN", "first_aid_kit"),
             ("ORIGIN", "cutting_wire"),
             ("ORIGIN", "rubber_grip"),
             ("odd_stamp", "cutting_wire"),
             ("first_aid_kit", "vigos_jar_of_salty_lips"),
             ("vigos_jar_of_salty_lips", "bog_laurel_sachet")]

    i = 1
    graph = nx.Graph()

    desirable = ["first_aid_kit", "sacrificial_cake", "battery"]

    graph.add_nodes_from([Node("ORIGIN000", "ORIGIN", (0, 0), (250, 250), True, True).get_tuple()])
    graph.add_nodes_from([Node(f"{name}000", name, (1, 0) if name in desirable else (1, 5), (random.randrange(500), random.randrange(500)), is_accessible, False).get_tuple() for name, is_accessible in all_unlockables])
    graph.add_edges_from([(edge[0] + "000", edge[1] + "000") for edge in edges])

    layout = Layout() # improvedLayout=true by default
    net = Network(notebook=True, layout=layout, height=1080, width=1920)
    net.from_nx(graph)
    net.show("graph.html")


    while i < 12:
        op2 = Optimiser2(graph)
        pg = op2.pareto_graph
        selected = op2.select_best()

        selected.set_user_claimed(True)
        # print(selected.name, selected.value, selected.is_user_claimed)

        nx.set_node_attributes(graph, selected.get_dict())
        for neighbor in graph.neighbors(selected.get_id()):
            data = graph.nodes[neighbor]
            if not data['is_accessible']:
                nx.set_node_attributes(graph, Node.from_dict(data, is_accessible=True).get_dict())

        NetworkUtil.write_to_html(pg, f"optimiser2_run{i}")
        i += 1

    """while i < 12:
        optimiser = Optimiser(graph)
        sum_graphs, selected = optimiser.run()
        selected.set_user_claimed(True)
        print(selected.name, selected.value, selected.is_user_claimed, selected.is_entity_claimed)

        # temporary until openCV
        nx.set_node_attributes(graph, selected.set_value(9999).get_dict())
        for neighbor in graph.neighbors(selected.get_id()):
            data = graph.nodes[neighbor]
            if not data['is_accessible']:
                nx.set_node_attributes(graph, Node.from_dict(data, is_accessible=True).get_dict())

        network = Network(notebook=True, layout=layout, height=1080, width=1920)
        network.from_nx(sum_graphs)
        network.show(f"run{i}.html")
        i += 1"""'''

if __name__ == '__main__':
    production_mode = True

    # initialisation: merged base for template matching
    print("initialisation, merging")
    merged_base = MergedBase()
    mouse = Controller()
    if production_mode:
        mouse.position = (0, 0)

    i = 0
    while i < 10:
        # screen capture
        x, y, width, height = 250, 380, 800, 800
        if production_mode:
            print("capturing screen")
            path_to_image = f"pic{i}.png"
            image = pyautogui.screenshot(path_to_image, region=(x, y, width, height))
            image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        else:
            path_to_image = "training_data/bases/shaderless/base_nurse_2.png"

        # hough transform: detect circles and lines
        print("hough transform")
        nodes_connections = HoughTransform(path_to_image, 11, 10, 45, 5, 85, 40, 30, 25)

        # match circles to unlockables: create networkx graph of nodes
        print("match to unlockables")
        matcher = Matcher(cv2.imread(path_to_image, cv2.IMREAD_GRAYSCALE), nodes_connections, merged_base)
        base_bloodweb = matcher.graph # all 9999

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
        NetworkUtil.write_to_html(optimiser.dijkstra_graph, f"dijkstra{i}", notebook=False)

        # select perk
        if production_mode:
            # hold on the perk for 0.5s
            mouse.position = (x + optimal_unlockable.x, y + optimal_unlockable.y)
            mouse.press(Button.left)
            time.sleep(0.1)
            mouse.position = (0, 0)
            time.sleep(0.4)
            mouse.release(Button.left)

            # TODO temp click
            time.sleep(1)
            mouse.click(Button.left)
            time.sleep(1)

        i += 1

    time.sleep(30)
    '''for base in [os.path.join(subdir, file) for (subdir, dirs, files) in os.walk("training_data/bases") for file in files]:
        if "target" in base or "shaders" in base:
            continue
        nodes_connections = HoughTransform(base, 11, 10, 45, 5, 85, 40, 30, 25)'''