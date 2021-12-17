import os
import shutil

from data import Data
from paths import Path

if __name__ == '__main__':
    all_files = [(subdir, file) for subdir, dirs, files in os.walk(Path.vanilla_image) for file in files]

    for category, unlockable in Data.categories_as_tuples():
        if os.path.isfile(Path.assets_file(category, unlockable)):
            continue

        found = False
        for subdir, file in all_files:
            if unlockable == file[:-4]:
                if not os.path.isdir(f"{Path.assets}/{category}"):
                    os.mkdir(f"{Path.assets}/{category}")
                shutil.copyfile(os.path.join(subdir, file), Path.assets_file(category, unlockable))
                found = True
                break
        if not found:
            print(f"no source found for desired unlockable: {unlockable} under category: {category}")