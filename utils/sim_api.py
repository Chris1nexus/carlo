
from utils.helpers import save_json
import os
import json

class  SenseBP:
    RGBCAMERA = 'sensor.camera.rgb' 
    GNSS = 'sensor.other.gnss'
    IMU = 'sensor.other.imu'
    LIDAR = 'sensor.lidar.ray_cast'
    RADAR = 'sensor.other.radar'
    SEM_LIDAR = 'sensor.lidar.ray_cast_semantic'
    DEPTH = 'sensor.camera.depth'
    INSTANCE_SEGMENTATION = 'sensor.camera.instance_segmentation'
    SEMANTIC_SEGMENTATION = 'sensor.camera.semantic_segmentation'
    #EVENTCAMERA = 'sensor.camera.dvs'


class SensorAPI:
    def __init__(self, sensor_label, sensor_bp):
        self.sensor_label, self.sensor_bp = sensor_label, sensor_bp
        self.options = None
        self.x,self.y,self.z,self.pitch,self.yaw,self.roll = None,None,None,None,None,None
    def set_pose(self, x=0,y=0,z=0,pitch=0.,yaw=0.,roll=0.):
        self.x,self.y,self.z,self.pitch,self.yaw,self.roll = x,y,z,pitch,yaw,roll

    def set_options(self, options):
        self.options = options
        
    def to_dict(self):
        
        pose_dict = {'x':self.x,
                     'y':self.y,
                     'z':self.z,
                     'pitch':self.pitch,
                     'yaw':self.yaw,
                     'roll':self.roll}
        data_dict = {'sensor_label':self.sensor_label,
                     'sensor_bp':self.sensor_bp,
                    'pose':pose_dict,
                    'options': self.options}

        
        return data_dict
    def write_to_file(self,dir_path):
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        
        
        sensor_label_dir_path = os.path.join(dir_path, self.sensor_label)
        if not os.path.exists(sensor_label_dir_path):
            os.makedirs(sensor_label_dir_path) 
        file_path = os.path.join(sensor_label_dir_path, self.sensor_bp + '.json')
        save_json(file_path, self.to_dict())
        
    def read_from_file(file_path):
        with open(file_path) as f:
            data_dict = json.load(f)
    
        sensor_label = data_dict['sensor_label']
        sensor_bp = data_dict['sensor_bp']
        
        pose_dict = data_dict['pose']
        sensor_options = data_dict['options']
        
        sensorapi = SensorAPI(sensor_label, sensor_bp)
        sensorapi.set_pose(**pose_dict)
        sensorapi.set_options(sensor_options)
        return sensorapi
    
    
class SimulationCfg:
    def __init__(self, vehicle_bp_name='model3', sync_sim_stepsize=0.02, file_setup_path='./'):
        self.vehicle_bp_name, self.sync_sim_stepsize, self.file_setup_path = vehicle_bp_name, sync_sim_stepsize, file_setup_path
        self.sensors = []
        self.file_setup_path = file_setup_path
    def add_sensor(self, sensor_label, sensor_bp,
                   x=0.,y=0.,z=0.,pitch=0.,yaw=0.,roll=0.,
                   sensor_options={}):
        sensor = SensorAPI(sensor_label, sensor_bp)
        sensor.set_pose(x,y,z,pitch,yaw,roll)
        sensor.set_options(sensor_options)
        
        self.sensors.append(sensor)
        
    def write_to_file(self):
        root_dir_path = os.path.join(self.file_setup_path, 'simsetup')
        if not os.path.exists(root_dir_path):
            os.makedirs(root_dir_path)
            
        sensors_dir_path = os.path.join(root_dir_path, 'sensors')
        if not os.path.exists(sensors_dir_path):
            os.makedirs(sensors_dir_path)
            
        base_cfg_file_path = os.path.join(root_dir_path, 'config.json')
        base_cfg_dict = {'vehicle_bp': self.vehicle_bp_name, 
                         'sim_step': self.sync_sim_stepsize}
        
        save_json(base_cfg_file_path, base_cfg_dict) 
        
        for sensor in self.sensors:
            sensor.write_to_file(sensors_dir_path)

    def add_camera_setup(self, sensor_label, blueprint_names,
                       x=0.,y=0.,z=0.,pitch=0.,yaw=0.,roll=0.,
                       sensor_options={}):
        
        for bp_name in blueprint_names:
            self.add_sensor(sensor_label, bp_name,
                       x=x,y=y,z=z,pitch=pitch,yaw=yaw,roll=roll,
                       sensor_options=sensor_options)
