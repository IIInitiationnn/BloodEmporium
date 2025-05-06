from typing import List, Optional

import networkx as nx

from backend.util.node_util import NodeType
from graph_node import GraphNode
from shapes import LinkedEdge, MatchedNode, UnmatchedNode


class Grapher:
    def __init__(self, nodes: List[MatchedNode], edges: List[LinkedEdge]):
        self.nodes: List[MatchedNode] = nodes
        self.edges: List[LinkedEdge] = edges

    def create(self):
        nodes = []
        ids = {} # map str(node) [unhashable] to node_id [GraphNode.node_id]

        i = 1
        for node in self.nodes:
            ids[str(node)] = i
            nodes.append(GraphNode(i, node.unique_id, 0, node.box, node.cls_name).get_tuple())
            i += 1

        edges = []
        for edge in self.edges:
            edges.append((ids[str(edge.node_a)], ids[str(edge.node_b)]))

        # construct networkx graph
        graph = nx.Graph()
        graph.add_nodes_from(nodes)
        graph.add_edges_from(edges)
        return graph

    # updated_nodes does not contain bp node
    @staticmethod
    def update(base_bloodweb, updated_nodes: List[UnmatchedNode], previously_selected_node: GraphNode) -> bool:
        if len(updated_nodes) == 0:
            return True # no nodes

        if len(updated_nodes) == 1:
            if updated_nodes[0].cls_name in [NodeType.ORIGIN, NodeType.PRESTIGE]:
                return True # just origin or new prestige (former can happen between levels; latter shouldn't happen)

        num_mismatches = 0 # another potential error checking mechanism
        for updated_node in updated_nodes:
            if updated_node.cls_name == NodeType.VOID:
                # voids appear as new, so this error check will think it was previously undetected; must skip
                continue

            for node_id, data in base_bloodweb.nodes.items():
                if updated_node.box.close_to_xy(int(data["x"]), int(data["y"])):
                    if updated_node.cls_name in NodeType.MULTI_UNCLAIMED and data["name"] == "":
                        # error check: if node had no unlockable matched (e.g. claimed, stolen) but now seems unclaimed
                        continue

                    updated_cls_name = updated_node.cls_name
                    if updated_node.box.close_to_xy(previously_selected_node.x, previously_selected_node.y):
                        # error check: if this is the previous selection, it should be
                        # - claimed: if not, it was inaccessible (thought was accessible but wasn't), OR
                        # - stolen: appeared accessible (not enough delay after last selection)
                        if updated_node.cls_name not in [NodeType.CLAIMED, NodeType.STOLEN]:
                            updated_cls_name = NodeType.INACCESSIBLE

                    x1, y1, x2, y2 = updated_node.xyxy()
                    nx.set_node_attributes(base_bloodweb, GraphNode.from_dict(data, cls_name=updated_cls_name,
                                                                              x1=x1, y1=y1, x2=x2, y2=y2).get_dict())
                    break # no need to keep iterating
            else: # for else: didn't break means previously undetected TODO match and add?
                # print(updated_node.xyxy())
                num_mismatches += 1

        # print(f"{num_mismatches} mismatches")
        if num_mismatches > 1:
            return True # unlikely to be more than 1 mismatch

        # no accessible nodes
        return not any([data["cls_name"] in NodeType.MULTI_UNCLAIMED for data in base_bloodweb.nodes.values()])

    @staticmethod
    def update_guess(base_bloodweb, nodes: List[GraphNode]) -> None:
        neighbors = set()
        for node in nodes:
            node.set_claimed(True)
            nx.set_node_attributes(base_bloodweb, node.get_dict())

            for neighbor in base_bloodweb.neighbors(node.node_id):
                neighbors.add(base_bloodweb.nodes[neighbor]["node_id"])

        for neighbor_id in neighbors:
            if base_bloodweb.nodes[neighbor_id]["cls_name"] == NodeType.INACCESSIBLE:
                nx.set_node_attributes(base_bloodweb, GraphNode.from_dict(base_bloodweb.nodes[neighbor_id], cls_name=NodeType.ACCESSIBLE).get_dict())