# Compilation (Powershell)
- pipreqs . --force
- Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
- .\venv\Scripts\activate
- ~~autopytoexe.exe~~
  - ~~icon -> inspo1.ico~~
  - ~~settings -> import config from json file -> compile.json~~
  - ~~output directory: E:\Coding Projects\Blood Emporium Output~~
  - ~~add empty logs\ folder~~
  - ~~IF DEV: add empty output\ folder~~
- .\compile.sh \<version> <optional: "dev">
- deactivate
- Set-ExecutionPolicy Restricted -Scope CurrentUser

# New Content
- add to killers in db
### Killer (Addons)
- add addons unlockables in db
- add addons to assets/<killer>
### Killer + Survivor (Perks)
- add perks to unlockables in db
- add perks to assets/killer and assets/survivor
OTHERS
- new maps (offerings), generic perks etc to look out for