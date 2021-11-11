from pyvis.network import Network
from pyvis.options import Layout

class NetworkUtil:
    @staticmethod
    def write_to_html(graph, file_name, improved_layout=False):
        if improved_layout:
            net = Network(notebook=True, bgcolor="#505152", height=1080, width=1920, font_color="#ffffff", layout=Layout())
        else:
            net = Network(notebook=True, bgcolor="#505152", height=1080, width=1920, font_color="#ffffff")
        net.from_nx(graph)
        net.show(f"{file_name}.html")