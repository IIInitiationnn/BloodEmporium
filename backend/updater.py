import subprocess
import sys
from multiprocessing import Process

import requests
from parse import parse

from backend.state import State


# auto-update code courtesy of DAzVise#1666
# https://stackoverflow.com/questions/52127046/how-can-i-pull-private-repo-data-using-github-api
def get_latest_update():
    resp = requests.get("https://api.github.com/repos/IIInitiationnn/BloodEmporium/releases/latest")

    if resp.status_code == 200:
        data = resp.json()
        old_version = State.version
        new_version = data["tag_name"]

        # compare version numbers MAJOR.MINOR.PATCH or MAJOR.MINOR.PATCH-alpha.PRERELEASE
        if "alpha" in old_version:
            old_maj, old_min, old_patch, old_prerelease = parse("v{:n}.{:n}.{:n}-alpha.{:n}", old_version)
        else:
            old_maj, old_min, old_patch = parse("v{:n}.{:n}.{:n}", old_version)
            old_prerelease = None
        new_maj, new_min, new_patch = parse("v{:n}.{:n}.{:n}", new_version)
        if old_maj < new_maj or \
                (old_maj == new_maj and old_min < new_min) or \
                (old_maj == new_maj and old_min == new_min and old_patch < new_patch) or \
                (old_maj == new_maj and old_min == new_min and old_patch == new_patch and old_prerelease is not None):
            return data

class UpdaterProcess(Process):
    def __init__(self):
        Process.__init__(self)

    def run(self):
        if getattr(sys, "frozen", False):
            update = get_latest_update()

            if update is not None:
                download = requests.get(update["assets"][0]["browser_download_url"])
                with open("updater.exe", "wb") as file:
                    file.write(download.content)
                installer = subprocess.Popen("updater.exe")
                # installer.wait()
                # os.remove("updater.exe")

class Updater:
    def __init__(self):
        self.process = None

    def run(self):
        if self.process is None:
            self.process = UpdaterProcess()
            self.process.start()