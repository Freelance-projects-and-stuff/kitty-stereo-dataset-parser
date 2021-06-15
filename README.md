# Stereo-vision-madafaka

Amazingness is the key!

## Features

- Data parser for kitty stereo vision dataset
- Example for calibration and stereo depth maps creation

## Data

First step is to download data from [google drive] and [kitty site]. 

Put the data from google drive directly to repo's data folder. 
For kitty dataset you can choose whichever dataset you want (it should not matter). For instance, you could choose dataset number one labeled as "2011_09_26_drive_0001". Download `synced+rectified data` and `calibration data` and unzip it. Move both uziped folders to repo's data folder. 

Repo's stucture tree should look like:
```
Stereo
│   README.md
│   LICENCE
│   ...
│───data
│   │   params_cpp.xml
│   │   params_py.xml
│   │   stereoR2.mp4
│   │   stereoL2.mp4
│   │   ...
│   │─── stereoR
│   │─── stereoL
│   │─── kitty
│       │─── 2011_09_26
│           │   calib_cam_to_cam.txt
│           │   calib_imu_to_velo.txt
│           │   calib_velo_to_cam.txt
│           │─── 2011_09_26_drive_0001_sync
│───pykitty
│   │   ...
```

Go to `stereo/source kitty/parse_data.py` and change basedir to:
```sh
basedir = './data/kitty'
```

## Usable scripts
- `stereo/source_kitty/parse_data.py`  -> example on how to use kitty dataset parser
- `stereo/source_stereo/calibrate.py` -> cameras calibration procedure
- `stereo/source_stereo/movie3d.py` -> depth maps generation from calibrated cameras





   [google drive]: <https://drive.google.com/drive/folders/1370niF0eqB4zK3wXJOppOO5wHEiTBU19?usp=sharing>
   [kitty site]: <http://www.cvlibs.net/datasets/kitti/raw_data.php>
