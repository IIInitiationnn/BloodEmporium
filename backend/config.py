import json
import os
from shutil import copyfile

from exceptions import ConfigError


class Config:
    def __init__(self):
        if not os.path.isfile("config.json"):
            copyfile("assets/default_config.json", "config.json")

        with open("config.json") as f:
            self.config = dict(json.load(f))

        self.commit_changes() # ensure all necessary keys are in (essentially copying missing values)

        # TODO set the value instead of raising error (use get_next_free_profile_name)
        ids = []
        for num, profile in enumerate(self.config["profiles"], 1):
            if "id" not in profile.keys():
                raise ConfigError(f"Missing profile id for profile {num} in config.json")
            if profile["id"] in ids:
                raise ConfigError(f"Multiple profiles with same id (profile {num}) in config.json")
            if "notes" not in profile.keys():
                profile["notes"] = ""

            ids.append(profile["id"])
            invalid_unlockables = []
            for unique_id, v in profile.items():
                # TODO validate that unique_id is a valid unlockable id
                if unique_id not in ["id", "notes"]:
                    if "tier" not in v:
                        invalid_unlockables.append(unique_id)
                        continue
                    if "subtier" not in v:
                        invalid_unlockables.append(unique_id)
                        continue
            [profile.pop(invalid_unlockable) for invalid_unlockable in invalid_unlockables]

    def top_left(self):
        return self.config["capture"]["top_left_x"], self.config["capture"]["top_left_y"]

    def path(self):
        return self.config["path"]

    def hotkey(self):
        return self.config["hotkey"].split(" ")

    def primary_mouse(self):
        return self.config["primary_mouse"]

    def __profiles(self):
        return self.config["profiles"]

    def get_profile_by_id(self, profile_id):
        if profile_id is None:
            return {"id": None, "notes": ""}
        profiles = self.__profiles()
        return [p for p in profiles if p["id"] == profile_id].pop(0) if len(profiles) > 0 else {"id": None, "notes": ""}

    def notes_by_id(self, profile_id):
        if profile_id is None:
            return ""
        return self.get_profile_by_id(profile_id).get("notes", "")

    def preference_by_id(self, unlockable_id, profile_id):
        if profile_id is None:
            return 0, 0
        return self.preference_by_profile(unlockable_id, self.get_profile_by_id(profile_id))

    def preference_by_profile(self, unlockable_id, profile):
        p = profile.get(unlockable_id, {})
        return p.get("tier", 0), p.get("subtier", 0)

    def profile_names(self):
        return [profile["id"] for profile in self.__profiles()]

    def commit_changes(self):
        with open("assets/default_config.json") as default:
            default_config = dict(json.load(default))
            with open("config.json", "w") as output:
                json.dump({
                    "path": self.config.get("path", default_config["path"]),
                    "hotkey": self.config.get("hotkey", default_config["hotkey"]),
                    "primary_mouse": self.config.get("primary_mouse", default_config["primary_mouse"]),
                    "profiles": self.config.get("profiles", default_config["profiles"]),
                }, output, indent=4) # to preserve order

    def set_path(self, path):
        self.config["path"] = path
        self.commit_changes()

    def set_hotkey(self, hotkey):
        self.config["hotkey"] = " ".join(hotkey)
        self.commit_changes()

    def set_primary_mouse(self, primary_mouse):
        self.config["primary_mouse"] = primary_mouse
        self.commit_changes()

    def set_profile(self, updated_profile):
        if updated_profile["id"] is None:
            return
        self.config["profiles"][self.config["profiles"].index(self.get_profile_by_id(updated_profile["id"]))] = updated_profile
        self.commit_changes()

    def is_profile(self, profile_id):
        """
        :return: whether the profile existed before already
        """
        return profile_id in [profile["id"] for profile in self.__profiles()]

    def get_next_free_profile_name(self):
        profile_ids = [profile["id"] for profile in self.__profiles()]
        i = 0
        profile_id = "new profile"
        while profile_id in profile_ids:
            i += 1
            profile_id = f"new profile ({i})"
        return profile_id

    def add_profile(self, new_profile, index=None):
        """
        :return: whether the profile existed before already
        """

        existing_profile = None
        for profile in self.__profiles():
            if profile["id"] == new_profile["id"]:
                existing_profile = profile

        if "notes" not in new_profile.keys():
            new_profile["notes"] = ""

        if existing_profile is None:
            if index is None:
                self.config["profiles"].append(new_profile)
            else:
                self.config["profiles"].insert(index, new_profile)
        else:
            self.set_profile(new_profile)

        self.commit_changes()

        return existing_profile is not None

    def delete_profile(self, profile_id):
        to_be_removed = [profile for profile in self.__profiles() if profile["id"] == profile_id].pop(0)
        self.config["profiles"].remove(to_be_removed)
        self.commit_changes()

    def export_profile(self, profile_id):
        if profile_id is None:
            return
        profile = self.get_profile_by_id(profile_id)
        with open(f"{profile_id}.emp", "w") as file:
            file.write(json.dumps(profile))