import inspect
import json
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))))

from data import Data

if __name__ == "__main__":
    with open("config.json" if len(sys.argv) == 1 else sys.argv[1]) as f:
        config = dict(json.load(f))
        unlockables = Data.get_unlockables()

        updated_profiles = []
        for profile in config["profiles"]:
            updated_profile = {}
            for old_id, v in profile.items():
                if old_id == "id":
                    updated_profile[old_id] = v
                else:
                    unique_id = [unlockable.unique_id for unlockable in unlockables if unlockable.id == old_id].pop(0)
                    updated_profile[unique_id] = v
            updated_profiles.append(updated_profile)
        config["profiles"] = updated_profiles

        with open("updated_config.json", "w") as output:
            json.dump(config, output, indent=4)