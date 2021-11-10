from pprint import pprint
import random

import cv2
import networkx as nx
import numpy as np
from pyvis.network import Network
from pyvis.options import Layout

from mergedbase import MergedBase
from node import Node
from optimiser import Optimiser
from matcher import Matcher, HoughTransform
from utils.training_util import CircleTrainer

''' timeline
    - backend with algorithm
    - openCV icon recognition
    - desire values from config file
        - can have multiple sets of desire values and can switch
    - frontend with GUI
        - debug mode using pyvis showing matched unlockables, paths and selected nodes
    - for higher matching accuracy, either auto detect with text recognition or just manual option in frontend
        to only select nurse unlockables, or survivor unlockables for instance
    - icon with entity hand (like EGC) grasping shards or bloodpoints or just a bloody entity hand
    
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
    -> identify lines and circles
        - circle: id, centre, colour
        - line: circles it joins
    -> matching circles to unlockable
        - networkx graph of nodes
    -> optimiser
        - optimal unlockable
    -> mouse
        - hold on position
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

    graph.add_nodes_from([Node("ORIGIN000", "ORIGIN", 9999, (250, 250), True, True, False).get_tuple()])
    graph.add_nodes_from([Node(f"{name}000", name, 9999, (random.randrange(500), random.randrange(500)), is_accessible, False, False).get_tuple() for name, is_accessible in all_unlockables])
    graph.add_edges_from([(edge[0] + "000", edge[1] + "000") for edge in edges])

    layout = Layout() # improvedLayout=true by default
    net = Network(notebook=True, layout=layout, height=1080, width=1920)
    net.from_nx(graph)
    net.show("graph.html")

    while i < 12:
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
        i += 1

if __name__ == '__main__':
    # initialisation: merged base for template matching
    merged_base = MergedBase()

    # hough transform: detect circles and lines
    image = cv2.imread("training_data/bases/base.png", cv2.IMREAD_GRAYSCALE)
    nodes_connections = HoughTransform(image, 11, 10, 45, 5, 85, 40, 30, 25)

    matcher = Matcher(image, nodes_connections, merged_base)
    base_bloodweb = matcher.graph # all 9999

    # run through optimiser

    # CircleTrainer()

    ''' use this for identifying origin
    image = cv2.split(cv2.imread("training_data/bases/base_larger.png", cv2.IMREAD_UNCHANGED))[2]
    template = cv2.resize(cv2.split(cv2.imread("assets/origin_basic.png", cv2.IMREAD_UNCHANGED))[2], (38, 38), interpolation=cv2.INTER_AREA)

    template_alpha = cv2.resize(cv2.split(cv2.imread("assets/origin_basic.png", cv2.IMREAD_UNCHANGED))[3], (38, 38), interpolation=cv2.INTER_AREA) # for masking
    result = cv2.matchTemplate(image, template, cv2.TM_CCORR_NORMED, mask=template_alpha)

    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    top_left = max_loc
    bottom_right = (top_left[0] + 38, top_left[1] + 38)
    cv2.rectangle(image, top_left, bottom_right, 255, 2) # 255 = white; 2 = thickness

    cv2.imshow("template", template)
    cv2.imshow("result", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()'''
