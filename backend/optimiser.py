import copy
import math
import random

import networkx as nx

from backend.util.node_util import NodeType
from config import Config
from graph_node import GraphNode


class Optimiser:
    TIER_VALUE = 100000
    SUBTIER_VALUE = 10

    def __init__(self, graph):
        self.base_graph = graph
        self.shortest_paths = dict(nx.all_pairs_shortest_path(self.base_graph))
        self.dijkstra_graph = None

    # deprecated
    def dijkstra(self, node_id, tier, subtier):
        # run dijkstra map for node corresponding to node_id
        heatmap = copy.deepcopy(self.base_graph)

        # the lower this number, the higher the priority
        desired_value = -(Optimiser.TIER_VALUE * tier + subtier * Optimiser.SUBTIER_VALUE)
        base_data = self.base_graph.nodes[node_id]
        nx.set_node_attributes(heatmap, GraphNode.from_dict(base_data, value=desired_value).get_dict())

        # for this graph, if the node is already accessible, its value cannot be decreased or increased by neighbours
        if heatmap.nodes[node_id]["cls_name"] == NodeType.ACCESSIBLE:
            return heatmap

        edited = True
        while edited:
            edited = False
            for node_id, data in heatmap.nodes.items():
                if data["cls_name"] not in NodeType.MULTI_UNCLAIMED:
                    continue

                #         O-\
                #         |  \
                # A - B - C - D - E
                # CDO accessible, ABE inaccessible
                # calculating dijkstra for A; then D and E not on the path to A and shouldn't be penalised for distance
                # essentially allows neighbours to be "cutoff points" to prevent further rolling down the hill
                neighbor_values = [heatmap.nodes[neighbor]["value"] for neighbor in heatmap.neighbors(node_id)
                                   if heatmap.nodes[neighbor]["cls_name"] == NodeType.INACCESSIBLE] # see above for why

                lowest_neighbor_value = min(neighbor_values) if len(neighbor_values) > 0 else Optimiser.TIER_VALUE # if node is not connected to rest of graph
                if data["value"] > lowest_neighbor_value + 1:
                    nx.set_node_attributes(heatmap, GraphNode.from_dict(data, value=lowest_neighbor_value + 1).get_dict())
                    edited = True

        return heatmap

    def dijkstra_multiplier(self, src_node, tier, subtier):
        heatmap = copy.deepcopy(self.base_graph)

        # the lower this number, the higher the priority (will always be negative!)
        desired_value = -(Optimiser.TIER_VALUE * tier + subtier * Optimiser.SUBTIER_VALUE)
        base_data = self.base_graph.nodes[src_node]
        nx.set_node_attributes(heatmap, GraphNode.from_dict(base_data, value=desired_value).get_dict())

        # for this graph, if the node is already accessible, its value cannot be decreased or increased by neighbours
        if heatmap.nodes[src_node]["cls_name"] == NodeType.ACCESSIBLE:
            return heatmap

        for dst_node in self.shortest_paths[src_node].keys(): # for every path from source node
            if dst_node == src_node: # ignore trivial paths
                continue

            # path must be to relevant dst (dst must be accessible, with no other accessible nodes along the way)
            if heatmap.nodes[dst_node]["cls_name"] != NodeType.ACCESSIBLE:
                continue
            if len([1 for intermediate_node in self.shortest_paths[src_node][dst_node]
                   if heatmap.nodes[intermediate_node]["cls_name"] == NodeType.ACCESSIBLE]) != 1:
                continue

            for i, intermediate_node in enumerate(self.shortest_paths[src_node][dst_node]):
                print(intermediate_node)
                # dist = 0 => divide by 1, dist = 1 => divide by 2 etc.
                averaged_value = round(desired_value / (i + 1)) # averaged over number of nodes required to obtain

                if heatmap.nodes[intermediate_node]["value"] > averaged_value:
                    nx.set_node_attributes(heatmap, GraphNode.from_dict(heatmap.nodes[intermediate_node],
                                                                        value=averaged_value).get_dict())
                if heatmap.nodes[intermediate_node]["cls_name"] == NodeType.ACCESSIBLE:
                    break
        return heatmap

    @staticmethod
    def add_graphs(graphs):
        total = copy.deepcopy(graphs[0])
        for graph in graphs[1:]:
            for node_id, data in graph.nodes.items():
                total_data = total.nodes[node_id]
                nx.set_node_attributes(total, GraphNode.from_dict(total_data,
                                                                  value=total_data["value"] + data["value"]).get_dict())
        return total

    def select_best(self) -> GraphNode:
        min_id, min_val = [None], math.inf
        for node_id, data in self.dijkstra_graph.nodes.items():
            if data["cls_name"] == NodeType.ACCESSIBLE:
                if data["value"] < min_val:
                    min_id, min_val = [node_id], data["value"]
                elif data["value"] == min_val:
                    min_id.append(node_id)
        return GraphNode.from_dict(self.dijkstra_graph.nodes[random.choice(min_id)])

    def run(self, profile_id):
        config = Config()
        graphs = []
        for node_id, data in self.base_graph.nodes.items():
            if data["cls_name"] not in NodeType.MULTI_UNCLAIMED:
                continue
            tier, subtier = config.preference_by_id(data["name"], profile_id)
            if tier > 0 or (tier == 0 and subtier > 0): # desirable and unclaimed
                graphs.append(self.dijkstra_multiplier(node_id, tier, subtier))
            elif tier < 0 or (tier == 0 and subtier < 0): # undesirable and unclaimed
                heatmap = copy.deepcopy(self.base_graph)
                cost = heatmap.nodes[node_id]["value"] - \
                       (Optimiser.TIER_VALUE * tier + subtier * Optimiser.SUBTIER_VALUE)
                nx.set_node_attributes(heatmap, GraphNode.from_dict(heatmap.nodes[node_id], value=cost).get_dict())
                graphs.append(heatmap)

        if len(graphs) == 0:
            graphs = [self.base_graph]

        self.dijkstra_graph = self.add_graphs(graphs)