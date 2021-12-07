
import json
import io
import time
import numpy as np
try:
    to_unicode = unicode
except NameError:
    to_unicode = str

    
def save_json(file_path, dictionary):
     
        with io.open(file_path  , 'w', encoding='utf8') as outfile:
            str_ = json.dumps(dictionary,
                                          indent=4, 
                                          separators=(',', ': '), ensure_ascii=False)
            
            outfile.write(to_unicode(str_))

def get_camera_calibration_matrix(camera_sensor_options):
    CAM_WIDTH = float(camera_sensor_options['image_size_x'])
    CAM_HEIGHT = float(camera_sensor_options['image_size_y'])
    FOV = float(camera_sensor_options['fov'])

    calibration = np.identity(3)
    calibration[0, 2] = int(CAM_WIDTH) / 2.0
    calibration[1, 2] = int(CAM_HEIGHT) / 2.0
    calibration[0, 0] = calibration[1, 1] = int(CAM_WIDTH) / (2.0 * np.tan(FOV/2* 2*np.pi / 360.0) )
    return calibration    



class CustomTimer:
    def __init__(self):
        try:
            self.timer = time.perf_counter
        except AttributeError:
            self.timer = time.time

    def time(self):
        return self.timer()
