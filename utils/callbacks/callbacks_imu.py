import numpy as np
import os
from ..helpers import save_json

def callback_imu_fn(imu_data, custom_args):
    accelerometer = imu_data.accelerometer
    gyroscope = imu_data.gyroscope
    json_data_dict = {'accelerometer':{
                            'x':accelerometer.x,
                            'y':accelerometer.y,
                            'z':accelerometer.z
                            },

                'gyroscope':{
                            'x':gyroscope.x,
                            'y':gyroscope.y,
                            'z':gyroscope.z
                            },}
    return json_data_dict

def save_imu_fn(outdir, imu_data, frame_id):

    output_file_path = os.path.join(outdir, str(frame_id)+ '.json')
    save_json(output_file_path, imu_data)