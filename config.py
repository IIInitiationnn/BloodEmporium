import json

from resolution import Resolution


class Config:
    def __init__(self):
        with open("config.json") as f:
            self.config = json.load(f)

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