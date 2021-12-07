import numpy as np
import carla
import os

def callback_image_fn(image_data, custom_args):

    image_data.convert(carla.ColorConverter.Raw)

    data_dict = {'image': image_data}
    return data_dict

def save_image_data_fn(outdir, data_dict, frame_id):
    image = data_dict['image']


    image_path = os.path.join(outdir, str(frame_id))                
    image.save_to_disk(image_path)
