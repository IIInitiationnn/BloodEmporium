from pprint import pprint
import random

import cv2
import networkx as nx
import numpy as np
import os
from pyvis.network import Network
from pyvis.options import Layout

from mergedbase import MergedBase
from node import Node
from optimiser import Optimiser
from matcher import Matcher, HoughTransform
from optimiser2 import Optimiser2
from utils.network_util import NetworkUtil
from utils.training_util import CircleTrainer

# TODO immediate priorities
#  - calibrate brightness of neutral using shaders
#  - calibrate brightness of background of default pack

''' timeline
    - backend with algorithm
    - openCV icon recognition
    - desire values from config file
        - can have multiple sets of desire values and can switch
    - frontend with GUI
        - debug mode using pyvis showing matched unlockables, paths and selected nodes
    - for higher matching accuracy, either auto detect with text recognition or just manual option in frontend
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
    # initialisation: merged base for template matching
    print("initialisation, merging")
    merged_base = MergedBase()

    # hough transform: detect circles and lines
    print("hough transform")
    path_to_image = "training_data/bases/shaderless/base_spirit.png"
    nodes_connections = HoughTransform(path_to_image, 11, 10, 45, 5, 85, 40, 30, 25)

    # match circles to unlockables: create networkx graph of nodes
    print("match to unlockables")
    matcher = Matcher(cv2.imread(path_to_image, cv2.IMREAD_GRAYSCALE), nodes_connections, merged_base)
    base_bloodweb = matcher.graph # all 9999

    # run through optimiser
    print("optimiser")
    optimiser = Optimiser(base_bloodweb)
    optimiser.run()
    pprint(optimiser.select_best().get_tuple())

    '''for base in [os.path.join(subdir, file) for (subdir, dirs, files) in os.walk("training_data/bases") for file in files]:
        if "target" in base or "shaders" in base:
            continue
        nodes_connections = HoughTransform(base, 11, 10, 45, 5, 85, 40, 30, 25)'''

    cv2.destroyAllWindows()