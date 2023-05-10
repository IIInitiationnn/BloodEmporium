import json

class Runtime:
    def __init__(self, validate=False):
        if validate:
            # create file if not exists
            try:
                with open("runtime.json", "x") as f:
                    f.write("{}")
            except FileExistsError:
                pass

            # validate json
            try:
                with open("runtime.json", "r") as f:
                    self.runtime = dict(json.load(f))
            except json.decoder.JSONDecodeError:
                with open("runtime.json", "w") as f:
                    f.write("{}")
                    self.runtime = dict()

            self.commit_changes()

        with open("runtime.json", "r") as f:
            self.runtime = dict(json.load(f))

    def profile(self):
        return self.runtime["profile"]

    def character(self):
        return self.runtime["character"]

    def mode(self):
        return self.runtime["mode"]

    def speed(self):
        return self.runtime["speed"]

    def limits(self, limit, fields):
        return (self.runtime["limits"][limit][field] for field in fields)

    def commit_changes(self):
        default_runtime = {
            "profile": "",
            "character": "survivor",
            "mode": "aware_multi",
            "speed": "slow",
            "limits": {
                "prestige": {
                    "enabled": False,
                    "value": "1"
                },
                "bloodpoint": {
                    "enabled": False,
                    "value": "69420"
                }
            }
        }
        updated_runtime = {field: self.runtime.get(field, default_runtime[field])
                           for field in ["profile", "character", "mode", "speed", "limits"]}
        for limit in ["prestige", "bloodpoint"]:
            if limit not in updated_runtime["limits"]:
                updated_runtime["limits"][limit] = default_runtime["limits"][limit]
            for field in ["enabled", "value"]:
                if field not in updated_runtime["limits"][limit]:
                    updated_runtime["limits"][limit][field] = default_runtime["limits"][limit][field]

        with open("runtime.json", "w") as output:
            json.dump(updated_runtime, output, indent=4) # to preserve order

    def set_profile(self, profile):
        self.runtime["profile"] = profile
        self.commit_changes()

    def set_character(self, character):
        self.runtime["character"] = character
        self.commit_changes()

    def set_mode(self, mode):
        self.runtime["mode"] = mode
        self.commit_changes()

    def set_speed(self, speed):
        self.runtime["speed"] = speed
        self.commit_changes()

    def change_limit(self, limit, **kwargs):
        for k, v in kwargs.items():
            self.runtime["limits"][limit][k] = v
        self.commit_changes()