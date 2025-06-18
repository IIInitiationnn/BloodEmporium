import os
import sqlite3

from config import Config
from paths import Path

class Unlockable:
    @staticmethod
    def generate_unique_id(unlockable_id, category):
        return f"{unlockable_id}_{category}"

    def __init__(self, unlockable_id, name, category, rarity, notes, unlockable_type, order, image_paths, are_custom_icons):
        self.unique_id = Unlockable.generate_unique_id(unlockable_id, category)
        self.id = unlockable_id
        self.name = name
        self.category = category
        self.rarity = rarity
        self.notes = notes
        self.type = unlockable_type
        self.order = order
        self.image_paths = image_paths
        self.are_custom_icons = are_custom_icons

    def set_image_path(self, image_paths):
        self.image_paths = image_paths

    def set_are_custom_icons(self, are_custom_icons):
        self.are_custom_icons = are_custom_icons

class Data:
    __connection = None
    try:
        __connection = sqlite3.connect(Path.assets_database)
        print("connected to database")
    except:
        print(f"error")

    __cursor = __connection.cursor()
    __cursor.execute("SELECT id, alternate_path, name, category, rarity, notes, type, \"order\" FROM unlockables ORDER BY \"order\"")
    __unlockables_rows = __cursor.fetchall()

    __cursor.execute("SELECT id, alias, name FROM killers")
    __killers_rows = __cursor.fetchall()

    __connection.close()
    print("disconnected from database")

    @staticmethod
    def __get_unlockable_data():
        all_files = [(subdir, file) for subdir, dirs, files in os.walk(Config().path()) for file in files]
        rows = []
        for row in Data.__unlockables_rows:
            u_id, u_alternate_path, u_name, u_category, u_rarity, u_notes, u_type, u_order = row

            # search in user's folder
            u_image_paths = []
            u_are_custom_icons = []

            possible_paths = [u_id] if u_alternate_path is None else [u_id, u_alternate_path]
            found_paths = []
            for possible_path in possible_paths:
                for subdir, file in all_files:
                    # lower() in case pack has recapitalised files
                    if possible_path.lower() in file.lower():
                        # nurse and dracula share an addon with the same name
                        if possible_path.lower() == "iconAddon_PocketWatch".lower():
                            if u_category == "dark lord" and "Eclair" not in subdir:
                                continue # this is nurse's addon, ignore it for dracula
                            if u_category == "nurse" and "Eclair" in subdir:
                                continue # this is dracula's addon, ignore it for nurse

                        u_image_paths.append(os.path.normpath(os.path.join(subdir, file)))
                        u_are_custom_icons.append(True)
                        found_paths.append(possible_path)
                        break

            for found_path in found_paths:
                possible_paths.remove(found_path)

            # search in asset folder
            for possible_path in possible_paths:
                asset_path = Path.assets_file(u_category, possible_path)
                if os.path.isfile(asset_path):
                    u_image_paths.append(os.path.normpath(os.path.abspath(asset_path)))
                    u_are_custom_icons.append(False)

            if len(u_image_paths) == 0:
                print(f"no source found for desired unlockable: {u_id} under category: {u_category}")
                continue

            rows.append(row + (u_image_paths, u_are_custom_icons))
        return rows

    @staticmethod
    def get_icons():
        icons = {}
        for row in Data.__get_unlockable_data():
            u_id, u_alternate_path, u_name, u_category, u_rarity, u_notes, u_type, u_order, u_image_paths, u_are_custom_icons = row
            icons[Unlockable.generate_unique_id(u_id, u_category)] = {
                "image_paths": u_image_paths,
                "are_custom_icons": u_are_custom_icons,
            }

        return icons

    @staticmethod
    def get_unlockables():
        unlockables = []
        for row in Data.__get_unlockable_data():
            u_id, u_alternate_path, u_name, u_category, u_rarity, u_notes, u_type, u_order, u_image_paths, u_are_custom_icons = row
            unlockables.append(Unlockable(u_id, u_name, u_category, u_rarity, u_notes, u_type, u_order, u_image_paths, u_are_custom_icons))
        return unlockables

    @staticmethod
    def get_killers(sort):
        # sort by alias
        return sorted(Data.__killers_rows, key=lambda row: row[1]) if sort else Data.__killers_rows

    @staticmethod
    def get_killer_alias():
        return {killer_id: f"{alias}" for killer_id, alias, name in Data.__killers_rows}

    @staticmethod
    def get_killer_full_name(include_the=False):
        return {killer_id: f"{'The ' if include_the else ''}{alias} ({name})" for killer_id, alias, name in Data.__killers_rows}

    @staticmethod
    def get_categories(sort):
        return ["universal", "survivor", "killer"] + [killer_id for killer_id, _, _ in Data.get_killers(sort)]

    @staticmethod
    def get_characters(sort):
        return ["survivor"] + [killer_id for killer_id, _, _ in Data.get_killers(sort)]

    @staticmethod
    def get_types():
        return ["add-on", "item", "offering", "perk", "mystery_box"]

    @staticmethod
    def get_rarities():
        return ["common", "uncommon", "rare", "very_rare", "ultra_rare", "event", "varies"]

    __costs = {
        "common": 2000,
        "uncommon": 2500,
        "rare": 3250,
        "very_rare": 4000,
        "ultra_rare": 5000,
        "event": 2000,
        "varies": 5000, # assume worst case
    }

    @staticmethod
    def get_cost(rarity, unlockable_type):
        return 4000 if unlockable_type == "perk" else Data.__costs[rarity]

    @staticmethod
    def get_sorts():
        return ["default", "name", "character", "rarity", "type", "tier"]

    @staticmethod
    def filter(unlockable_widgets, name, categories, rarities, types, sort_by=None):
        # category = character

        sorted_widgets = unlockable_widgets.copy()
        killer_aliases = Data.get_killer_alias()
        if sort_by == "default":
            sorted_widgets.sort(key=lambda widget: widget.unlockable.order)
        elif sort_by == "name":
            sorted_widgets.sort(key=lambda widget: widget.unlockable.name.replace("\"", ""))
        elif sort_by == "character":
            sorted_widgets.sort(key=lambda widget: killer_aliases.get(widget.unlockable.category, widget.unlockable.category))
        elif sort_by == "rarity":
            rarities_enum = {"common": 1, "uncommon": 2, "rare": 3, "very_rare": 4,
                             "ultra_rare": 5, "event": 6, "varies": 7}
            sorted_widgets.sort(key=lambda widget: rarities_enum[widget.unlockable.rarity])
        elif sort_by == "type":
            sorted_widgets.sort(key=lambda widget: widget.unlockable.type)
        elif sort_by == "tier":
            def sort(widget):
                try:
                    return widget.getTiers()
                except:
                    return 1000, 1000
            sorted_widgets.sort(key=sort, reverse=True)

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