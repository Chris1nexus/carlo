import os

def callback_lidar_fn(lidar_data, custom_args):
    return lidar_data

def save_lidar_fn(outdir, lidar_frame, frame_id):
    lidar_frame.save_to_disk(os.path.join(outdir, str(frame_id)) )
