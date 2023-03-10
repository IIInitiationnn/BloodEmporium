import platform

from config import Config


class Path:
    if platform.system() == "Linux":
        vanilla_image = "/mnt/e/Coding Projects/DBD/Icons (Vanilla)"
        image = "/mnt/c/Program Files (x86)/Steam/steamapps/common/Dead by Daylight/DeadByDaylight/Content/UI/Icons"
    else:
        vanilla_image = "E:/Coding Projects/DBD/Icons (Vanilla)"
        image = Config().path()

    offerings = image + "/Favors" # 70, 50
    addons = image + "/ItemAddons" # 50, 40
    items = image + "/Items" # 50, 40
    perks = image + "/Perks" # 67, 51

    assets = "assets"
    assets_backgrounds = "assets/backgrounds"
    assets_database = "assets/data.db"

    @staticmethod
    def assets_file(category, unlockable):
        return f"{Path.assets}/{category}/{unlockable}.png"