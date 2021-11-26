import json

class Config:
    def __init__(self):
        with open("config.json") as f:
            self.config = json.load(f)