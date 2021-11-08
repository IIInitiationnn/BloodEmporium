import networkx as nx
from pyvis.network import Network
from pyvis.options import Layout

from node import Node
from optimiser import Optimiser

''' timeline
    - backend with algorithm
    - openCV icon recognition
    - values from config file
        - can have multiple sets of values and can switch
    - frontend with GUI
'''

def main():
    all_unlockables = [("battery", False),
                       ("annotated_blueprint", False),
                       ("deja_vu", False),
                       ("sacrificial_cake", False),
                       ("butterfly_tape", True),
                       ("rubber_grip", True),
                       ("odd_stamp", False),
                       ("cutting_wire", True),
                       ("first_aid_kit", True),
                       ("vigos_jar_of_salty_lips", False),
                       ("bog_laurel_sachet", False)]
    edges = [("annotated_blueprint", "battery"),
             ("annotated_blueprint", "deja_vu"),
             ("annotated_blueprint", "sacrificial_cake"),
             ("annotated_blueprint", "butterfly_tape"),
             ("deja_vu", "sacrificial_cake"),
             ("butterfly_tape", "sacrificial_cake"),
             ("ORIGIN", "butterfly_tape"),
             ("ORIGIN", "first_aid_kit"),
             ("ORIGIN", "cutting_wire"),
             ("ORIGIN", "rubber_grip"),
             ("odd_stamp", "cutting_wire"),
             ("first_aid_kit", "vigos_jar_of_salty_lips"),
             ("vigos_jar_of_salty_lips", "bog_laurel_sachet")]

    i = 1
    graph = nx.Graph()

    graph.add_nodes_from([Node("ORIGIN000", "ORIGIN", 9999, True, True, False).get_tuple()])
    graph.add_nodes_from([Node(f"{name}000", name, 9999, is_accessible, False, False).get_tuple() for name, is_accessible in all_unlockables])
    graph.add_edges_from([(edge[0] + "000", edge[1] + "000") for edge in edges])

    layout = Layout()
    net = Network(notebook=True, layout=layout)
    net.from_nx(graph)
    net.show("graph.html")

    while i < 12:
        optimiser = Optimiser(graph)
        sum_graphs, selected = optimiser.run()
        selected.set_user_claimed(True)
        print(selected.name, selected.value, selected.is_user_claimed, selected.is_entity_claimed)

        # temporary until openCV
        nx.set_node_attributes(graph, selected.set_value(9999).get_dict())
        for neighbor in graph.neighbors(selected.get_id()):
            data = graph.nodes[neighbor]
            if not data['is_accessible']:
                nx.set_node_attributes(graph, Node.from_dict(data, is_accessible=True).get_dict())

        network = Network(notebook=True, layout=layout)
        network.from_nx(sum_graphs)
        network.show(f"run{i}.html")
        i += 1

if __name__ == '__main__':
    main()
