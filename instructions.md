If you are a user reading this file, you are in the wrong place!
Please download the installer from https://github.com/IIInitiationnn/BloodEmporium/releases/latest

# Compilation (Powershell)
(Update state version)
- pipreqs . --force
- Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
- .\venv\Scripts\activate
- ~~autopytoexe.exe~~
  - ~~icon -> inspo1.ico~~
  - ~~settings -> import config from json file -> compile.json~~
  - ~~output directory: E:\Coding Projects\Blood Emporium Output~~
  - ~~add empty logs\ folder~~
  - ~~IF DEV: add empty output\ folder~~
- .\compile-onedir.sh \<version> <optional: "dev"> OR .\compile-onefile.sh \<version> <optional: "dev">
- deactivate
- Set-ExecutionPolicy Restricted -Scope CurrentUser

remove torch/lib/dnnl.lib

# New Content
- add to killers in db
### Killer (Addons)
- add addons unlockables in db
- add addons to assets/<killer>
### Killer + Survivor (Perks)
- add perks to unlockables in db
- add perks to assets/killer and assets/survivor
### Others
- new maps (offerings), generic perks etc to look out for
- mystery boxes scaled to 0.8

- update preference profiles