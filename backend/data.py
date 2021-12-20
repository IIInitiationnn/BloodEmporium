import os
import sqlite3

from backend.config import Config
from paths import Path

class Unlockable:
    def __init__(self, unlockable_id, name, category, rarity, notes, unlockable_type, image_path):
        self.id = unlockable_id
        self.name = name
        self.category = category
        self.rarity = rarity
        self.notes = notes
        self.type = unlockable_type
        self.image_path = image_path

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

    @staticmethod
    def get_unlockables():
        all_files = [(subdir, file) for subdir, dirs, files in os.walk(Config().path()) for file in files]
        unlockables = []
        for row in Data.__unlockables_rows:
            u_id, u_name, u_category, u_rarity, u_notes, u_type = row

            # search in user's folder
            found = False
            for subdir, file in all_files:
                if u_id in file:
                    # bubba and hillbilly share an addon with the same name
                    if u_category == "bubba" and u_id == "iconAddon_speedLimiter" and "Xipre" in subdir:
                        continue
                    elif u_category == "hillbilly" and u_id == "iconAddon_speedLimiter" and "Xipre" not in subdir:
                        continue

                    u_image_path = os.path.normpath(os.path.join(subdir, file))
                    found = True
                    break

            # search in asset folder
            if not found:
                asset_path = Path.assets_file(u_category, u_id)
                if os.path.isfile(asset_path):
                    u_image_path = os.path.normpath(os.path.abspath(asset_path))
                else:
                    print(f"no source found for desired unlockable: {u_id} under category: {u_category}")
                    continue

            unlockables.append(Unlockable(u_id, u_name, u_category, u_rarity, u_notes, u_type, u_image_path))

        return unlockables

    @staticmethod
    def get_killers():
        return [killer for killer, in Data.__killers_rows]