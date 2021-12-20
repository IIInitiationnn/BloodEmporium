import os
import shutil

from data import Data
from paths import Path

if __name__ == '__main__':
    all_files = [(subdir, file) for subdir, dirs, files in os.walk(Path.vanilla_image) for file in files]

    for unlockable in Data.get_unlockables():

        if os.path.isfile(Path.assets_file(unlockable.category, unlockable.id)):
            continue

        found = False
        for subdir, file in all_files:
            if unlockable.id == file[:-4]:
                if not os.path.isdir(f"{Path.assets}/{unlockable.category}"):
                    os.mkdir(f"{Path.assets}/{unlockable.category}")
                shutil.copyfile(os.path.join(subdir, file), Path.assets_file(unlockable.category, unlockable.id))
                found = True
                break
        if not found:
            print(f"no source found for desired unlockable: {unlockable.id} under category: {unlockable.category}")