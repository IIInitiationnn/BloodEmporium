import os
import sqlite3

from config import Config
from paths import Path

class Unlockable:
    @staticmethod
    def generate_unique_id(unlockable_id, category):
        return f"{unlockable_id}_{category}"

    def __init__(self, unlockable_id, name, category, rarity, notes, unlockable_type, image_path, is_custom_icon):
        self.unique_id = Unlockable.generate_unique_id(unlockable_id, category)
        self.id = unlockable_id
        self.name = name
        self.category = category
        self.rarity = rarity
        self.notes = notes
        self.type = unlockable_type
        self.image_path = image_path
        self.is_custom_icon = is_custom_icon

    def set_image_path(self, image_path):
        self.image_path = image_path

    def set_is_custom_icon(self, is_custom_icon):
        self.is_custom_icon = is_custom_icon

class Data:
    __connection = None
    try:
        __connection = sqlite3.connect(Path.assets_database)
        print("connected to database")
    except:
        print(f"error")

    __cursor = __connection.cursor()
    __cursor.execute("SELECT * FROM unlockables")
    __unlockables_rows = __cursor.fetchall()

    __cursor.execute("SELECT * FROM killers")
    __killers_rows = __cursor.fetchall()

    __connection.close()
    print("disconnected from database")

    @staticmethod
    def get_icons():
        all_files = [(subdir, file) for subdir, dirs, files in os.walk(Config().path()) for file in files]
        icons = {}
        for row in Data.__unlockables_rows:
            u_id, _, u_category, _, _, _ = row

            # search in user's folder
            u_image_path = None
            u_is_custom_icon = None
            for subdir, file in all_files:
                if u_id in file:
                    # bubba and hillbilly share an addon with the same name
                    if u_category == "bubba" and u_id == "iconAddon_speedLimiter" and "Xipre" in subdir:
                        continue
                    elif u_category == "hillbilly" and u_id == "iconAddon_speedLimiter" and "Xipre" not in subdir:
                        continue

                    u_image_path = os.path.normpath(os.path.join(subdir, file))
                    u_is_custom_icon = True
                    break

            # search in asset folder
            if u_image_path is None:
                asset_path = Path.assets_file(u_category, u_id)
                if os.path.isfile(asset_path):
                    u_image_path = os.path.normpath(os.path.abspath(asset_path))
                    u_is_custom_icon = False
                else:
                    print(f"no source found for desired unlockable: {u_id} under category: {u_category}")
                    continue

            if u_image_path is not None:
                icons[Unlockable.generate_unique_id(u_id, u_category)] = {
                    "image_path": u_image_path,
                    "is_custom_icon": u_is_custom_icon,
                }

        return icons

    @staticmethod
    def get_unlockables():
        all_files = [(subdir, file) for subdir, dirs, files in os.walk(Config().path()) for file in files]
        unlockables = []
        for row in Data.__unlockables_rows:
            u_id, u_name, u_category, u_rarity, u_notes, u_type = row

            # search in user's folder
            u_image_path = None
            u_is_custom_icon = None
            for subdir, file in all_files:
                if u_id in file:
                    # bubba and hillbilly share an addon with the same name
                    if u_category == "bubba" and u_id == "iconAddon_speedLimiter" and "Xipre" in subdir:
                        continue
                    elif u_category == "hillbilly" and u_id == "iconAddon_speedLimiter" and "Xipre" not in subdir:
                        continue

                    u_image_path = os.path.normpath(os.path.join(subdir, file))
                    u_is_custom_icon = True
                    break

            # search in asset folder
            if u_image_path is None:
                asset_path = Path.assets_file(u_category, u_id)
                if os.path.isfile(asset_path):
                    u_image_path = os.path.normpath(os.path.abspath(asset_path))
                    u_is_custom_icon = False
                else:
                    print(f"no source found for desired unlockable: {u_id} under category: {u_category}")
                    continue

            if u_image_path is not None:
                unlockables.append(Unlockable(u_id, u_name, u_category, u_rarity, u_notes, u_type, u_image_path,
                                              u_is_custom_icon))

        return unlockables

    @staticmethod
    def get_killers(sort):
        killers = [killer for killer, in Data.__killers_rows]
        return sorted(killers) if sort else killers

    @staticmethod
    def get_categories(sort):
        return ["universal", "survivor", "killer"] + Data.get_killers(sort)

    @staticmethod
    def get_characters(sort):
        return ["survivor"] + Data.get_killers(sort)

    @staticmethod
    def get_types():
        return ["add-on", "item", "offering", "perk", "universal"] # universal = mystery box

    @staticmethod
    def get_rarities():
        return ["common", "uncommon", "rare", "very_rare", "ultra_rare", "event", "varies"]

    @staticmethod
    def get_cost(rarity):
        return {
            "common": 2000,
            "uncommon": 2500,
            "rare": 3250,
            "very_rare": 4000,
            "ultra_rare": 5000,
            "event": 2000,
            "varies": 5000, # assume worst case
        }[rarity]

    @staticmethod
    def get_sorts():
        return ["name", "character", "rarity", "type"]

    @staticmethod
    def __get_default_ordering(widgets):
        print(len(widgets))
        h = [widget for widget in widgets for u_id, u_name, u_category, _, _, _ in Data.__unlockables_rows
             if Unlockable.generate_unique_id(u_id, u_category) == widget.unlockable.unique_id]
        print(len(h))
        return h

    @staticmethod
    def filter(unlockable_widgets, name, categories, rarities, types, sort_by=None):
        # category = character

        # technically not needed since unlockable_widgets never changes order
        # sorted_widgets = Data.__get_default_ordering(unlockable_widgets)
        sorted_widgets = unlockable_widgets
        if sort_by == "name":
            sorted_widgets = sorted(sorted_widgets, key=lambda widget: widget.unlockable.name.replace("\"", ""))
        elif sort_by == "character":
            sorted_widgets = sorted(sorted_widgets, key=lambda widget: widget.unlockable.category)
        elif sort_by == "rarity":
            rarities_enum = {"common": 1, "uncommon": 2, "rare": 3, "very_rare": 4,
                             "ultra_rare": 5, "event": 6, "varies": 7}
            sorted_widgets = sorted(sorted_widgets, key=lambda widget: rarities_enum[widget.unlockable.rarity])
        elif sort_by == "type":
            sorted_widgets = sorted(sorted_widgets, key=lambda widget: widget.unlockable.type)

        filtered = []
        for unlockable_widget in sorted_widgets:
            unlockable = unlockable_widget.unlockable
            if name != "" and name.lower() not in unlockable.name.lower():
                filtered.append((unlockable_widget, False))
                continue

            if len(categories) != 0 and unlockable.category not in categories:
                filtered.append((unlockable_widget, False))
                continue

            if len(rarities) != 0 and unlockable.rarity not in rarities:
                filtered.append((unlockable_widget, False))
                continue

            if len(types) != 0 and unlockable.type not in types:
                filtered.append((unlockable_widget, False))
                continue

            filtered.append((unlockable_widget, True))

        return filtered

    # TODO move following to config class
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