import json
import os
from shutil import copyfile

from exceptions import ConfigError

migrations = [
    # 7.3.3 hawkins reinstatement
    ("iconPerks_situationalAwareness_survivor", "iconPerks_betterTogether_survivor"),
    ("iconPerks_survivalInstincts_survivor",    "iconPerks_innerStrength_survivor"),
    ("iconPerks_guardian_survivor",             "iconPerks_babySitter_survivor"),
    ("iconPerks_pushThroughIt_survivor",        "iconPerks_secondWind_survivor"),

    # 7.5.0 hillbilly changes
    ("iconAddon_junkyardAirFilter_hillbilly",   "iconAddon_greasedThrottle_hillbilly"),
    ("iconAddon_heavyClutch_hillbilly",         "iconAddon_counterweight_hillbilly"),
    ("iconAddon_speedLimiter_hillbilly",        "iconAddon_crackedPrimerBulb_hillbilly"),
    ("iconAddon_puncturedMuffler_hillbilly",    "iconAddon_thermalCasing_hillbilly"),
    ("iconAddon_deathEngravings_hillbilly",     "iconAddon_cloggedIntake_hillbilly"),
    ("iconAddon_bigBuckle_hillbilly",           "iconAddon_chainsBloody_hillbilly"),
    ("iconAddon_mothersHelpers_hillbilly",      "iconAddon_discardedAirFilter_hillbilly"),
    ("iconAddon_leafyMash_hillbilly",           "iconAddon_raggedEngine_hillbilly"),
    ("iconAddon_doomEngravings_hillbilly",      "iconAddon_iridescentEngravings_hillbilly"),
    ("iconAddon_blackGrease_hillbilly",         "iconAddon_theThompsonsMix_hillbilly"),
    ("iconAddon_pighouseGloves_hillbilly",      "iconAddon_highSpeedIdlerScrew_hillbilly"),
    ("iconAddon_iridescentBrick_hillbilly",     "iconAddon_filthySlippers_hillbilly"),

    # 8.1.0 knight changes
    ("iconAddon_ChainmailFragment_knight",      "iconAddon_SharpenedMount_knight"),
    ("iconAddon_LightweightGreaves_knight",     "iconAddon_JailersChimes_knight"),
]

class Config:
    def __init__(self, validate=False):
        if validate:
            if not os.path.isfile("config.json"):
                copyfile("assets/default_config.json", "config.json")

            with open("config.json", "r") as f:
                self.config = dict(json.load(f))
            self.commit_changes() # ensure all necessary keys are in (essentially copying missing values)

        with open("config.json", "r") as f:
            self.config = dict(json.load(f))

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

        self.bundled_profiles = []
        if os.path.isdir("assets/presets"):
            for file in os.listdir("assets/presets"):
                with open(f"assets/presets/{file}", "r") as f:
                    self.bundled_profiles.append(json.load(f))

    def top_left(self):
        return self.config["capture"]["top_left_x"], self.config["capture"]["top_left_y"]

    def path(self):
        return self.config["path"]

    def hotkey(self):
        return self.config["hotkey"].split(" ")

    def interaction(self):
        return self.config["interaction"]

    def primary_mouse(self):
        return self.config["primary_mouse"]

    def __profiles(self, bundled=False):
        return self.bundled_profiles if bundled else self.config["profiles"]

    def get_profile_by_id(self, profile_id, bundled=False):
        if profile_id is None:
            return {"id": None, "notes": ""}
        profiles = self.__profiles(bundled)
        return [p for p in profiles if p["id"] == profile_id].pop(0) if len(profiles) > 0 else {"id": None, "notes": ""}

    def notes_by_id(self, profile_id, bundled=False):
        if profile_id is None:
            return ""
        return self.get_profile_by_id(profile_id, bundled).get("notes", "")

    def preference_by_id(self, unlockable_id, profile_id, bundled=False):
        if profile_id is None:
            return 0, 0
        return Config.preference_by_profile(unlockable_id, self.get_profile_by_id(profile_id, bundled))

    @staticmethod
    def preference_by_profile(unlockable_id, profile_data):
        p = profile_data.get(unlockable_id, {})
        return p.get("tier", 0), p.get("subtier", 0)

    def profile_names(self, bundled=False):
        return [profile["id"] for profile in self.__profiles(bundled)]

    def commit_changes(self):
        with open("assets/default_config.json", "r") as default:
            default_config = dict(json.load(default))
            for profile in self.config.get("profiles", []):
                Config.migrate_profile(profile)
            with open("config.json", "w") as output:
                json.dump({
                    "path": self.config.get("path", default_config["path"]),
                    "hotkey": self.config.get("hotkey", default_config["hotkey"]),
                    "interaction": self.config.get("interaction", default_config["interaction"]),
                    "primary_mouse": self.config.get("primary_mouse", default_config["primary_mouse"]),
                    "profiles": self.config.get("profiles", default_config["profiles"]),
                }, output, indent=4) # to preserve order

    @staticmethod
    def verify_tiers(widgets):
        non_integer = []
        for widget in widgets:
            try:
                tier, subtier = widget.getTiers()
                if abs(tier) > 999 or abs(subtier) > 999:
                    non_integer.append(widget.unlockable.name)
            except ValueError:
                non_integer.append(widget.unlockable.name)
        return non_integer

    @staticmethod
    def verify_path(path):
        return os.path.isdir(path)

    def set_path(self, path):
        self.config["path"] = path
        self.commit_changes()

    def set_hotkey(self, hotkey):
        self.config["hotkey"] = " ".join(hotkey)
        self.commit_changes()

    def set_interaction(self, interaction):
        self.config["interaction"] = interaction
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

    def export_profile(self, profile_id, bundled=False):
        if profile_id is None:
            return
        profile = self.get_profile_by_id(profile_id, bundled)
        with open(f"exports/{profile_id}.emp", "w") as file:
            file.write(json.dumps(profile))

    @staticmethod
    def migrate_profile(profile):
        for migration_src, migration_dst in migrations:
            if migration_src in profile:
                profile[migration_dst] = profile[migration_src]
                profile.pop(migration_src)