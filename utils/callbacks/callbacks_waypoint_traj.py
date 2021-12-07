import numpy as np
import os
from ..helpers import save_json


def callback_waypoints_fn( lidar_data, custom_args):

    vehicle = custom_args['ego_veh']

    world = custom_args['world']
    map = custom_args['map']


    loc = vehicle.get_location()
    current_w = map.get_waypoint(loc)



    waypoint_loc = current_w.transform.location

    reflection_matrix = np.array([[0, 1, 0],
                            [0, 0 , -1],
                            [1, 0, 0]])

    data_dict = {   'frame_num' : lidar_data.frame,
                    'timestamp' : lidar_data.timestamp,
                    'waypoint_world': {'x':waypoint_loc.x, 
                                'y':waypoint_loc.y, 
                                'z':waypoint_loc.z}, 
                                'veh_to_world' : vehicle.get_transform().get_matrix() 
                } 
    

    
    return data_dict

def save_waypoints_data_fn(output_path, data, frame_id):
    output_file_path = os.path.join(output_path, str(frame_id)+ '.json')
    save_json(output_file_path, data)


