# Blood Emporium
[Releases](https://github.com/IIInitiationnn/BloodEmporium/releases)

A program to automatically level the Bloodweb in the game Dead by Daylight.

### Overview
- Automatically selects optimal nodes on the Bloodweb based on user-configured preferences
- Uses game icon files to identify nodes on the Bloodweb
- Should not be bannable since there are no interactions with the game's memory or process
    - Use at your own risk! (maybe one day we'll ask a dev if it's okay)

### Configuration
- You will be able to set your preferences and dislikes for certain addons, items, offerings and perks
  - Each unlockable you configure will have a tier and subtier
    - The higher the tier (or subtier), the higher your preference for that item
    - The lower the tier (or subtier), the lower your preference for that item
    - You do not need to configure unlockables for which you have a neutral preference
    (tier and subtier are both 0 in this case)
    - Subtier allows for preference within a tier e.g. a tier 3 subtier 3 is higher priority than tier 3 subtier 2
    - Roughly speaking, two tier 1 unlockables is equivalent in preference to one tier 2 unlockable, and so on
    (basic maths)
- Each profile can store a different set of preferences, for easy switching when required

### Features
- Uses a cost algorithm to determine optimally how to select maximal preferred unlockables and minimal undesirable ones
- Allows user to configure which unlockables are preferred or undesirable
- Completely automatic and hands-free

### Issues
- Icon packs with similar-looking icons are more likely to cause incorrect object recognition, which may result in
  incorrect or suboptimal selection
- Shaders must be disabled while using this program, as colour changes interfere with object and colour recognition