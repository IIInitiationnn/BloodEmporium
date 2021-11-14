from pprint import pprint

import cv2
import networkx as nx

from matcher import HoughTransform, Matcher
from mergedbase import MergedBase
from node import Node
from optimiser import Optimiser
from utils.network_util import NetworkUtil


class Simulation:
    def __init__(self, path_to_image, res, run_optimiser=True, alpha=1, beta=0):
        self.path_to_image = path_to_image
        self.res = res
        self.run_optimiser = run_optimiser
        self.alpha = alpha
        self.beta = beta

    def run(self):
        if self.run_optimiser:
            # initialisation: merged base for template matching
            merged_base = MergedBase(self.res)

        # hough transform: detect circles and lines
        nodes_connections = HoughTransform(self.path_to_image, self.res, alpha=self.alpha, beta=self.beta)
        self.num_circles = len(nodes_connections.circles)
        self.image = nodes_connections.output

        # cv2.imshow("matched origin", cv2.split(cv2.imread(f"assets/{nodes_connections.origin_type}", cv2.IMREAD_UNCHANGED))[2])
        # cv2.imshow("edges for matching lines", nodes_connections.edges)
        # cv2.imshow("unfiltered raw output (r-adjusted)", nodes_connections.output)
        # cv2.imshow("validated & processed output (r-adjusted)", nodes_connections.output_validated)
        # cv2.waitKey(0)

        if self.run_optimiser:
            # match circles to unlockables: create networkx graph of nodes
            matcher = Matcher(cv2.imread(self.path_to_image, cv2.IMREAD_GRAYSCALE), nodes_connections, merged_base)
            base_bloodweb = matcher.graph # all 9999

        i = 0
        run = self.run_optimiser
        while run:
            # correct reachable nodes
            for node_id, data in base_bloodweb.nodes.items():
                if any([base_bloodweb.nodes[neighbour]["is_user_claimed"] for neighbour in base_bloodweb.neighbors(node_id)]) \
                        and not data["is_accessible"]:
                    nx.set_node_attributes(base_bloodweb, Node.from_dict(data, is_accessible=True).get_dict())

            # run through optimiser
            optimiser = Optimiser(base_bloodweb)
            optimiser.run()
            optimal_unlockable = optimiser.select_best()
            pprint(optimal_unlockable.get_tuple())
            NetworkUtil.write_to_html(optimiser.dijkstra_graph, f"output/dijkstra{i}")

            # select the node
            optimal_unlockable.set_user_claimed(True)
            optimal_unlockable.set_value(9999)
            nx.set_node_attributes(base_bloodweb, optimal_unlockable.get_dict())
            i += 1

            if all([data["is_user_claimed"] for data in base_bloodweb.nodes.values()]):
                run = False
