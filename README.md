# carla-data-collector
A tool to generate synthetic autonomous driving datasets from arbitrary sensor setups from the carla simulator


Carla-simulator defines its coordinate frame as LEFT-HANDED:

+ X is forward
+ Y is right
+ Z is up

To define a sensor setup
proceed by creating a SimulationCfg object, and then adding new sensors to it
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
    
Usage:
0. define your sensor setup in this notebook or on your custom python script.
⋅⋅⋅Make sure to give your preferred path where the simulation setup will be generated.⋅⋅
⋅⋅⋅In all cases, everything that concerns the simulation setup will fall under that directory,⋅⋅
⋅⋅⋅in the folder 'simsetup'⋅⋅
⋅⋅⋅Every attribute, pose or blueprint follows the naming convention provided by carla.⋅⋅
⋅⋅⋅So to define your own custom sensor options, just referr to (https://carla.readthedocs.io/en/latest/python_api/)⋅⋅
1. start CarlaUE4.sh
2. python3 sensor_capture.py --help to see available options
⋅⋅⋅DO NOT FORGET TO GIVE THE PATH OF THE DIRECTORY WHERE THE GENERATED SIMSETUP IS LOCATED ⋅⋅
⋅⋅⋅(do not add 'simsetup' to the folder path, just give the directory path that contains it)⋅⋅
3. data will be stored in a folder named according to the chosen simulation parameters 
⋅⋅⋅(customizable by the command line args of sensor_capture.py)
