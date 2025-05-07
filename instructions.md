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

- update preference profiles (to assets/profiles folder as emps)
- update README
- zip updated assets & updated asset metadata version
- update app version if necessary

# Model Training
1. gather training images and name `<batch>.<descriptor> (number)`
2. move `compress.py` to batch folder and run (linux) to reduce file size
3. copy to `batch <batch> <nodes/edges> compressed/images` for both nodes and edges
4. run (windows) `python predict.py --nodes` and `python3 predict.py --edges` with latest models to generate annotations etc
5. add to roboflow in 80-20 training-validation split and edit if necessary
6. follow the below

## YOLOv8 Node Detection
- TODO
- create new cfg file with path to new data
- `yolo cfg="<file>.yaml"`
  - eg `yolo cfg="hyperparameters nodes v4.yaml"`

## YOLOv5-OBB Edge Detection
- download from roboflow in yolov5-obb format to `Blood Emporium Edge Detection/datasets`, naming folder `roboflow/`
- `cd yolov5_obb`
- `python train.py --hyp "../hyperparameters edges v2.yaml" --data ../datasets/roboflow/data.yaml --epochs 2000 --batch-size 16 --img 1024 --device 0 --patience 300 --adam`
  - this hyperparameter config file doesnt contain the data so we dont need to update it