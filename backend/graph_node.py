from pprint import pprint
from typing import Dict, Any

from backend.shapes import Box
from util.node_util import ColorUtil, NodeType


class GraphNode:
    def __init__(self, node_id, name, value, box: Box, cls_name):
        self.node_id = node_id # number on graph 1, 2, ...
        self.name = name.replace(".png", "") # aka unique_id
        self.value = value
        self.x1, self.y1, self.x2, self.y2 = box.xyxy()
        self.cls_name = cls_name

        self.x, self.y = box.centre().xy() # for networkx positioning

    @staticmethod
    def from_dict(data: Dict[str, Any], **kwargs):
        box = Box(int(data["x1"]), int(data["y1"]), int(data["x2"]), int(data["y2"]))
        node = GraphNode(data["node_id"], data["name"], data["value"], box, data["cls_name"])
        for attribute, val in kwargs.items():
            node.__setattr__(attribute, val)
        return node

    def print(self):
        pprint(self.__dict__)

    def get_id(self):
        return self.node_id

    def set_value(self, value):
        self.value = value
        return self

    def set_claimed(self, is_claimed):
        if is_claimed:
            self.cls_name = NodeType.CLAIMED

    def get_tuple(self):
        data = {
            "node_id": self.node_id,
            "name": self.name,
            "value": self.value, # also pyvis
            "x1": str(self.x1),
            "y1": str(self.y1),
            "x2": str(self.x2),
            "y2": str(self.y2),
            "x": str(self.x),
            "y": str(self.y),
            "cls_name": self.cls_name,

            # pyvis attributes https://visjs.github.io/vis-network/docs/network/nodes.html
            "label": ((self.name + "\n") if self.name else "") + f"{self.value} ({self.cls_name})",
            # "font": {
            #     "color": ColorUtil.hex_from_cls_name(self.cls_name),
            #     "size": 11,
            # },
            "color": ColorUtil.hex_from_cls_name(self.cls_name),
            "physics": False
        }
        return self.node_id, data

    def get_dict(self):
        t = self.get_tuple()
        return {t[0]: t[1]}
