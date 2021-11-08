from pprint import pprint

class Node:
    def __init__(self, node_id, name, value, is_accessible, is_user_claimed, is_entity_claimed):
        self.node_id = node_id
        self.name = name
        self.value = value
        self.is_accessible = is_accessible
        self.is_user_claimed = is_user_claimed
        self.is_entity_claimed = is_entity_claimed

    @classmethod
    def from_dict(cls, data, **kwargs):
        node = cls(data['node_id'], data['name'], data['value'], data['is_accessible'], data['is_user_claimed'], data['is_entity_claimed'])
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

    def set_user_claimed(self, is_claimed):
        self.is_user_claimed = is_claimed

    def get_tuple(self):
        data = {
            "title": f"{self.value}, " + ("user claimed" if self.is_user_claimed else "entity claimed" if self.is_entity_claimed else "not claimed"), # pyvis attribute
            "color": "red" if self.is_user_claimed else "yellow" if self.is_accessible else "gray" if not self.is_entity_claimed else "black", # pyvis attribute
            "node_id": self.node_id,
            "name": self.name,
            "value": self.value,
            "is_accessible": self.is_accessible,
            "is_user_claimed": self.is_user_claimed,
            "is_entity_claimed": self.is_entity_claimed
        }
        return self.node_id, data

    def get_dict(self):
        t = self.get_tuple()
        return {t[0]: t[1]}
