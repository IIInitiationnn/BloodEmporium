import os
from typing import List

import cv2

from backend.image import CVImage
from backend.mergedbase import MergedBase
from backend.shapes import MatchedNode, LinkedEdge
from backend.util.node_util import ColorUtil
from util.network_util import NetworkUtil


# direct = in this function, indirect = stored to be used by another function
class Debugger:
    def __init__(self, timestamp, write_to_output=False):
        self.write_to_output = write_to_output
        self.time = timestamp.strftime("%d-%m-%y %H-%M-%S")

        self.cv_images = []
        self.nodes: List[List[MatchedNode]] = []
        self.edges: List[List[LinkedEdge]] = []

        if self.write_to_output:
            if not os.path.isdir(f"output"):
                os.mkdir(f"output")
            if not os.path.isdir(f"output/{self.time}"):
                os.mkdir(f"output/{self.time}")

    # merged base - direct output
    def set_merged_base(self, merged_base: MergedBase):
        self.merged_base = merged_base
        if self.write_to_output:
            cv2.imwrite(f"output/{self.time}/collage.png", merged_base.images)
        return self

    # image - direct output, indirect debug
    def set_image(self, bloodweb_iteration, cv_image: CVImage):
        while len(self.cv_images) < bloodweb_iteration + 1:
            self.cv_images.append(None)
            self.nodes.append([])
            self.edges.append([])
        self.cv_images[bloodweb_iteration] = cv_image
        if self.write_to_output:
            if not os.path.isdir(f"output/{self.time}/{bloodweb_iteration}"):
                os.mkdir(f"output/{self.time}/{bloodweb_iteration}")
            cv2.imwrite(f"output/{self.time}/{bloodweb_iteration}/initial.png", cv_image.get_bgr())

    # nodes - indirect output, indirect debug
    def set_nodes(self, bloodweb_iteration, nodes: List[MatchedNode]):
        # TODO in future show separate images for unprocessed (bbox nodes, oriented bbox edges) and
        #  processed (centre dot nodes, line edges)
        self.nodes[bloodweb_iteration] = nodes

    # edges - indirect output, indirect debug
    def set_edges(self, bloodweb_iteration, edges: List[LinkedEdge]):
        self.edges[bloodweb_iteration] = edges

    # grapher - direct output
    def set_base_bloodweb(self, bloodweb_iteration, base_bloodweb):
        if self.write_to_output:
            NetworkUtil.write_to_html(base_bloodweb, f"output/{self.time}/{bloodweb_iteration}/base_bloodweb")
        return self

    # updated image - direct output
    def add_updated_image(self, bloodweb_iteration, update_iteration, updated_image):
        if self.write_to_output:
            cv2.imwrite(f"output/{self.time}/{bloodweb_iteration}/updated_{update_iteration}.png",
                        updated_image.get_bgr())

    # optimiser - direct output (this is technically not dijkstra optimised when running naive mode)
    def set_dijkstra(self, bloodweb_iteration, update_iteration, dijkstra_graph):
        if self.write_to_output:
            NetworkUtil.write_to_html(dijkstra_graph,
                                      f"output/{self.time}/{bloodweb_iteration}/dijkstra_{update_iteration}")
        return self

    def construct_and_show_images(self, bloodweb_iteration):
        img = self.cv_images[bloodweb_iteration].get_bgr(True)
        for node in self.nodes[bloodweb_iteration]:
            cv2.rectangle(img, node.box.nw.xy(), node.box.se.xy(),
                          ColorUtil.bgr_from_cls_name(node.cls_name), 4)

            if node.unique_id != "":
                matched_icon = self.merged_base.valid_images[self.merged_base.names.index(node.unique_id)]
                resized_match = cv2.resize(matched_icon, tuple(reversed([c * 2 // 3 for c in matched_icon.shape])))
                centre_x, centre_y = node.box.centre().xy()
                node_width, node_height = node.box.dimensions()
                offset_x, offset_y = centre_x + node_width // 2, centre_y - node_height // 2
                img[offset_y:offset_y+resized_match.shape[0], offset_x:offset_x+resized_match.shape[1]] = \
                    cv2.merge([resized_match, resized_match, resized_match])
        for edge in self.edges[bloodweb_iteration]:
            cv2.line(img, edge.node_a.box.centre().xy(), edge.node_b.box.centre().xy(), (255, 255, 255), 1)

        if self.write_to_output:
            cv2.imwrite(f"output/{self.time}/{bloodweb_iteration}/processed.png", img)

        cv2.imshow("processed", img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()