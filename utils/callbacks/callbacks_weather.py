import numpy as np

import os
from ..helpers import save_json
def callback_weather_fn(sensor_data, custom_args):
    ## note that in this function, sensor data comes from the 
    ## 'weather' custom arg
    ## the sensor is used just to trigger the callback at the correct timestamp
    weather = custom_args['weather']
    world = custom_args['world']


    data_dict = weather.to_json()
    return data_dict

    
def save_weather_data_fn(outdir, data_dict, frame_id):
    output_file_path = os.path.join(outdir, str(frame_id)+ '.json')
    save_json(output_file_path, data_dict)
    