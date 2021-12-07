import numpy as np
import os
from ..helpers import save_json
import carla
import tarfile, io
import json
try:
    to_unicode = unicode
except NameError:
    to_unicode = str
import time

def callback_tracker_fn(lidar_scan , custom_args):


    world = custom_args['world']
    env_objs_list = custom_args['env_objs']


    world_elements = get_world_elements_data( world , env_objs_list)

    return world_elements
        






def get_world_elements_data(world, env_objs_list):


    def carla_element_as_dict(id, extent, bbox_to_world, 
                                semantic_tag, elem_carla_type):
 
        element_dict = {'id' : id,
                        'extent': {'x':extent.x,
                                    'y':extent.y,
                                    'z':extent.z},
                        'bbox_to_world' : bbox_to_world.tolist(),
                        'semantic_tag': semantic_tag,
                        'elem_carla_type': elem_carla_type,
                    }  
        return element_dict

    world_elements = []


    for item in world.get_actors():
            if len(item.semantic_tags) == 0:
                continue


            bb_to_item_tf = carla.Transform(item.bounding_box.location)
            bb_to_item_mtx = np.array(bb_to_item_tf.get_matrix()) 
            item_to_world = np.array(item.get_transform().get_matrix()) 
            bbox_to_world_mtx = item_to_world.dot(bb_to_item_mtx) 
            elem_dict = carla_element_as_dict(item.id, item.bounding_box.extent, bbox_to_world_mtx, item.semantic_tags, 'actor')

            world_elements.append(elem_dict)






    for env_obj in env_objs_list:
            bb_transform = carla.Transform(env_obj.bounding_box.location,env_obj.bounding_box.rotation)
            bb_matrix = np.array(bb_transform.get_matrix())
            bbox_to_world_mtx = np.array(bb_transform.get_matrix())


            elem_dict = carla_element_as_dict(env_obj.id, env_obj.bounding_box.extent, bbox_to_world_mtx, [int(env_obj.type)], 'env_obj')

            world_elements.append(elem_dict)

    return world_elements










    

def save_tracker_data_fn(outdir, world_elements, frame_id):
   
    dir_path = os.path.join(outdir, 'object_data')
    if not os.path.exists(dir_path):
            os.makedirs(dir_path)
    file_path = os.path.join(dir_path, f"{frame_id}.json")
    #save_json(file_path, world_elements)


    

    tarinfo = tarfile.TarInfo(name=f"{frame_id}.json")
    


    with tarfile.open(f"{file_path}.tar.bz2", "w:bz2") as outfile:
            str_ = json.dumps(world_elements,
                                          indent=4, 
                                          separators=(',', ': '), ensure_ascii=False)

            unicode_str = to_unicode(str_)
            tarinfo.size = len(unicode_str)

            outfile.addfile(tarinfo, io.BytesIO(unicode_str.encode('utf8')))