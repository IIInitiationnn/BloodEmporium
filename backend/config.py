import json

import os
from shutil import copyfile

from exceptions import ConfigError
from resolution import Resolution


class Config:
    def __init__(self):
        if not os.path.isfile("config.json"):
            copyfile("assets/default_config.json", "config.json")

        with open("config.json") as f:
            self.config = dict(json.load(f))

        # ensure all parameters are legal
        if "resolution" not in self.config.keys():
            raise ConfigError("Missing resolution in config.json")
        if "width" not in self.config["resolution"].keys():
            raise ConfigError("Missing resolution width in config.json")
        if "height" not in self.config["resolution"].keys():
            raise ConfigError("Missing resolution height in config.json")
        if "ui_scale" not in self.config["resolution"].keys():
            raise ConfigError("Missing resolution UI scale in config.json")

        if "path" not in self.config.keys():
            raise ConfigError("Missing path in config.json")

        if "character" not in self.config.keys():
            raise ConfigError("Missing character in config.json")

        if "active_profile" not in self.config.keys():
            raise ConfigError("Missing active profile in config.json")

        if "profiles" not in self.config.keys():
            raise ConfigError("Missing profiles in config.json")

        ids = []
        for num, profile in enumerate(self.config["profiles"], 1):
            if "id" not in profile.keys():
                raise ConfigError(f"Missing profile id for profile {num} in config.json")
            if profile["id"] in ids:
                raise ConfigError(f"Multiple profiles with same id (profile {num}) in config.json")

            ids.append(profile["id"])
            for unique_id, v in profile.items():
                # TODO validate that unique_id is a valid unlockable id
                if unique_id != "id":
                    if "tier" not in v:
                        raise ConfigError(f"Missing tier for unlockable {unique_id} under profile {profile['id']} in config.json")
                    if "subtier" not in v:
                        raise ConfigError(f"Missing subtier for unlockable {unique_id} under profile {profile['id']} in config.json")

    def resolution(self):
        return Resolution(self.config["resolution"]["width"],
                          self.config["resolution"]["height"],
                          self.config["resolution"]["ui_scale"])

    def top_left(self):
        return self.config["capture"]["top_left_x"], self.config["capture"]["top_left_y"]

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

    def get_profile_by_id(self, profile_id):
        return [profile for profile in self.__profiles() if profile["id"] == profile_id].pop(0)

    def active_profile_name(self):
        return self.active_profile()["id"]

    def preference(self, unlockable_id, profile_id=None):
        if profile_id is None:
            p = self.active_profile().get(unlockable_id, {})
        else:
            p = self.get_profile_by_id(profile_id).get(unlockable_id, {})
        return p.get("tier", 0), p.get("subtier", 0)

    def profile_names(self):
        return [profile["id"] for profile in self.__profiles()]

    def commit_changes(self):
        with open("config.json", "w") as output:
            json.dump(self.config, output, indent=4)

    def set_resolution(self, width, height, ui_scale):
        self.config["resolution"]["width"] = width
        self.config["resolution"]["height"] = height
        self.config["resolution"]["ui_scale"] = ui_scale
        self.commit_changes()

    def set_path(self, path):
        self.config["path"] = path
        self.commit_changes()

    def set_active_profile(self, active_profile):
        self.config["active_profile"] = active_profile
        self.commit_changes()

    def set_profile(self, updated_profile):
        self.config["profiles"][self.config["profiles"].index(self.get_profile_by_id(updated_profile["id"]))] = updated_profile
        self.commit_changes()

    def add_profile(self, new_profile):
        existing_profile = None
        for profile in self.__profiles():
            if profile["id"] == new_profile["id"]:
                existing_profile = profile

        if existing_profile is None:
            self.config["profiles"].append(new_profile)
        else:
            self.set_profile(new_profile)

        self.commit_changes()

    def set_character(self, character):
        self.config["character"] = character
        self.commit_changes()