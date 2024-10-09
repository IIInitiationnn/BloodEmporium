import json
import os.path
import subprocess
import sys
import zipfile
from multiprocessing import Process, Pipe

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

def get_latest_assets():
    resp = requests.get("https://github.com/IIInitiationnn/BloodEmporium/raw/refs/heads/master/asset_metadata.json")
    if resp.status_code != 200:
        return

    data = resp.json()
    latest_version = data["version"]

    if not os.path.isfile("asset_metadata.json"):
        current_version = -1
    else:
        try:
            with open("asset_metadata.json", "r") as f:
                current_version = dict(json.load(f))["version"]
        except:
            return data # corrupted metadata file

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
    def __init__(self, pipe: Pipe):
        Process.__init__(self)
        self.pipe = pipe

    def run(self):
        if getattr(sys, "frozen", False):
            update = get_latest_update()

            if update is not None:
                download = requests.get(update["assets"][0]["browser_download_url"], stream=True)

                total_size = int(download.headers.get("content-length", None))
                block_size = 1024

                with open("updater.exe", "wb") as file:
                    for i, data in enumerate(download.iter_content(chunk_size=block_size), 1):
                        self.pipe.send(("progress", (min(100, round(100 * i * (block_size / total_size))),)))
                        file.write(data)
                installer = subprocess.Popen("updater.exe")
                self.pipe.send(("completion", ()))
                # installer.wait()
                # os.remove("updater.exe")

class AssetUpdaterProcess(Process):
    def __init__(self, pipe: Pipe):
        Process.__init__(self)
        self.pipe = pipe

    def run(self):
        if getattr(sys, "frozen", False):
            update = get_latest_assets()

            if update is not None:
                download = requests.get("https://github.com/IIInitiationnn/BloodEmporium/raw/refs/heads/master/assets.zip", stream=True)

                total_size = int(download.headers.get("content-length", None))
                block_size = 1024

                new_asset_path = "new_assets.zip"
                with open(new_asset_path, "wb") as file:
                    for i, data in enumerate(download.iter_content(chunk_size=block_size), 1):
                        self.pipe.send(("progress", (min(100, round(100 * i * (block_size / total_size))),)))
                        file.write(data)

                with zipfile.ZipFile(new_asset_path, "r") as zip_ref:
                    zip_ref.extractall("assets/")

                with open("asset_metadata.json", "w") as f:
                    json.dump(update, f, indent=4)

                self.pipe.send(("completion", ()))