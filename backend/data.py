import os
import sqlite3

from config import Config
from paths import Path

class Unlockable:
    @staticmethod
    def generate_unique_id(unlockable_id, category):
        return f"{unlockable_id}_{category}"

    def __init__(self, unlockable_id, name, category, rarity, notes, unlockable_type, order, image_path, is_custom_icon):
        self.unique_id = Unlockable.generate_unique_id(unlockable_id, category)
        self.id = unlockable_id
        self.name = name
        self.category = category
        self.rarity = rarity
        self.notes = notes
        self.type = unlockable_type
        self.order = order
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
    __cursor.execute("SELECT id, name, category, rarity, notes, type, \"order\" FROM unlockables ORDER BY \"order\"")
    __unlockables_rows = __cursor.fetchall()

    __cursor.execute("SELECT id, alias, name FROM killers")
    __killers_rows = __cursor.fetchall()

    __connection.close()
    print("disconnected from database")

    @staticmethod
    def get_icons():
        all_files = [(subdir, file) for subdir, dirs, files in os.walk(Config().path()) for file in files]
        icons = {}
        for row in Data.__unlockables_rows:
            u_id, _, u_category, _, _, _, _ = row

            # search in user's folder
            u_image_path = None
            u_is_custom_icon = None
            for subdir, file in all_files:
                if u_id.lower() in file.lower(): # in case pack has recapitalised files
                    # bubba and hillbilly share an addon with the same name TODO what is location of iconAddon_chainsBloody for hillbilly? does it use bubba asset
                    # if u_category == "bubba" and u_id == "iconAddon_chainsBloody" and "Xipre" in subdir:
                    #     continue
                    # elif u_category == "hillbilly" and u_id == "iconAddon_chainsBloody" and "Xipre" not in subdir:
                    #     continue

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
            u_id, u_name, u_category, u_rarity, u_notes, u_type, u_order = row

            # search in user's folder
            u_image_path = None
            u_is_custom_icon = None
            for subdir, file in all_files:
                if u_id.lower() in file.lower(): # in case pack has recapitalised files
                    # bubba and hillbilly share an addon with the same name
                    # if u_category == "bubba" and u_id == "iconAddon_chainsBloody" and "Xipre" in subdir:
                    #     continue
                    # elif u_category == "hillbilly" and u_id == "iconAddon_chainsBloody" and "Xipre" not in subdir:
                    #     continue

                    # nurse and dracula share an addon with the same name
                    if u_id.lower() == "iconAddon_PocketWatch".lower():
                        if u_category == "dark lord" and "Eclair" not in subdir:
                            continue # this is nurse's addon, ignore it for dracula
                        if u_category == "nurse" and "Eclair" in subdir:
                            continue # this is dracula's addon, ignore it for nurse

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
                unlockables.append(Unlockable(u_id, u_name, u_category, u_rarity, u_notes, u_type, u_order, u_image_path,
                                              u_is_custom_icon))

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
        return ["add-on", "item", "offering", "perk", "universal"] # universal = mystery box

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