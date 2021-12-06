import copy
import math
import random

import networkx as nx

from node import Node


class Optimiser:
    def __init__(self, graph):
        self.base_graph = graph
        self.dijkstra_graph = None

    def dijkstra(self, desired_node_id):
        heatmap = copy.deepcopy(self.base_graph)
        """TODO: for each priority higher (aka more desirable) set desired_value to be 20 lower thus negating distance
            ie it will go longer if it needs to to get something which is fiercely desired
            for each priority lower (aka less desirable) set desired_value to be 12 higher
            ie if there is a path to desirable through 1 undesirable vs a path to a desirable (lower prio than first) through neutral
            we will path through undesirable; however if theres multiple (2+) undesirable in the path OR something 2 degrees of undesirable then we will opt for neutral path first
            adjust numbers later as needed, refer to desirability.png
            
            amongst multiple of the same lowest, choose randomly? print if random and see if any situations where random fails
            
            in total probably 5 tiers of desirability: 4 normal, then 1 at negative infinite
            then neutral,
            then 3 tiers of undesirability: 2 normal, then 1 at infinite (never ever pick unless forced)"""
        desired_value = -20 # TODO for now, will read from config later: set to negative for desired, >9999 for non-desired (aka invert priority in config), 9999 for neutral
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

                # TODO if this node is undesirable, add 12? refer to run3.html on the left side
                lowest_neighbor_value = min([heatmap.nodes[neighbor]["value"] for neighbor in heatmap.neighbors(node_id)])
                """has_path = False # whether there is a simple path from ORIGIN to name to desired_name
                for path in nx.all_simple_paths(heatmap, "ORIGIN", desired_name):
                    if name in path:
                        has_path = True"""
                if data["value"] > lowest_neighbor_value + 1:
                    nx.set_node_attributes(heatmap, Node.from_dict(data, value=lowest_neighbor_value + 1).get_dict())
                    edited = True
                # print(unlockable, min([heatmap.nodes[neighbor]["value"] for neighbor in heatmap.neighbors(unlockable)]))

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

    def num_left(self):
        total = 0
        for node_id, data in self.dijkstra_graph.nodes.items():
            if not data["is_user_claimed"]:
                total += 1
        return total

    def run(self):
        desired_unlockables = ["iconAddon_heavyPanting.png",
                               "iconAddon_darkCincture.png",
                               "iconAddon_ataxicRespiration.png",
                               "iconAddon_badMansLastBreath.png",
                               "iconAddon_fragileWheeze.png",
                               "iconAddon_kavanaghsLastBreath.png",
                               "iconFavors_hollowShell.png",
                               "iconFavors_survivorPudding.png",
                               "iconFavors_bloodyPartyStreamers.png",
                               "iconFavors_wardBlack.png",
                               "iconAddon_bandages.png",
                               "iconAddon_battery.png",
                               "iconAddon_brokenFlashlightBulb.png",
                               "iconAddon_gelDressings.png",
                               "iconAddon_heavyDutyBattery.png",
                               "iconAddon_longLifeBattery.png",
                               "iconAddon_metalSaw.png",
                               "iconAddon_scraps",
                               "iconFavors_escapeCake.png",
                               "iconItems_firstAidKit.png",
                               "iconItems_flashlight.png",
                               "iconItems_flashlightSport.png",
                               "iconItems_flashlightUtility.png",
                               "iconItems_toolboxAlexs.png",
                               "iconItems_toolboxWornOut.png",
                               "iconItems_toolbox.png",
                               "iconItems_rangersAidKit.png",
                               "iconItems_rundownAidKit.png",
                               "iconFavors_wardWhite.png",
                               "iconFavors_petrifiedOak.png",

                               # "iconFavors_ardentRavenWreath.png",
                               # "iconFavors_ardentShrikeWreath.png",
                               # "iconFavors_ardentSpottedOwlWreath.png",
                               # "iconFavors_ardentTanagerWreath.png",
                               ]
        undesired_unlockables = ["annotated_blueprint", "first_aid_kit"]

        graphs = []
        for node_id, data in self.base_graph.nodes.items():
            if data["is_user_claimed"]: # claimed
                pass
            elif data["name"] in desired_unlockables: # desirable and unclaimed TODO in future use value assigned in config
                graphs.append(self.dijkstra(node_id))
            elif data["name"] in undesired_unlockables: # temp: undesirable and unclaimed
                heatmap = copy.deepcopy(self.base_graph)
                nx.set_node_attributes(heatmap, Node.from_dict(heatmap.nodes[node_id], value=heatmap.nodes[node_id]["value"] + 12).get_dict())
                graphs.append(heatmap)

        if len(graphs) == 0:
            graphs = [self.base_graph]

        # TODO in the future, add desirability (lower weight (value)) to nodes which are in danger and are desirable
        self.dijkstra_graph = self.add_graphs(graphs)