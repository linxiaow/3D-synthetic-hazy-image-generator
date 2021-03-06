import bpy
from random import uniform
from mathutils import *
from math import *
import os

'''
Blender code for AQI modeling
Require: your working directory
Output: hazed image and depth map
Output: camera coordinate via console

Edited by: Linxiao and Zhizhuo
'''

# Global variable save directory
SAVE_DIRECTORY = r'C:\Users\34654\Documents\UMich\Academy\research\Air_Quality\3D_Blender\smoke_cube\img' 

def delete_all():
    '''
    Delete current objects
    '''
    # select mesh and cameras
    candidate_list = [item.name for item in bpy.data.objects if item.type == "MESH" or item.type == 'CAMERA']

    # select objects in candidate list
    for object_name in candidate_list:
      bpy.data.objects[object_name].select = True

    # remove all selected.
    bpy.ops.object.delete()

    # remove the meshes, they have no users anymore.
    for item in bpy.data.meshes:
      bpy.data.meshes.remove(item)
    
    
def edit_node(file, num_specify=-1):
    '''
    Edit each cube and specify the parameter
    '''
    # Save time with variable names.
    # Set active object to variable
    activeObject = bpy.context.active_object
    # Set new material to variable
    mat = bpy.data.materials.new(name="Material") 
    # Add the material to the object
    activeObject.data.materials.append(mat) 
    mat = bpy.context.object.active_material
    mat.use_nodes = True
    material_output = mat.node_tree.nodes['Material Output']
    # Delete every node but 'Material Output'
    for k in mat.node_tree.nodes.keys():
        if k != 'Material Output':
            mat.node_tree.nodes.remove(mat.node_tree.nodes[k])
    
    # Always use material_output as reference.
    x,y = material_output.location

    # Add all nodes
    volume_scatter = mat.node_tree.nodes.new('ShaderNodeVolumeScatter') # volume scatter
    volume_scatter.location = (x - 450, y)

    volume_abs = mat.node_tree.nodes.new('ShaderNodeVolumeAbsorption') # volume absorption
    volume_abs.location = (x - 450, y - 150)

    add_shader = mat.node_tree.nodes.new('ShaderNodeAddShader') # add shader
    add_shader.location = (x - 300, y)
  
    # Link nodes together.
    # mat.node_tree.links.new(add_shader.outputs['Shader'], material_output.inputs['Volume'])
    # mat.node_tree.links.new(volume_scatter.outputs[0], add_shader.inputs[0])
    mat.node_tree.links.new(volume_scatter.outputs[0], material_output.inputs['Volume'])
    # mat.node_tree.links.new(volume_abs.outputs[0], add_shader.inputs[1])

    # change the value of volume scatter and absorption
    # volume_abs.inputs[1].default_value = 0 # uniform(0.01, 0.02)
    picked_num = uniform(0.1, 0.3)
    if num_specify != -1:
        picked_num = num_specify
    volume_scatter.inputs[1].default_value = picked_num
    file.write("%f " % picked_num)
    
def camera_look_at(obj, target, roll=0):
    """
    Rotate obj to look at target

    :arg obj: the object to be rotated. Usually the camera
    :arg target: the location (3-tuple or Vector) to be looked at
    :arg roll: The angle of rotation about the axis from obj to target in radians. 

    Based on: https://blender.stackexchange.com/a/5220/12947 (ideasman42)     
    """
    #if not isinstance(target, mathutils.Vector):
    if not isinstance(target, Vector):
        # target = mathutils.Vector(target)
        target = Vector(target)
    loc = obj.location
    # direction points from the object to the target
    direction = target - loc

    quat = direction.to_track_quat('-Z', 'Y')

    # /usr/share/blender/scripts/addons/add_advanced_objects_menu/arrange_on_curve.py
    quat = quat.to_matrix().to_4x4()
    # rollMatrix = mathutils.Matrix.Rotation(roll, 4, 'Z')
    rollMatrix = Matrix.Rotation(roll, 4, 'Z')

    # remember the current location, since assigning to obj.matrix_world changes it
    loc = loc.to_tuple()
    obj.matrix_world = quat * rollMatrix
    obj.location = loc

def generate_camera_view(pathname):
    '''
    Generate camera rendered views within specified pathname
    '''
    scene = bpy.context.scene
    #scene.render.layers['RenderLayer'].use_pass_mist = False
    #scene.render.layers['RenderLayer'].use_pass_normal = True
    #scene.render.layers['RenderLayer'].use_pass_combined = True
    #scene.render.layers['RenderLayer'].use_pass_material_index = True
    tree = bpy.context.scene.node_tree
    links = tree.links
    rl = tree.nodes.new(type="CompositorNodeRLayers")
    composite = tree.nodes.new(type = "CompositorNodeComposite")
    links.new(rl.outputs['Image'],composite.inputs['Image'])
    for ob in bpy.context.scene.objects:
        if ob.type == 'CAMERA':
            bpy.context.scene.camera = ob
            print('Set camera %s' % ob.name )
            file = os.path.join(pathname, ob.name )
            bpy.context.scene.render.filepath = file
            bpy.ops.render.render(write_still=True)


def align_camera(loc=(0, 0, 0)):
    '''
    Adjust each camera and make them point
    at the center
    '''
    camera_path = os.path.join(SAVE_DIRECTORY, 'camera')
    if not os.path.exists(camera_path):
        os.makedirs(camera_path)
              
    filepath = os.path.join(camera_path, 'camera.txt')
    f = open(filepath, "w+")
    # f.write("%d\n%d\n%d\n" % (dim[0], dim[1], dim[2]))
    f.write("Camera look at\n %f %f %f\n" % (loc[0], loc[1], loc[2]))
    cam_list = [item.name for item in bpy.data.objects if item.type == "CAMERA"]
    for name in cam_list: 
        cam = bpy.data.objects[name]
        f.write("Camera name: %s\n" % (cam))
        f.write("Camera locate at\n %f %f %f\n" % (cam.location[0], cam.location[1], cam.location[2]))
        camera_look_at(cam, loc)
    f.close()
       
       
def create_camera(radius, z_axis, num = 2, angle = 45):
    '''
    this function is used to create num cameras with 
    angle to each other 
    '''
    trans = radians(angle)
    
    # print(trans)
    for i in range(num):
        #i = num
        x = radius * sin(i * trans)
        y = radius * cos(i * trans)
        # print(x)
        # print(y)
        bpy.ops.object.camera_add(view_align=False, location=[x,y, z_axis])
        
    # f.close() 

def create_scene(dim=[3, 3, 3], rad=2, scene_mode="close"):
    x_loc = 0
    y_loc = 0 
    if scene_mode == "moderate":
        y_loc = rad
    elif scene_mode == "close":
        y_loc = rad + (dim[1]//2 - 1) * 2 * rad
    elif scene_mode == "far":
        # far
        y_loc = rad - (dim[1]//2) * 2 * rad
    
    if scene_mode != "dense":
        for x_step in range(-1 * dim[0] // 2, dim[0] // 2):
            if x_step % 2 == 1 or x_step % 2 == 0:
                x_loc = rad + x_step * 2 * rad
                bpy.ops.mesh.primitive_cylinder_add(radius= rad * dim[0] * 0.2, depth=rad * dim[2], location=(x_loc,y_loc,0.5 * rad * dim[2]))
                activeObject = bpy.context.active_object
                mat = bpy.data.materials.new(name="Building") #set new material to variable
                activeObject.data.materials.append(mat) #add the material to the object
                bpy.context.object.active_material.diffuse_color = (uniform(0, 1), uniform(0, 1), uniform(0, 1)) #change color    
    
    else:
        # dense mode               
        for y_step in range(-1 * dim[1] // 2, dim[1] // 2):
            for x_step in range(-1 * dim[0] // 2, dim[0] // 2):
                x_loc = rad + x_step * 2 * rad
                y_loc = rad + y_step * 2 * rad
                bpy.ops.mesh.primitive_cylinder_add(radius= rad * dim[0] * 0.2, depth=rad * dim[2], location=(x_loc,y_loc,rad * dim[2]))
                activeObject = bpy.context.active_object
                mat = bpy.data.materials.new(name="Building") #set new material to variable
                activeObject.data.materials.append(mat) #add the material to the object
                bpy.context.object.active_material.diffuse_color = (uniform(0, 1), uniform(0, 1), uniform(0, 1)) #change color    
        
def main():
    '''
    Create pollution cubes and general actions
    '''
    delete_all()
    bpy.context.scene.render.engine = "CYCLES" # use cycle render
    
    
    #####################################################
    # tunable parameters
    input_file_mode = True
    filename = "input_file\same_0.05.txt"
    
    scene_mode = "moderate" # scene_mode is close, moderate, far, or dense
    
    '''
    The first three lines specify x dim, y dim and z dim
    and the following lines specifies each x
    '''
    save_directory = SAVE_DIRECTORY
    # half length for each cube
    rad = 2
    r = rad - 0.0001 
    # will create dim[0] * dim[1] * dim[2] of cubes
    dim = [5, 5, 5] 
    ###################################################
    # no need to modify when use
    inFile = None
    input_list = []
    if input_file_mode:
        f_path = os.path.join(save_directory, filename)
        # print(f_path)
        inFile = open(f_path , 'r')
        input_list = inFile.readlines()
        # print(input_list)
        dim[0] = int(input_list.pop(0))
        dim[1] = int(input_list.pop(0))
        dim[2] = int(input_list.pop(0))
        # print(dim)
        inFile.close()
    ####################################################
    
    # number of image set to create
    num_image_set = 1 
    # add 2 cameras with 45 degree of distance to each other
    create_camera(rad * 2.3 * dim[0], rad * dim[0], 2, degrees(45)) 
    # make all camera look at (0, 0, dim[2] // 2)
    align_camera((0, 0,  rad * dim[0] * 0.4))  
    # end of tunable parameter
    ####################################################
    x = rad
    y = rad
    z = rad # starting point
    
    ### USE SKY
    bpy.context.scene.world.use_sky_paper = True
    
    bpy.ops.mesh.primitive_plane_add(radius=rad*dim[0]*1.5, location=(0,0,-0.001))  # ground
    activeObject = bpy.context.active_object
    mat = bpy.data.materials.new(name="Ground") #set new material to variable
    activeObject.data.materials.append(mat) #add the material to the object
    bpy.context.object.active_material.diffuse_color = (.2, .2, .2) #change color
    
    
    for i in range(num_image_set):
        
        dir = "image_set_" + scene_mode + str(i)
        file_name = 'label' + str(i) +'.txt'
        pathname = os.path.join(save_directory, dir)
        # print(pathname)
        if not os.path.exists(pathname):
            os.makedirs(pathname)
              
        filepath = os.path.join(pathname, file_name)
        f = open(filepath, "w+")
        f.write("%d\n%d\n%d\n" % (dim[0], dim[1], dim[2]))
        # create cubes
        if input_file_mode: # if specify input
            iter = 0;
            for z_step in range(0, dim[2]):
                # f.write("Layer %d:\n" % z_step)
                for y_step in range(-1 * dim[1] // 2, dim[1] // 2):
                    line = input_list[iter]
                    iter += 1
                    num_list = line.split(" ")
                    for x_step, num in zip(range(-1 * dim[0] // 2, dim[0] // 2), num_list):
                        # print(num)
                        add_x = x_step*rad*2
                        add_y = y_step*rad*2
                        add_z = z_step*rad*2
                        loc = (x+add_x,y+add_y,z+add_z)
                        bpy.ops.mesh.primitive_cube_add(radius=r, location=loc)
                        edit_node(f, num_specify=float(num))
                    f.write("\n")         
        else:
            for z_step in range(0, dim[2]):
                # f.write("Layer %d:\n" % z_step)
                for y_step in range(-1 * dim[1] // 2, dim[1] // 2):
                    for x_step in range(-1 * dim[0] // 2, dim[0] // 2):
                        add_x = x_step*rad*2
                        add_y = y_step*rad*2
                        add_z = z_step*rad*2
                        loc = (x+add_x,y+add_y,z+add_z)
                        bpy.ops.mesh.primitive_cube_add(radius=r, location=loc)
                        edit_node(f)
                    f.write("\n")
                
        f.close()
        
        '''
        Generate Depth Map with Buildings
        '''
        # create buildings
        create_scene(dim=dim, rad=rad, scene_mode=scene_mode)
        
        # add light
        scene = bpy.context.scene
        lamp_data = bpy.data.lamps.new(name="New Lamp", type='SUN')
        lamp_object = bpy.data.objects.new(name="New Lamp", object_data=lamp_data)
        scene.objects.link(lamp_object)
        lamp_object.location = (10.0, 10.0, 10.0)
        lamp_object.select = True
        scene.objects.active = lamp_object
        lamp = scene.objects.active
        lamp.data.use_nodes = True
        lamp.data.node_tree.nodes['Emission'].inputs['Strength'].default_value = 5
        
        bpy.context.scene.cycles.transparent_max_bounces = 32 # 8 #64
        bpy.context.scene.cycles.max_bounces = 12 # 4 #25
        
        # Generate normal views 
        generate_camera_view(pathname)
        
        
        ##
        # EXPERIMENTAL
        bpy.context.scene.use_nodes = True
        tree = bpy.context.scene.node_tree
        links = tree.links
        
        scene = bpy.context.scene
        scene.render.use_multiview = True
        scene.render.views_format = 'STEREO_3D'
        
        rl = tree.nodes.new(type="CompositorNodeRLayers")
        composite = tree.nodes.new(type = "CompositorNodeComposite")
        composite.location = 200,0

        scene = bpy.context.scene

        #setup the depthmap calculation using blender's mist function:
        scene.render.layers['RenderLayer'].use_pass_mist = True
        #the depthmap can be calculated as the distance between objects and camera ('LINEAR'), 
        #or square/inverse square of the distance ('QUADRATIC'/'INVERSEQUADRATIC'):
        scene.world.mist_settings.falloff = 'LINEAR'
        #minimum depth:
        scene.world.mist_settings.intensity = 0.0
        #maximum depth (can be changed depending on the scene geometry to normalize the depth 
        #map whatever the camera orientation and position is):
        dist = 100
        scene.world.mist_settings.depth = dist
        print(dist)
        #ouput the depthmap:
        links.new(rl.outputs['Mist'],composite.inputs['Image'])

        scene.render.use_multiview = False
        dir2 = "depth_set_" + scene_mode + str(i)
        
        depthpath = os.path.join(save_directory, dir2)
        for ob in bpy.context.scene.objects:
            if ob.type == 'CAMERA':
                bpy.context.scene.camera = ob
                file = os.path.join(depthpath, ob.name )
                bpy.context.scene.render.filepath = file
                bpy.ops.render.render( write_still=True ) 
     
    
if __name__ == '__main__':
    main()