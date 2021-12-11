import copy
import math
import random

import networkx as nx

from config import Config
from node import Node


class Optimiser:
    def __init__(self, graph):
        self.base_graph = graph
        self.dijkstra_graph = None

    def dijkstra(self, desired_node_id, tier, subtier):
        heatmap = copy.deepcopy(self.base_graph)
        desired_value = -(9999 * tier + subtier)
        base_data = self.base_graph.nodes[desired_node_id]
        nx.set_node_attributes(heatmap, Node.from_dict(base_data, value=desired_value).get_dict())

        if heatmap.nodes[desired_node_id]["is_accessible"]:
            return heatmap

        edited = True
        while edited:
            edited = False
            for node_id, data in heatmap.nodes.items():
                if node_id == "ORIGIN":
                    continue

                neighbor_values = [heatmap.nodes[neighbor]["value"] for neighbor in heatmap.neighbors(node_id)
                                   if not heatmap.nodes[neighbor]["is_accessible"]]
                lowest_neighbor_value = min(neighbor_values) if len(neighbor_values) > 0 else 9999 # if node is not connected to rest of graph
                if data["value"] > lowest_neighbor_value + 1:
                    nx.set_node_attributes(heatmap, Node.from_dict(data, value=lowest_neighbor_value + 1).get_dict())
                    edited = True

        return heatmap

    @staticmethod
    def add_graphs(graphs):
        total = copy.deepcopy(graphs[0])
        for graph in graphs[1:]:
            for node_id, data in graph.nodes.items():
                total_data = total.nodes[node_id]
                nx.set_node_attributes(total, Node.from_dict(total_data, value=total_data["value"] + data["value"]).get_dict())
        return total

    def select_best(self):
        min_id, min_val = ["ORIGIN"], [math.inf]
        for node_id, data in self.dijkstra_graph.nodes.items():
            if data["is_accessible"] and not data["is_user_claimed"]:
                if data["value"] < min(min_val):
                    min_id, min_val = [node_id], [data["value"]]
                elif data["value"] == min(min_val):
                    min_id.append(node_id)
                    min_val.append(data["value"])

        return Node.from_dict(self.dijkstra_graph.nodes[random.choice(min_id)])

    def run(self):
        config = Config()
        graphs = []
        for node_id, data in self.base_graph.nodes.items():
            if data["is_user_claimed"]: # claimed
                pass
            else:
                tier, subtier = config.preference(data["name"])
                if tier > 0: # desirable and unclaimed
                    graphs.append(self.dijkstra(node_id, tier, subtier))
                elif tier < 0: # temp: undesirable and unclaimed
                    heatmap = copy.deepcopy(self.base_graph)
                    cost = heatmap.nodes[node_id]["value"] + 9999 * tier + subtier
                    nx.set_node_attributes(heatmap, Node.from_dict(heatmap.nodes[node_id], value=cost).get_dict())
                    graphs.append(heatmap)

        if len(graphs) == 0:
            graphs = [self.base_graph]

        # TODO in the future, add desirability (lower weight (value)) to nodes which are in danger and are desirable
        self.dijkstra_graph = self.add_graphs(graphs)