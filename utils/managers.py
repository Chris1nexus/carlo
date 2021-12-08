import os
import carla

class SensorManager:

    def __init__(self, world, 
                     sensor_bp_name, sensor_options, 
                     transform, callback_fn, save_data_fn, custom_args, 
                     attach_to=None,
                      outdir='output'):
        
        if not os.path.exists(outdir):
            os.makedirs(outdir)

        self.outdir = outdir


        '''
            a function that takes as params ( carla_sensor_measurement, user_defined_custom_args )
            
            ## def: defines how to process data received from sensor and 
                    returns the data 
        '''
        self.callback_fn = callback_fn

        '''
            a function that takes as params (output_path, data_stored_with_callback_fn)
            and defines how to save it to a file
        '''
        self.save_data_fn = save_data_fn
        '''
            user defined arguments that are passed as a dictionary to callback_fn 

            ## def: defines how to save the data processed in callback_fn 
        '''
        self.custom_args = custom_args

        self.data = None

        self.sensor_bp_name = sensor_bp_name
        self.sensor_options = sensor_options
        self.transform = transform
        self.attach_to = attach_to
        self.sensor = self.__init_sensor(world, sensor_options, transform, attach_to)
    

    def __init_sensor(self, world, sensor_options, transform, attach_to):
        sensor_bp = world.get_blueprint_library().find(self.sensor_bp_name)
        

        for k,v in sensor_options.items():
            sensor_bp.set_attribute(k,v)

        sensor = world.spawn_actor(sensor_bp,  transform, attach_to=attach_to,
                    attachment_type=carla.AttachmentType.Rigid)



        sensor.listen(lambda image: self.on_received_sensor_data(image) )

        return sensor
    def on_received_sensor_data(self, image):
        data = self.callback_fn(image, self.custom_args)
        self.store_data(data)

    def store_data(self, data):
        self.data = data

    def save_data(self, frame_id):
        if self.data is not None:
            self.save_data_fn(self.outdir, self.data, frame_id)
            self.data = None

    def has_new_data(self):
        return self.data is not None
    def render(self):

        pass
    def destroy(self):
        self.sensor.destroy()



class DetectionSystem:


    def __init__(self, world,   vehicle, 
                                            sensor_managers_list = None,

                                            ):

        self.world = world

        self.ego_vehicle = vehicle

        self.sensor_managers_list  = sensor_managers_list
        




    def save_data(self, frame_id):


        all_data_available = True
        for sensor_manager in self.sensor_managers_list:
            all_data_available = all_data_available and sensor_manager.has_new_data()

        if all_data_available:
            for sensor_manager in self.sensor_managers_list:
                sensor_manager.save_data(frame_id)

                

    def destroy(self):
        
        for sensor_manager in self.sensor_managers_list:
            sensor_manager.destroy()


