import json
from pprint import pprint

from resolution import Resolution


class Config:
    def __init__(self):
        # TODO if config file does not exist
        with open("config.json") as f:
            self.config = dict(json.load(f))

        keys = [
            "resolution",
            "capture",
            "path",
            "character",
            "active_profile",
            "profiles",
        ]

        # ensure all parameters are legal
        if not all([k in keys for k in self.config.keys()]):
            pass # TODO add to config as default config


    def resolution(self):
        return Resolution(self.config["resolution"]["width"],
                          self.config["resolution"]["height"],
                          self.config["resolution"]["ui_scale"])

    def top_left(self):
        return self.config["capture"]["top_left_x"], self.config["capture"]["top_left_y"]

    def width(self):
        return self.config["capture"]["width"]

    def height(self):
        return self.config["capture"]["height"]

    def path(self):
        return self.config["path"]

    def character(self):
        return self.config["character"]

    def __profiles(self):
        return self.config["profiles"]

    def active_profile(self):
        for profile in self.__profiles():
            if profile["id"] == self.config["active_profile"]:
                return profile

    def preference(self, unlockable):
        p = self.active_profile().get(unlockable, {})
        return p.get("tier", 0), p.get("subtier", 0)