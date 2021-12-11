import platform

from config import Config


class Path:
    # diff for win and mac, but in development we use linux
    if platform.system() == "Linux":
        vanilla_image = "/mnt/c/Program Files (x86)/Steam/steamapps/common/Dead by Daylight/DeadByDaylight/Content/UI/Icons (Vanilla)"
        image = "/mnt/c/Program Files (x86)/Steam/steamapps/common/Dead by Daylight/DeadByDaylight/Content/UI/Icons"
    else:
        vanilla_image = "C:/Program Files (x86)/Steam/steamapps/common/Dead by Daylight/DeadByDaylight/Content/UI/Icons (Vanilla)"
        image = Config().path()

    offerings = image + "/Favors" # 70, 50
    addons = image + "/ItemAddons" # 50, 40
    items = image + "/Items" # 50, 40
    perks = image + "/Perks" # 67, 51

    assets = "assets"
    assets_origins = "assets/origins"

    @staticmethod
    def assets_file(category, unlockable):
        return f"{Path.assets}/{category}/{unlockable}.png"