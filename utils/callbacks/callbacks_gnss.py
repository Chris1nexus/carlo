import numpy as np
import os
from ..helpers import save_json
import carla

def callback_gnss_fn(gnss_data , custom_args):

    vehicle = custom_args['ego_veh']
    world = custom_args['world']

    veh_to_world = vehicle.get_transform().get_matrix() 
    reflection_matrix = np.array([[0, 1, 0],
                                [0, 0 , -1],
                                [1, 0, 0]])



    json_data_dict = {  'veh_to_world':veh_to_world,
                        'gnss_to_world': gnss_data.transform.get_matrix(),
                        'altitude':gnss_data.altitude,
                        'latitude':gnss_data.latitude,
                        'longitude':gnss_data.longitude,
                            'unreal_to_cam_reflection': reflection_matrix.tolist(),
                      }


    return json_data_dict
        








def save_gnss_data_fn(outdir, gnss_data_dict, frame_id):
   
    dir_path = outdir
    if not os.path.exists(dir_path):
            os.makedirs(dir_path)
    file_path = os.path.join(dir_path, f"{frame_id}.json")
    save_json(file_path, gnss_data_dict)