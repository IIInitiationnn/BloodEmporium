[![Blood Emporium](assets/images/splash.png)](https://github.com/IIInitiationnn/BloodEmporium/releases/latest)

[Releases](https://github.com/IIInitiationnn/BloodEmporium/releases)

A program to automatically level the Bloodweb in the game Dead by Daylight.

## Developer Notes
Assets for icon recognition are up-to-date as of Dead by Daylight Patch 6.4.0 (CHAPTER 26: Forged in Fog).\
To contact me about this project, or if you have any inquiries, please join the [Discord](https://discord.gg/J4KCqJJuaM).
Any bug reports, requests for technical support, or suggestions can be submitted through either this server or
[GitHub issues](https://github.com/IIInitiationnn/BloodEmporium/issues).\
This project is free and open-source. Any [donations](https://www.paypal.me/IIInitiationnn) are appreciated,
but absolutely not necessary. Please consider your own financial situation before donating!

## Installation
1. Download the latest release [here](https://github.com/IIInitiationnn/BloodEmporium/releases/latest) - make sure you
download `Blood Emporium.version.zip` and not the source code.
2. Extract the ZIP archive at a folder of your choice. Please make sure the path to this folder
does not contain any special unicode characters (see [#5](https://github.com/IIInitiationnn/BloodEmporium/issues/5))
3. Run `Blood Emporium.exe` and check the `Settings` section to make sure the app is ready to run. For more information,
see below; there is also a `Help` section in the app.

## Overview
- Automatically selects optimal nodes on the Bloodweb based on user-configured preferences.
- Uses a cost algorithm to determine optimally how to select maximal preferred unlockables and minimal undesirable ones.
- Uses game icon files to identify nodes on the Bloodweb.
- Should not be bannable since there are no interactions with the game's memory or process.

## Configuration
- You will be able to set your preferences and dislikes for certain addons, items, offerings and perks.
  - Each unlockable you configure will have a tier and subtier:
    - The higher the tier (or subtier), the higher your preference for that item.
    - The lower the tier (or subtier), the lower your preference for that item.
    - You do not need to configure unlockables for which you have a neutral preference.
    (tier and subtier are both automatically 0 in this case)
      - Any items not in the profile will be assumed to be tier and subtier 0.
    - Tiers and subtiers can be from -999 to 999.
    - Subtier allows for preference within a tier e.g. a tier 3 subtier 3 is higher priority than tier 3 subtier 2.
    - Roughly speaking, two tier 1 unlockables is equivalent in preference to one tier 2 unlockable, and so on.
    (basic maths)
- Each profile can store a different set of preferences, for easy switching when required.

## Features
- Allows user to configure which unlockables are preferred or undesirable.
- Two modes: NAIVE (select any available item) and AWARE (select items according to preference)
- Bloodpoint spend limit / prestige level limit.
- Hotkey to run / stop the program (default: Ctrl + Alt + 9).
- Completely automatic and hands-free.

## Issues
- Icon packs with similar-looking icons are more likely to cause incorrect object recognition, which may result in
  incorrect or suboptimal selection.
- Shaders must be disabled while using this program, as colour changes interfere with object and colour recognition.

## Known Bugs
- Slight inaccuracies in detecting which unlockables are connected (especially as of Patch 6.4.0).

## Roadmap & Future Developments
- Improved accuracy
- Automatic termination upon depleting bloodpoints
- Item summary

## Credits
- Icons taken from [The Noun Project](https://thenounproject.com/).
- Inspiration for GUI from a variety of [Wanderson's](https://www.youtube.com/WandersonIsMe) projects.
- Thank you to the beta testers for providing feedback, suggestions, and bug reports.