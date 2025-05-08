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
- download from roboflow in yolov8 format to `Blood Emporium Node Detection/datasets`
  - there is a `main.py` file that could be used, update this note if i use it in future
- create new hyperparameter yaml file `hyperparameters nodes v<version>.yaml` with path to new data with the version corresponding to the model number
- modify the `data.yaml` file for absolute paths instead of relative paths to train/valid
- in `Blood Emporium Node Detection`, `yolo cfg="hyperparameters nodes v<version>.yaml"`
  - to resume, set `resume` to `True` in hyperparameters config and use `yolo cfg="hyperparameters nodes v<version>.yaml"`

- copy model from `runs/train` to update model from `Blood Emporium/assets/models`, as well as the prediction model in `node-detector`: `nodes v<version> (train<run>)`
  - run `python main_node.py` in `node-detector` to verify validity (need to change model name in `nodedetect.py`)

## YOLOv5-OBB Edge Detection
- download from roboflow in yolov5-obb format to `Blood Emporium Edge Detection/datasets`, naming folder `roboflow/`
-   there is a `main.py` file that could be used, update this note if i use it in future
- navigate to `node-detector`
- `.\venv\Scripts\activate`
- `cd yolov5_obb`
- `$env:PYTORCH_CUDA_ALLOC_CONF="max_split_size_mb:1024"`
- `echo $env:PYTORCH_CUDA_ALLOC_CONF`
- `python train.py --hyp "../hyperparameters edges v2.yaml" --data ../datasets/roboflow/data.yaml --epochs 2000 --batch-size 8 --img 1024 --device 0 --patience 300 --adam`
  - this hyperparameter config file doesnt contain the data so we dont need to update it
  - i used to use batch size 16 but for some reason i cant on my better gpu??? idk youd think i could use an even bigger batch size now but i guess not
  - to resume, add `--resume`
- copy model from `runs/train` to update model from `Blood Emporium/assets/models`, as well as the prediction model in `node-detector`: `edges v<version> (exp<run>)`
  - run `python main_edge.py` in `node-detector` to verify validity (need to change model name in `edgedetect.py`)