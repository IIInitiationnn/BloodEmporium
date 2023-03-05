from pprint import pprint

from backend.shapes import Position
from utils.color_util import ColorUtil


class GraphNode:
    PRESTIGE = "prestige"
    ORIGIN = "origin"
    CLAIMED = "claimed"
    ACCESSIBLE = "accessible"
    INACCESSIBLE = "inaccessible"
    STOLEN = "stolen"
    VOID = "void"

    def __init__(self, node_id, name, value, position, cls_name):
        self.node_id = node_id # aka (circle_number bloodweb position thing)_(unique_id)
        self.name = name.replace(".png", "") # aka unique_id # TODO does this need to replace .png?
        self.value = value
        self.x1, self.y1, self.x2, self.y2 = position.xyxy()
        self.x, self.y = position.centre() # for networkx positioning
        self.cls_name = cls_name

    @staticmethod
    def from_dict(data, **kwargs):
        position = Position(int(data["x1"]), int(data["y1"]), int(data["x2"]), int(data["y2"]))
        node = GraphNode(data["node_id"], data["name"], data["value"], position, data["cls_name"])
        for attribute, val in kwargs.items():
            node.__setattr__(attribute, val)
        return node

    @staticmethod
    def state_from_color(color):
        """
        :return: (is_accessible, is_user_claimed)
        """
        if color == "taupe":
            return True, False
        elif color == "red":
            return True, True
        else: # neutral
            return False, False

    def print(self):
        pprint(self.__dict__)

    def get_id(self):
        return self.node_id

    def set_value(self, value):
        self.value = value
        return self

    def set_claimed(self, is_claimed):
        if is_claimed:
            self.cls_name = "claimed"

    def get_tuple(self):
        data = {
            "node_id": self.node_id,
            "name": self.name,
            "value": self.value,
            "x1": str(self.x1),
            "y1": str(self.y1),
            "x2": str(self.x2),
            "y2": str(self.y2),
            "x": str(self.x),
            "y": str(self.y),
            "cls_name": self.cls_name,

            # pyvis attributes
            "title": f"{self.value}, " + ("claimed" if self.cls_name == GraphNode.CLAIMED else "not claimed"),
            "color": ColorUtil.red_hex if self.cls_name == GraphNode.CLAIMED else
                     ColorUtil.taupe_hex if self.cls_name == GraphNode.ACCESSIBLE else ColorUtil.neutral_hex,
            "physics": False
        }
        return self.node_id, data

    def get_dict(self):
        t = self.get_tuple()
        return {t[0]: t[1]}
