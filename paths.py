import platform

# diff for win and mac, but in development we use linux
if platform.system() == "Linux":
    image_path = "/mnt/c/Program Files (x86)/Steam/steamapps/common/Dead by Daylight/DeadByDaylight/Content/UI/Icons"
else:
    image_path = "C:/Program Files (x86)/Steam/steamapps/common/Dead by Daylight/DeadByDaylight/Content/UI/Icons"

offerings_path = image_path + "/Favors" # 70, 50
addons_path = image_path + "/ItemAddons" # 50, 40
items_path = image_path + "/Items" # 50, 40
perks_path = image_path + "/Perks" # 67, 51