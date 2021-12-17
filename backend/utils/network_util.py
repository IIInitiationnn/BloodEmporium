import networkx as nx
from pyvis.network import Network
from pyvis.options import Layout

from node import Node


class NetworkUtil:
    @staticmethod
    def write_to_html(graph, file_name, improved_layout=False, notebook=True):
        if improved_layout:
            net = Network(notebook=notebook, bgcolor="#5B9885", height=1440, width=2560, font_color="#ffffff", layout=Layout())
        else:
            net = Network(notebook=notebook, bgcolor="#5B9885", height=1440, width=2560, font_color="#ffffff")

        graph_copy = graph.copy()
        for node_id, data in graph_copy.nodes.items():
            nx.set_node_attributes(graph_copy, Node.from_dict(data, x=int(data["x"]) - 600, y=int(data["y"]) - 600).get_dict())
        net.from_nx(graph_copy)
        net.show(f"{file_name}.html")