import copy
import math
from pprint import pprint

import networkx as nx

from node import Node

class Optimiser:
    def __init__(self, graph):
        self.base_graph = graph
        self.dijkstra_graph = None

    def dijkstra(self, desired_name):
        heatmap = copy.deepcopy(self.base_graph)
        '''TODO: for each priority higher (aka more desirable) set desired_value to be 20 lower thus negating distance
            ie it will go longer if it needs to to get something which is fiercely desired
            for each priority lower (aka less desirable) set desired_value to be 12 higher
            ie if there is a path to desirable through 1 undesirable vs a path to a desirable (lower prio than first) through neutral
            we will path through undesirable; however if theres multiple (2+) undesirable in the path OR something 2 degrees of undesirable then we will opt for neutral path first
            adjust numbers later as needed, refer to desirability.png
            
            amongst multiple of the same lowest, choose randomly? print if random and see if any situations where random fails
            
            in total probably 5 tiers of desirability: 4 normal, then 1 at negative infinite
            then neutral,
            then 3 tiers of undesirability: 2 normal, then 1 at infinite (never ever pick unless forced)'''
        desired_value = -1 if desired_name == "battery" else 0 # TODO for now, will read from config later: set to negative for desired, >9999 for non-desired (aka invert priority in config), 9999 for neutral
        base_data = self.base_graph.nodes[desired_name]
        nx.set_node_attributes(heatmap, Node.from_dict(base_data, value=desired_value).get_dict())

        if base_data["is_accessible"]:
            return heatmap

        edited = True
        while edited:
            edited = False
            for name, data in heatmap.nodes.items():
                if name == 'ORIGIN' or data['is_entity_claimed']:
                    continue
                lowest_neighbor_value = min([heatmap.nodes[neighbor]['value'] if not heatmap.nodes[neighbor]['is_entity_claimed']
                                             else 9999 for neighbor in heatmap.neighbors(name)])
                '''has_path = False # whether there is a simple path from ORIGIN to name to desired_name
                for path in nx.all_simple_paths(heatmap, "ORIGIN", desired_name):
                    if name in path:
                        has_path = True'''
                if data['value'] > lowest_neighbor_value + 1:
                    nx.set_node_attributes(heatmap, Node.from_dict(data, value=lowest_neighbor_value + 1).get_dict())
                    edited = True
                # print(unlockable, min([heatmap.nodes[neighbor]['value'] for neighbor in heatmap.neighbors(unlockable)]))

        return heatmap

    @staticmethod
    def add_graphs(graphs):
        total = copy.deepcopy(graphs[0])
        for graph in graphs[1:]:
            for name, data in graph.nodes.items():
                total_data = total.nodes[name]
                nx.set_node_attributes(total, Node.from_dict(total_data, value=total_data['value'] + data['value']).get_dict())

        # reduce everything to 0
        # lowest = min([data['value'] for data in total.nodes.values()])
        # for name, data in total.nodes.items():
        #     nx.set_node_attributes(total, Node.from_dict(data, value=data['value'] - lowest).get_dict())
        return total

    def select_best(self):
        lowest_name = ""
        lowest = math.inf
        for name, data in self.dijkstra_graph.nodes.items():
            if data['is_accessible'] and not data['is_user_claimed'] and not data['is_entity_claimed'] and data['value'] < lowest:
                lowest_name = name
                lowest = data['value']

        return Node.from_dict(self.dijkstra_graph.nodes[lowest_name])

    def run(self):
        desired_unlockables = ["sacrificial_cake", "vigo's_jar_of_salty_lips", "battery", "odd_stamp"]
        undesired_unlockables = ["annotated_blueprint", "first_aid_kit"]

        graphs = []
        for name, data in self.base_graph.nodes.items():
            if data["is_user_claimed"]: # claimed
                graphs.append(self.base_graph)
            elif name in desired_unlockables: # desirable and unclaimed TODO in future use value assigned in config
                graphs.append(self.dijkstra(name))
            elif name in undesired_unlockables: # temp: undesirable and unclaimed
                heatmap = copy.deepcopy(self.base_graph)
                nx.set_node_attributes(heatmap, Node.from_dict(heatmap.nodes[name], value=heatmap.nodes[name]['value'] + 1).get_dict())
                graphs.append(heatmap)
            else: # temp: neutral and unclaimed
                graphs.append(self.base_graph)
        # TODO in the future, add desirability (lower weight (value)) to nodes which are in danger and are desirable
        self.dijkstra_graph = self.add_graphs(graphs)

        return self.dijkstra_graph, self.select_best()