import networkx as nx

from node import Node


class Grapher:
    def __init__(self, debugger, circles, connections):
        self.debugger = debugger
        self.circles = circles
        self.connections = connections

    def create(self):
        nodes = []
        ids = {}

        i = 1
        for circle in self.circles:
            if circle.name == "ORIGIN":
                ids[circle] = "ORIGIN"
                nodes.append(Node("ORIGIN", circle.name, 9999, circle.xy(), True, True).get_tuple())
                continue

            node_id = f"{i}_{circle.name}"
            ids[circle] = node_id
            is_accessible, is_user_claimed = Node.state_from_color(circle.color)
            nodes.append(Node(node_id, circle.name, 9999, circle.xy(), is_accessible, is_user_claimed).get_tuple())
            i += 1

        # actual edges joining circles
        edges = []
        for connection in self.connections:
            edges.append((ids[connection.circle1], ids[connection.circle2]))

        # construct networkx graph
        graph = nx.Graph()
        graph.add_nodes_from(nodes)
        graph.add_edges_from(edges)
        return graph