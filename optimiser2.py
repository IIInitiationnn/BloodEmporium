import copy
import math

import networkx as nx

from node import Node


class Optimiser2:
    def __init__(self, graph):
        self.base_graph = graph
        self.pareto_optimal_paths()

    def pareto_optimal_paths(self):
        self.pareto_graph = copy.deepcopy(self.base_graph)

        unvisited = set()
        self.dist = {}
        self.prev = {}

        for node_id, data in self.pareto_graph.nodes.items():
            if data["is_user_claimed"]:
                self.dist[node_id] = (0, 0)
                self.prev[node_id] = None
                unvisited.add(node_id)
            else:
                self.dist[node_id] = (math.inf, math.inf)
                self.prev[node_id] = None
                unvisited.add(node_id)
        self.dist["ORIGIN000"] = (0, 0) # TODO change back to ORIGIN after main test is done

        while len(unvisited) != 0:
            min_vertex, min_dist = None, (math.inf, math.inf)
            for u in unvisited:
                if Optimiser2.weighted_dist(self.dist[u]) <= Optimiser2.weighted_dist(min_dist):
                    min_vertex, min_dist = u, self.dist[u]

            unvisited.remove(min_vertex)
            for neighbour in self.pareto_graph.neighbors(min_vertex):
                if neighbour in unvisited:
                    new_dist = tuple(map(sum, zip(min_dist, self.pareto_graph.nodes[neighbour]["value"])))
                    if Optimiser2.weighted_dist(new_dist) < Optimiser2.weighted_dist(self.dist[neighbour]):
                        self.dist[neighbour] = new_dist
                        self.prev[neighbour] = min_vertex

        for node_id, data in self.pareto_graph.nodes.items():
            nx.set_node_attributes(self.pareto_graph, Node.from_dict(data, value=self.dist[node_id]).get_dict())

    @staticmethod
    def weighted_dist(dist_vector):
        ratio = 4 # how much more important reward value should be than ratio
        return dist_vector[0] + ratio * dist_vector[1]

    def select_best(self):
        min_vertex, min_dist = None, (math.inf, math.inf)
        for node_id, data in self.pareto_graph.nodes.items():
            if Optimiser2.weighted_dist(data["value"]) < Optimiser2.weighted_dist(min_dist) and not self.pareto_graph.nodes[node_id]["is_user_claimed"]:
                min_vertex, min_dist = node_id, data["value"]

        path = [min_vertex]
        v = min_vertex
        while not self.pareto_graph.nodes[v]["is_accessible"]:
            prev = self.prev[v]
            path.append(prev)
            v = prev

        for v in path:
            data = self.pareto_graph.nodes[v]
            if data['is_accessible'] and not data['is_user_claimed']:
                return Node.from_dict(data)

