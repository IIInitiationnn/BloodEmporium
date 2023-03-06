from typing import List

import networkx as nx

from graph_node import GraphNode
from shapes import LinkedEdge, MatchedNode, UnmatchedNode


class Grapher:
    def __init__(self, nodes: List[MatchedNode], edges: List[LinkedEdge]):
        self.nodes = nodes
        self.edges = edges

    def create(self):
        nodes = []
        ids = {} # map str(node) [unhashable] to node_id [GraphNode.node_id]

        i = 1
        for node in self.nodes:
            ids[str(node)] = i
            nodes.append(GraphNode(i, node.unique_id, 9999, node.box, node.cls_name).get_tuple())
            i += 1

        edges = []
        for edge in self.edges:
            edges.append((ids[str(edge.node_a)], ids[str(edge.node_b)]))

        # construct networkx graph
        graph = nx.Graph()
        graph.add_nodes_from(nodes)
        graph.add_edges_from(edges)
        return graph

    @staticmethod
    def update(base_bloodweb, updated_nodes: List[UnmatchedNode]):
        for updated_node in updated_nodes:
            for node_id, data in base_bloodweb.nodes.items():
                if updated_node.box.close_to_xy(int(data["x"]), int(data["y"])):
                    x1, y1, x2, y2 = updated_node.xyxy()
                    nx.set_node_attributes(base_bloodweb, GraphNode.from_dict(data, cls_name=updated_node.cls_name,
                                                                              x1=x1, y1=y1, x2=x2, y2=y2).get_dict())
                else: # TODO previously undetected, match and add?
                    pass