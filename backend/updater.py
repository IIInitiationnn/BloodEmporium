import subprocess
import sys
from multiprocessing import Process

import requests
from parse import parse

from backend.state import State


# contributions to auto-update code courtesy of DAzVise#1666
# https://stackoverflow.com/questions/52127046/how-can-i-pull-private-repo-data-using-github-api
def get_latest_update():
    resp = requests.get("https://api.github.com/repos/IIInitiationnn/BloodEmporium/releases/latest")
    if resp.status_code != 200:
        return

    data = resp.json()
    current_version = Version(State.version)
    latest_version = Version(data["tag_name"])

    if current_version.prerelease is not None: # current version is alpha
        resp2 = requests.get("https://api.github.com/repos/IIInitiationnn/BloodEmporium/releases")
        if resp2.status_code != 200:
            return
        data2 = resp2.json()

        latest_alpha_version = None
        latest_alpha_data = None
        for release in data2:
            if release["prerelease"]:
                latest_alpha_data = release
                latest_alpha_version = Version(release["tag_name"])
                break

        if latest_alpha_version is None:
            if current_version < latest_version:
                return data
        elif current_version == latest_alpha_version:
            if current_version < latest_version:
                return data
        else:
            if latest_alpha_version < latest_version:
                return data
            if latest_version < latest_alpha_version:
                return latest_alpha_data
    else:
        if current_version < latest_version:
            return data

class Version:
    def __init__(self, version_string):
        if "alpha" in version_string:
            self.maj, self.min, self.patch, self.prerelease = parse("v{:n}.{:n}.{:n}-alpha.{:n}", version_string)
        else:
            self.maj, self.min, self.patch = parse("v{:n}.{:n}.{:n}", version_string)
            self.prerelease = None

    # compare version numbers MAJOR.MINOR.PATCH or MAJOR.MINOR.PATCH-alpha.PRERELEASE
    def __eq__(self, other):
        return (self.maj == other.maj and self.min == other.min and self.patch == other.patch and
                self.prerelease == other.prerelease)

    def __ne__(self, other):
        return not (self == other)

    def __lt__(self, other):
        return (self.maj < other.maj or
                (self.maj == other.maj and self.min < other.min) or
                (self.maj == other.maj and self.min == other.min and self.patch < other.patch) or
                (self.maj == other.maj and self.min == other.min and self.patch == other.patch and
                 (self.prerelease is not None or self.prerelease < other.prerelease)))

    def __le__(self, other):
        return self < other or self == other

    def __gt__(self, other):
        return not (self <= other)

    def __ge__(self, other):
        return not (self < other)

    def __str__(self):
        return f"v{self.maj}.{self.min}.{self.patch}" + \
               (f"-alpha.{self.prerelease}" if self.prerelease is not None else "")

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