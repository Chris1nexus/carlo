# carla-data-collector
A tool to generate synthetic autonomous driving datasets from arbitrary sensor setups from the carla simulator

## Intro
The script 'sensor_capture.py' allows to generate datasets of arbitrary size by collecting data
from user defined sensor setups.   

The data is **synchronized**, so the multiple sensor perspectives can be fused together.


To define a sensor setup
proceed by creating a SimulationCfg object, and then adding new sensors to it


Carla-simulator defines its coordinate frame as LEFT-HANDED:

+ X is forward
+ Y is right
+ Z is up

```python     
cfg = SimulationCfg(sync_sim_stepsize=FIXED_DELTA_SECONDS)
camera_setup_blueprints = [SenseBP.RGBCAMERA, SenseBP.DEPTH, SenseBP.SEGMENTATION]
cfg.add_sensor('lidar',SenseBP.LIDAR,
                   x=-0.595, z=1.73, 
                   sensor_options=lidar_sensor_options )
cfg.add_sensor('cam0',SenseBP.RGBCAMERA,x=-0.325, z=1.65, sensor_options=front_camera_attributes )
```
    
                    
After the definition above, simply call:
```python
cfg.write_to_file()
``` 
To generate the simulated sensor setup that will be automatically 
read when calling the script sensor_capture.py
    
##Usage:

0. define your sensor setup on the provided jupyter notebook or on your custom python script.
1. Make sure to give your preferred path where the simulation setup will be generated.
   In all cases, everything that concerns the simulation setup will fall under that directory,  
   in the folder 'simsetup'  
   Every attribute, pose or blueprint follows the naming convention provided by carla.  
   So to define your own custom sensor options, just referr to (https://carla.readthedocs.io/en/latest/python_api/)  
1. start CarlaUE4.sh
2. python3 sensor_capture.py --help to see available options  
   DO NOT FORGET TO GIVE THE PATH OF THE DIRECTORY WHERE THE GENERATED SIMSETUP IS LOCATED   
   (do not add 'simsetup' to the folder path, just give the directory path that contains it)  

3. data will be stored in a folder named according to the chosen simulation parameters  
   (customizable by the command line args of sensor_capture.py)




## Dataset structure
top level folder contains the directories
*sensor_data
*calibration

Sensor_data contains all data of the sensors in subfolders named with the provided sensor_label.     
For each of these, one or more modalities, dependeing on how it has been set up, are available.  
E.g. 
* sensor_data
    * front_camera
        * rgbcamera
        * depth
        * segmentation
    * lidar
    * imu
    * ...

The calibration folder contains the pose of the sensor in vehicle coordinates.   
* calibration
    * front_camera.json
    * imu.json
    * ...
The origin of the vehicle coordinates is the center point of its bounding box at the ground level (z-coord == 0 at the contact point with the ground)     
In case of camera sensors, the intrinsics matrix is also provided (can be found as calib_mtx in the files associated with cameras)     
Although not always necessary, the **reflection matrix needed to transform from unreal to camera coordinates is provided  'unreal_to_camcoordsys_reflection'**    

Cam coordinates, in the literature are always defined and treated as follows:
* Z front
* X right
* Y down

The transform from unreal engine coords to camera coords is illustrated as follows(credit to the drawing made in the examples/lidar_to_camera.py script) :
```  
  ^ z                       . z   
  |                        /   
  |              to:      +-------> x   
  | . x                   |   
  |/                      |   
  +-------> y             v y   
```





