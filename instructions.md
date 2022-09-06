# Compilation (Powershell)
- pipreqs . --force
- Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
- .\venv\Scripts\activate
- ~~autopytoexe.exe~~ use alternate command
- deactivate
- Set-ExecutionPolicy Restricted -Scope CurrentUser


- icon -> inspo1.ico
- settings -> import config from json file -> compile.json
- output directory: E:\Coding Projects\Blood Emporium Output


- add empty logs\ folder
- IF DEV: add empty output\ folder

alternatively (use this):
pyinstaller --noconfirm --onedir --windowed --name "Blood Emporium" --icon "E:/Coding Projects/Blood Emporium/references/inspo1.ico" --add-data "E:/Coding Projects/Blood Emporium/assets;assets/" --paths "E:/Coding Projects/Blood Emporium/backend" --distpath "E:\Coding Projects\Blood Emporium Output" "E:/Coding Projects/Blood Emporium/main.py"
mkdir "..\Blood Emporium Output\Blood Emporium\output"

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