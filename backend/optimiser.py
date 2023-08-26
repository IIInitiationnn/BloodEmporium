import copy
import math
import random
from collections import defaultdict
from statistics import mean
from typing import List

import networkx as nx

from backend.data import Data, Unlockable
from backend.util.node_util import NodeType
from backend.util.timer import Timer
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

            # path must be to relevant dst (dst must be accessible, path must be entirely in/accessible,
            # with no other accessible nodes along the way)
            if heatmap.nodes[dst_node]["cls_name"] != NodeType.ACCESSIBLE:
                continue
            path = self.shortest_paths[src_node][dst_node]
            if any([heatmap.nodes[intermediate_node]["cls_name"] not in NodeType.MULTI_UNCLAIMED
                    for intermediate_node in path]):
                continue
            if len([1 for intermediate_node in path
                   if heatmap.nodes[intermediate_node]["cls_name"] == NodeType.ACCESSIBLE]) != 1:
                continue

            for i, intermediate_node in enumerate(path):
                # dist = 0 => divide by 1; dist = 1 => divide by 2 etc.
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

    # prioritise inaccessible (select more than one node)
    def select_random_prioritise_inaccessible(self) -> GraphNode:
        inaccessible = [node_id for node_id, data in self.dijkstra_graph.nodes.items()
                        if data["cls_name"] == NodeType.INACCESSIBLE]
        accessible = [node_id for node_id, data in self.dijkstra_graph.nodes.items()
                      if data["cls_name"] == NodeType.ACCESSIBLE]
        if len(inaccessible) > 0:
            random_id = random.choice(inaccessible)
        else:
            random_id = random.choice(accessible)
        return GraphNode.from_dict(self.dijkstra_graph.nodes[random_id])

    def select_best_single(self) -> GraphNode:
        timer = Timer("select_best_single")
        min_node_ids, min_val = [None], math.inf
        for node_id, data in self.dijkstra_graph.nodes.items():
            if data["cls_name"] != NodeType.ACCESSIBLE:
                continue
            if data["value"] < min_val:
                min_node_ids, min_val = [node_id], data["value"]
            elif data["value"] == min_val:
                min_node_ids.append(node_id)
        timer.update()
        return GraphNode.from_dict(self.dijkstra_graph.nodes[random.choice(min_node_ids)])

    def select_best_multi(self, unlockables: List[Unlockable]) -> List[GraphNode]:
        timer = Timer("select_best_multi")
        # find all relevant path (multi-claim) selections
        paths, bp_vals, opt_vals = [], [], []
        for src_node_id, data in self.dijkstra_graph.nodes.items():
            if data["cls_name"] != NodeType.ACCESSIBLE:
                continue
            # for every path from accessible source node to a more external node on the same "branch"
            for dst_node_id in self.shortest_paths[src_node_id].keys():
                # path must be to relevant dst (entire path must be in/accessible; src should be only accessible node)
                path = self.shortest_paths[src_node_id][dst_node_id]
                if any([self.dijkstra_graph.nodes[intermediate_node]["cls_name"] not in NodeType.MULTI_UNCLAIMED
                        for intermediate_node in path]):
                    continue
                if len([1 for intermediate_node in path
                       if self.dijkstra_graph.nodes[intermediate_node]["cls_name"] == NodeType.ACCESSIBLE]) != 1:
                    continue

                # currently this is different from single behaviour; for path from a to c
                # this does (a + b/2 + c/3) + (b/2 + c/3) + (c/3) = a + b + c
                # but should do (a + b/2 + c/3) + (b + c/2) + (c) = a + 3b/2 + 11c/6 (what single does)
                # more weight should be given to further nodes because the value they provide propagates down the path
                path_opt_val = mean([self.dijkstra_graph.nodes[intermediate_node]["value"]
                                     for intermediate_node in path])
                path_unlockables = [[u for u in unlockables
                                    if u.unique_id == self.dijkstra_graph.nodes[intermediate_node]["name"]][0]
                                    for intermediate_node in path]
                path_bp_val = sum([Data.get_cost(u.rarity, u.type) for u in path_unlockables])
                paths.append(path)
                bp_vals.append(path_bp_val)
                opt_vals.append(path_opt_val)

        # if any paths have shared destination nodes, remove the path(s) with the most bloodpoint value from the list
        # and repeat until this condition is no longer violated
        # this can remove all paths (e.g. all have the same bp value, two have value X and two have value Y)
        run = True
        while run: # repeat until no more changes
            run = False
            duplicates = defaultdict(list) # dict {dst_node_id: [indices]}
            indices_to_remove = []
            for indices, path in enumerate(paths):
                duplicates[path[-1]].append(indices)
            for dst_node_id, indices in duplicates.items():
                if len(indices) > 1: # more than one path to this destination node
                    run = True
                    # TODO print paths for debugging

                    # remove path(s) with most bloodpoint value
                    max_bp_val = max([bp_vals[index] for index in indices])
                    for index in indices:
                        if bp_vals[index] == max_bp_val:
                            indices_to_remove.append(index)

            for index in sorted(indices_to_remove, reverse=True): # remove in reverse order so indices are preserved
                paths.pop(index)
                bp_vals.pop(index)
                opt_vals.pop(index)

        min_paths, min_val = [[]], math.inf
        for i, path in enumerate(paths):
            path_opt_val = opt_vals[i]
            if path_opt_val < min_val:
                min_paths, min_val = [path], path_opt_val
            elif path_opt_val == min_val:
                min_paths.append(path)
        timer.update()
        return [GraphNode.from_dict(self.dijkstra_graph.nodes[node]) for node in random.choice(min_paths)]

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

    def can_auto_purchase(self, profile_id, threshold_tier=None, threshold_subtier=None):
        # two ways to auto-purchase
        # A: all tiers and subtiers of all items are the same
        # B: all tiers and subtiers fall below threshold (if threshold is enabled)
        # check A, then B

        config = Config()
        tiers, subtiers = set(), set()
        for data in self.base_graph.nodes.values():
            if data["cls_name"] not in NodeType.MULTI_UNCLAIMED:
                continue
            tier, subtier = config.preference_by_id(data["name"], profile_id)
            tiers.add(tier)
            subtiers.add(subtier)

        # A
        if len(tiers) == 1 and len(subtiers) == 1:
            return True
        if threshold_tier is None:
            return False

        # B
        return max(tiers) < threshold_tier and max(subtiers) < threshold_subtier