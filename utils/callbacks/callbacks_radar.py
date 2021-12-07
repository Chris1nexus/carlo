import numpy as np
import os
from ..helpers import save_json

def callback_radar_fn(radar_data, custom_args):
    points = np.frombuffer(radar_data.raw_data, dtype=np.dtype('f4'))
    points = np.reshape(points, (len(radar_data), 4))
    json_data_dict = {'points':points.tolist()}
    return json_data_dict

def save_radar_fn(outdir, radar_data, frame_id):

    output_file_path = os.path.join(outdir, str(frame_id)+ '.json')
    save_json(output_file_path, imu_data)
