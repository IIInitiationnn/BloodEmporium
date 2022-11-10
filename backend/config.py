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
            self.copy_from_default("resolution")
        if any([prop not in self.config["resolution"].keys() for prop in ["width", "height", "ui_scale"]]):
            self.copy_from_default("resolution")

        if "path" not in self.config.keys():
            self.copy_from_default("path")

        if "hotkey" not in self.config.keys():
            self.copy_from_default("hotkey")

        if "profiles" not in self.config.keys():
            self.copy_from_default("profiles")

        # TODO set the value instead of raising error
        ids = []
        for num, profile in enumerate(self.config["profiles"], 1):
            if "id" not in profile.keys():
                raise ConfigError(f"Missing profile id for profile {num} in config.json")
            if profile["id"] in ids:
                raise ConfigError(f"Multiple profiles with same id (profile {num}) in config.json")
            if profile["id"] == "blank":
                raise ConfigError(f"blank is an invalid profile id for profile {num} in config.json")

            ids.append(profile["id"])
            for unique_id, v in profile.items():
                # TODO validate that unique_id is a valid unlockable id
                if unique_id != "id":
                    if "tier" not in v:
                        raise ConfigError(f"Missing tier for unlockable {unique_id} under profile {profile['id']}"
                                          f"in config.json")
                    if "subtier" not in v:
                        raise ConfigError(f"Missing subtier for unlockable {unique_id} under profile {profile['id']}"
                                          f"in config.json")

    def copy_from_default(self, prop):
        with open("assets/default_config.json") as f:
            default_config = dict(json.load(f))
        self.config[prop] = default_config[prop]
        self.commit_changes()

    def resolution(self):
        return Resolution(self.config["resolution"]["width"],
                          self.config["resolution"]["height"],
                          self.config["resolution"]["ui_scale"])

    def top_left(self):
        return self.config["capture"]["top_left_x"], self.config["capture"]["top_left_y"]

    def path(self):
        return self.config["path"]

    def hotkey(self):
        return self.config["hotkey"].split(" ")

    def __profiles(self):
        return self.config["profiles"]

    def get_profile_by_id(self, profile_id):
        return [profile for profile in self.__profiles() if profile["id"] == profile_id].pop(0)

    def preference(self, unlockable_id, profile_id):
        if profile_id == "blank":
            return 0, 0
        p = self.get_profile_by_id(profile_id).get(unlockable_id, {})
        return p.get("tier", 0), p.get("subtier", 0)

    def profile_names(self):
        return [profile["id"] for profile in self.__profiles()]

    def commit_changes(self):
        with open("config.json", "w") as output:
            json.dump({
                "resolution": self.config["resolution"],
                "path": self.config["path"],
                "hotkey": self.config["hotkey"],
                "profiles": self.config["profiles"],
            }, output, indent=4)

    def set_resolution(self, width, height, ui_scale):
        self.config["resolution"]["width"] = width
        self.config["resolution"]["height"] = height
        self.config["resolution"]["ui_scale"] = ui_scale
        self.commit_changes()

    def set_path(self, path):
        self.config["path"] = path
        self.commit_changes()

    def set_hotkey(self, hotkey):
        self.config["hotkey"] = " ".join(hotkey)
        self.commit_changes()

    def set_profile(self, updated_profile):
        self.config["profiles"][self.config["profiles"].index(self.get_profile_by_id(updated_profile["id"]))] = updated_profile
        self.commit_changes()

    def add_profile(self, new_profile):
        """
        :return: whether the profile existed before already
        """

        existing_profile = None
        for profile in self.__profiles():
            if profile["id"] == new_profile["id"]:
                existing_profile = profile

        if existing_profile is None:
            self.config["profiles"].append(new_profile)
        else:
            self.set_profile(new_profile)

        self.commit_changes()

        return existing_profile is not None

    def delete_profile(self, profile_id):
        to_be_removed = [profile for profile in self.__profiles() if profile["id"] == profile_id].pop(0)
        self.config["profiles"].remove(to_be_removed)
        self.commit_changes()