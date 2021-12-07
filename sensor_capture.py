#!/usr/bin/env python

# Copyright (c) 2020 Computer Vision Center (CVC) at the Universitat Autonoma de
# Barcelona (UAB).
#
# This work is licensed under the terms of the MIT license.
# For a copy, see <https://opensource.org/licenses/MIT>.

"""
Script that render multiple sensors in the same pygame window

By default, it renders four cameras, one LiDAR and one Semantic LiDAR.
It can easily be configure for any different number of sensors. 
To do that, check lines 290-308.
"""

import glob
import os
import sys
import pandas as pd
import threading
import cv2
try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla
import argparse
import random
import time
import numpy as np
import threading
import cv2
import time


import json

from spawn_utils import spawn_npc
from utils.sim_api import SensorAPI, SimulationCfg, SenseBP
from utils.callbacks.callbacks_tracker import callback_tracker_fn, save_tracker_data_fn
from utils.callbacks.callbacks_camera import callback_image_fn, save_image_data_fn
from utils.callbacks.callbacks_imu import callback_imu_fn, save_imu_fn
from utils.callbacks.callbacks_lidar import callback_lidar_fn, save_lidar_fn
from utils.callbacks.callbacks_waypoint_traj import callback_waypoints_fn, save_waypoints_data_fn
from utils.callbacks.callbacks_weather import callback_weather_fn, save_weather_data_fn
from utils.callbacks.callbacks_gnss import callback_gnss_fn, save_gnss_data_fn

from utils.helpers import get_camera_calibration_matrix
from utils.managers import SensorManager, DetectionSystem
from utils.helpers import save_json, get_camera_calibration_matrix, CustomTimer

from utils.weather import Weather, Sun, Storm

def run_simulation(args, client):
    """This function performed one test run using the args parameters
    and connecting to the carla client passed.
    """

    ego_vehicle = None
    vehicle_list = []
    timer = CustomTimer()


    SIMULATE_PHYSICS = True
    try:
        cfg_dir_path = args.cfg_dirpath
        cfg_file_path = os.path.join(cfg_dir_path, 'config.json')
        with open(cfg_file_path) as f:
            cfg_data_dict = json.load(f)


        # Getting the world and
        #cli
        world = client.get_world()
        #world_map = "Town10HD_Opt"
        world = client.load_world(args.world_map)
        original_settings = world.get_settings()

        VEHICLE_MODEL_BLUEPRINT = cfg_data_dict['vehicle_bp'] 
        FIXED_DELTA_SECONDS = cfg_data_dict['sim_step']

        
            
        traffic_manager = client.get_trafficmanager(args.tm_port)
        settings = world.get_settings()
        traffic_manager.set_synchronous_mode(True)
        settings.synchronous_mode = True
        settings.fixed_delta_seconds = FIXED_DELTA_SECONDS

        if SIMULATE_PHYSICS:
                settings.substepping = True
                settings.max_substep_delta_time = FIXED_DELTA_SECONDS/10.
                settings.max_substeps = 16
        world.apply_settings(settings)


        bp = world.get_blueprint_library().filter( VEHICLE_MODEL_BLUEPRINT   )[0]
        ego_vehicle = world.spawn_actor(bp, random.choice(world.get_map().get_spawn_points()))
        vehicle_list.append(ego_vehicle)
        ego_vehicle.set_autopilot(True, traffic_manager.get_port())
        ego_vehicle.set_simulate_physics(SIMULATE_PHYSICS)



        vehicles_list, walkers_list, all_actors, all_id = spawn_npc(client, traffic_manager, sync=True, hybrid_phys=True,
                filterv="vehicle.*", filterw='walker.pedestrian.*',
                safe_mode=True,
                car_lights_on = True,
                number_of_vehicles=args.number_of_vehicles,
                number_of_walkers=args.number_of_walkers, 
                simulate_physics=SIMULATE_PHYSICS)      


        ################################### FIND VALID OBJECTS TO TRACK
        valid_tags = [carla.libcarla.CityObjectLabel.Other, carla.libcarla.CityObjectLabel.NONE, carla.libcarla.CityObjectLabel.Pedestrians,
            carla.libcarla.CityObjectLabel.Buildings, 

            carla.libcarla.CityObjectLabel.Vegetation,carla.libcarla.CityObjectLabel.Sky, carla.libcarla.CityObjectLabel.GuardRail, 

            carla.libcarla.CityObjectLabel.Fences, carla.libcarla.CityObjectLabel.Other, carla.libcarla.CityObjectLabel.Poles, carla.libcarla.CityObjectLabel.RoadLines, 
            carla.libcarla.CityObjectLabel.Roads, carla.libcarla.CityObjectLabel.Sidewalks,  carla.libcarla.CityObjectLabel.Vehicles, 
            carla.libcarla.CityObjectLabel.Walls, carla.libcarla.CityObjectLabel.TrafficSigns, carla.libcarla.CityObjectLabel.Ground, carla.libcarla.CityObjectLabel.Bridge,
             carla.libcarla.CityObjectLabel.RailTrack, carla.libcarla.CityObjectLabel.TrafficLight, carla.libcarla.CityObjectLabel.Static, carla.libcarla.CityObjectLabel.Dynamic,
              carla.libcarla.CityObjectLabel.Water, carla.libcarla.CityObjectLabel.Terrain]

        env_obj_list = []
        for tag in set(valid_tags):
            env_obj_list.extend(world.get_environment_objects(tag))
        ################################### END FIND VALID OBJECTS TO TRACK


        ########################## INIT WEATHER
        weather = Weather(world.get_weather())




        dataset_dirname = args.world_map + f"_dataset__n_{args.number_of_vehicles}__w_{args.number_of_walkers}__s_{args.speed}"
        top_level_dir = os.path.join(args.dest_path, dataset_dirname)
        sensor_data_dir = 'sensor_data'





        

        callback_mapper = {SenseBP.RGBCAMERA: {'callback_fn':callback_image_fn,
                            'save_data_fn':save_image_data_fn},
         SenseBP.GNSS :{'callback_fn':callback_gnss_fn, 
                            'save_data_fn':save_gnss_data_fn},
         SenseBP.IMU :{'callback_fn':callback_imu_fn,
                            'save_data_fn':save_imu_fn},
         SenseBP.LIDAR :{'callback_fn':callback_lidar_fn,
                            'save_data_fn':save_lidar_fn},
         SenseBP.RADAR :{'callback_fn':callback_image_fn,
                            'save_data_fn':save_image_data_fn},
         SenseBP.SEM_LIDAR :{'callback_fn':callback_lidar_fn,
                            'save_data_fn':save_lidar_fn},
         SenseBP.DEPTH:{'callback_fn':callback_image_fn,
                            'save_data_fn':save_image_data_fn},
         SenseBP.INSTANCE_SEGMENTATION  :{'callback_fn':callback_image_fn,
                            'save_data_fn':save_image_data_fn},             
        SenseBP.SEMANTIC_SEGMENTATION  :{'callback_fn':callback_image_fn,
                            'save_data_fn':save_image_data_fn},               
                            }

        custom_args = {'ego_veh': ego_vehicle,
                'world': world,
                'map': world.get_map(),
                'weather': weather,
                'env_objs':env_obj_list,
                }

        sensor_manager_list = []
        sensor_dir_path = os.path.join(cfg_dir_path, 'sensors')
        calibration_data_dir_path = os.path.join(top_level_dir, 'calibration')
        if not os.path.exists(calibration_data_dir_path):
            os.makedirs(calibration_data_dir_path)
        reflection_matrix = np.array([[0, 1, 0],
                                [0, 0 , -1],
                                [1, 0, 0]])



        for sensor_label_filename in os.listdir(sensor_dir_path):
            sensor_label_dir_path = os.path.join(sensor_dir_path, sensor_label_filename)

            for sensor_bp_filename in os.listdir(sensor_label_dir_path):
                sensor_file_path = os.path.join(sensor_label_dir_path, sensor_bp_filename)

                sensor = SensorAPI.read_from_file(sensor_file_path)

                sensor_manager = SensorManager(world, 
                             sensor_bp_name=sensor.sensor_bp, sensor_options=sensor.options, 
                             transform=carla.Transform(carla.Location(x=sensor.x,y=sensor.y,z=sensor.z), carla.Rotation(pitch=sensor.pitch,yaw=sensor.yaw,roll=sensor.roll)), 
                             callback_fn=callback_mapper[sensor.sensor_bp]['callback_fn'], 
                             save_data_fn=callback_mapper[sensor.sensor_bp]['save_data_fn'], 
                             custom_args=custom_args, 
                             attach_to=ego_vehicle,
                              outdir= os.path.join(top_level_dir, sensor_data_dir, sensor.sensor_label, sensor.sensor_bp.split('.')[-1] ))
                sensor_manager_list.append(sensor_manager)



                calib_data_dict = {'label':sensor.sensor_label,
                            'sensor_to_veh_tf':sensor_manager.transform.get_matrix(), 
                            'unreal_to_sensor_reflection':reflection_matrix.tolist()  }
                sensor_category = sensor.sensor_bp.split('.')[-2]
                if sensor_category == 'camera':
                    calib_data_dict['calib_mtx'] = get_camera_calibration_matrix(sensor.options).tolist()
                
                curr_sensor_calib_file_path = os.path.join(calibration_data_dir_path, 
                                                    sensor.sensor_label + '.json' ) 
                save_json(curr_sensor_calib_file_path, calib_data_dict)









        ######################## WORLD OBJECT TRACKER ###########################################
        tracker_manager = SensorManager(world, 
                             sensor_bp_name='sensor.other.imu',
                            sensor_options= {
                                        'sensor_tick':str(FIXED_DELTA_SECONDS)
                                        }, 
                             transform=ego_vehicle.get_transform(), 
                             callback_fn=callback_tracker_fn, 
                             save_data_fn=save_tracker_data_fn, 
                             custom_args=custom_args, 
                             attach_to=ego_vehicle,
                              outdir=os.path.join(top_level_dir,  sensor_data_dir, 'object_tracker') )

        ############################ WAYPOINTS ###########
        waypoints_manager = SensorManager(world, 
                             sensor_bp_name='sensor.other.imu',
                            sensor_options= {
                                        'sensor_tick':str(FIXED_DELTA_SECONDS)
                                        }, 
                             transform=ego_vehicle.get_transform(), 
                             callback_fn=callback_waypoints_fn, 
                             save_data_fn=save_waypoints_data_fn, 
                             custom_args=custom_args, 
                             attach_to=ego_vehicle,
                              outdir=os.path.join(top_level_dir,  sensor_data_dir, 'waypoint_trajectory', 'waypoint_trajectory_data' ))

        ########################### WEATHER SENSOR ################
        weather_manager = SensorManager(world,
                             sensor_bp_name='sensor.other.imu',
                            sensor_options= {
                                        'sensor_tick':str(FIXED_DELTA_SECONDS),
                                        }, 
                             transform=ego_vehicle.get_transform(), 
                             callback_fn=callback_weather_fn, 
                             save_data_fn=save_weather_data_fn, 
                             custom_args=custom_args, 
                             attach_to=ego_vehicle,
                              outdir=os.path.join(top_level_dir,  sensor_data_dir,'weather', 'weather_data' ))
        sensor_manager_list.append(tracker_manager)
        sensor_manager_list.append(waypoints_manager)
        sensor_manager_list.append(weather_manager)



        det_sys = DetectionSystem(world, ego_vehicle, 
                                            sensor_managers_list = sensor_manager_list,
                                            )

        #################################### METEO PARAMETERS
        speed_factor = args.speed
        update_freq = 0.1 / speed_factor
        elapsed_time = 0
        #################################### END METEO PARAMETERS


        #Simulation loop
        call_exit = False
        time_init_sim = timer.time()
        frame_id = 0

        for _ in range(2):
            print("#"*53)
        print("#### Simulation started: press 'Ctrl+C' to quit. ####")
        for _ in range(2):
            print("#"*53)
   
        while True:
                
                # Carla Tick
                world.tick()


     
                # the first frames include the setup of the carla world, so ignore this initial 'burn in period'
                # by skipping these frames
                if frame_id >= 50:
                    det_sys.save_data(frame_id)

                frame_id +=1


                elapsed_time += FIXED_DELTA_SECONDS
                if elapsed_time > update_freq:
                    weather.tick(speed_factor * elapsed_time)
                    world.set_weather(weather.weather)

                    elapsed_time = 0.0


                if call_exit:
                    break
            

    finally:


        client.apply_batch([carla.command.DestroyActor(x) for x in vehicle_list])


        print('\ndestroying %d vehicles' % len(vehicles_list))
        client.apply_batch([carla.command.DestroyActor(x) for x in vehicles_list])

        # stop walker controllers (list is [controller, actor, controller, actor ...])
        for i in range(0, len(all_id), 2):
            all_actors[i].stop()

        print('\ndestroying %d walkers' % len(walkers_list))
        client.apply_batch([carla.command.DestroyActor(x) for x in all_id])

        time.sleep(0.5)

        world.apply_settings(original_settings)



def main():
    argparser = argparse.ArgumentParser(
        description='CARLA Sensor tutorial')

    argparser.add_argument(
        '--dest-path',

        default='./',
        help='Path to the directory in which the dataset will be placed (default: ./)')
    argparser.add_argument(
        '--cfg-dirpath',

        default='./simsetup',
        help='Path to the directory that contains the simulation setup, generated by the simulation cfg script (default: ./simsetup)')
    argparser.add_argument(
        '--host',
        metavar='H',
        default='127.0.0.1',
        help='IP of the host server (default: 127.0.0.1)')
    argparser.add_argument(
        '-p', '--port',
        metavar='P',
        default=2000,
        type=int,
        help='TCP port to listen to (default: 2000)')
    argparser.add_argument(
        '-tp', '--tm-port',
        metavar='P',
        default=8000,
        type=int,
        help='traffica manager TCP port to listen to (default: 8000)')


    argparser.add_argument(
        '--world-map',
        default='Town04',
        help='default loaded world map (default: Town04)')

    argparser.add_argument(
        '-n', '--number-of-vehicles',
        metavar='N',
        default=10,
        type=int,
        help='number of vehicles (default: 10)')
    argparser.add_argument(
        '-w', '--number-of-walkers',
        metavar='W',
        default=50,
        type=int,
        help='number of walkers (default: 50)')
    argparser.add_argument(
        '-s', '--speed',
        metavar='FACTOR',
        default=1.0,
        type=float,
        help='rate at which the weather changes (default: 1.0)')
    args = argparser.parse_args()


    try:
        client = carla.Client(args.host, args.port)
        client.set_timeout(10)

        run_simulation(args, client)

    except KeyboardInterrupt:
        print('\nCancelled by user. Bye!')


if __name__ == '__main__':

    main()
