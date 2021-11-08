from pprint import pprint


class Node:
    def __init__(self, name, value, is_accessible, is_user_claimed, is_entity_claimed):
        self.name = name
        self.value = value
        self.is_accessible = is_accessible
        self.is_user_claimed = is_user_claimed
        self.is_entity_claimed = is_entity_claimed

    @classmethod
    def from_dict(cls, data, **kwargs):
        node = cls(data['name'], data['value'], data['is_accessible'], data['is_user_claimed'], data['is_entity_claimed'])
        for attribute, val in kwargs.items():
            node.__setattr__(attribute, val)
        return node

    def print(self):
        pprint(self.__dict__)

    def get_name(self):
        return self.name

    def set_value(self, value):
        self.value = value
        return self

    def set_user_claimed(self, is_claimed):
        self.is_user_claimed = is_claimed

    def get_tuple(self):
        data = {
            "title": f"{self.value}, " + ("user claimed" if self.is_user_claimed else "entity claimed" if self.is_entity_claimed else "not claimed"), # pyvis attribute
            "color": "red" if self.is_user_claimed else "yellow" if self.is_accessible else "gray" if not self.is_entity_claimed else "black", # pyvis attribute
            "name": self.name,
            "value": self.value,
            "is_accessible": self.is_accessible,
            "is_user_claimed": self.is_user_claimed,
            "is_entity_claimed": self.is_entity_claimed
        }
        return self.name, data

    def get_dict(self):
        t = self.get_tuple()
        return {t[0]: t[1]}
