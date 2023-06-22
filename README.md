[![Blood Emporium](assets/images/splash.png)](https://github.com/IIInitiationnn/BloodEmporium/releases/latest)

[Releases](https://github.com/IIInitiationnn/BloodEmporium/releases) \
[Latest Release](https://github.com/IIInitiationnn/BloodEmporium/releases/latest)

A program to automatically level the Bloodweb in the game Dead by Daylight.

## Developer Notes
Assets for icon recognition are up-to-date as of Dead by Daylight Patch 7.0.1 (CHAPTER 28: End Transmission).\
To contact me about this project, or if you have any inquiries, please join the [Discord](https://discord.gg/J4KCqJJuaM).
Any bug reports, requests for technical support, or suggestions can be submitted either through this server or
[GitHub issues](https://github.com/IIInitiationnn/BloodEmporium/issues).\
This project is free and open-source. Any [donations](https://www.paypal.me/IIInitiationnn) are appreciated,
but absolutely not necessary. Please consider your own financial situation before donating!

## Overview
A [video guide](https://www.youtube.com/watch?v=3GFwQaB06Ug) is available for a quick summary of how the app works.
- Automatically selects optimal nodes on the Bloodweb based on user-configured preferences.
- Uses a cost algorithm to determine optimally how to select maximal preferred unlockables and minimal undesirable ones.
- Uses game icon files to identify nodes on the Bloodweb.
- Should not be bannable since there are no interactions with the game's memory or process, and the entire procedure
  occurs outside game matches. There have been no verified reported bans as of yet.

## Installation
1. Download the latest release [here](https://github.com/IIInitiationnn/BloodEmporium/releases/latest) - make sure you
   download `BloodEmporiumInstaller-version.exe` and not the source code. Install.
2. Run `Blood Emporium.exe` and check the `Settings` section to make sure the app is ready to run. For more information,
   see below; there is also a `Help` section in the app.

## Configuration
- You will be able to set your preferences and dislikes for certain addons, items, offerings and perks.
    - Each unlockable you configure will have a tier and subtier:
        - The higher the tier (or subtier), the higher your preference for that unlockable.
        - The lower the tier (or subtier), the lower your preference for that unlockable.
        - You do not need to configure unlockables for which you have a neutral preference.
          (tier and subtier are both automatically 0 in this case)
            - Any unlockables not in the profile will be assumed to be neutral (tier and subtier 0).
        - Tiers and subtiers can range from -999 to 999.
        - Tier (A + B) unlockable is equivalent in preference to a tier A unlockable + tier B unlockable.
            - For instance, a single tier 2 unlockable is equivalent to two tier 1 unlockables.
            - You can use these numbers to fine tune exactly how much you want each unlockable.
        - Similar mechanics apply with negative tiers to specify how much you dislike an unlockable.
        - Subtier allows for preference within a tier e.g. tier 3 subtier 3 is higher priority than tier 3 subtier 2.
- Each profile can store a different set of preferences, for easy switching when required.
- You can import and export profiles as `.emp` files to share with others.

## Features
- Allows user to configure which unlockables are preferred or undesirable.
- Three modes: naive (select randomly), aware (select items according to preference, either one at a time or along a 
  path).
- Two speeds: slow and fast.
- Bloodpoint spend limit / prestige level limit.
- Automatic termination upon bloodpoint depletion.
- Hotkey to run / stop the program (default: Ctrl + Alt + 9).
- Completely automatic and hands-free - and now, fast!

## Notes
- Shaders, game filters, and colourblind modes must be disabled while using this program,
  as colour changes interfere with object and colour recognition.

## Roadmap & Future Developments
- Summary of unlockables obtained after running.

## Known Issues
- Windows Defender and some other antivirus applications may report a threat. This is due to a library used to
  compile the application. You should be able to configure your antivirus to ignore this.
  To document that this software contains no malicious content, here are some threads detailing the problem:
    - https://github.com/pyinstaller/pyinstaller/issues/6754
    - https://www.reddit.com/r/learnpython/comments/ng3hmp/pyinstaller_create_onefile_exe_windows/
    - https://stackoverflow.com/questions/43777106/program-made-with-pyinstaller-now-seen-as-a-trojan-horse-by-avg

## Credits
- Icons taken from [The Noun Project](https://thenounproject.com/).
- Inspiration for GUI from a variety of [Wanderson's](https://www.youtube.com/WandersonIsMe) projects.
- Contributions from Saul Goodman and DAzVise.
- Many thanks to community members for submitting feedback, suggestions, and bug reports.