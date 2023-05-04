bl_info = {
    "name": "Splatoon Tools",
    "author": "Coconuts XXS",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Add > Mesh > Inkling",
    "description": "Create a procedural Splatoon character in few clicks.",
    "warning": "",
    "doc_url": "",
    "category": "Add Mesh",
}

import bpy
import os
import bmesh
from bpy.types import Operator
from bpy.props import FloatVectorProperty
from bpy_extras.object_utils import AddObjectHelper, object_data_add
from mathutils import Vector
from bpy_extras.object_utils import AddObjectHelper
from bpy.utils import resource_path
from pathlib import Path

USER = Path(resource_path('USER'))
ADDON = "Splatoon Tools"

srcPath = USER / "scripts" / "addons" / ADDON

def path_iterator(folder_path):
    for fp in os.listdir(folder_path):
        if fp.endswith( tuple( bpy.path.extensions_image ) ):
            yield fp

def import_weapon(armature=None, path="", file="", inkA=(0,0,0)):
    bpy.ops.object.select_all(action='DESELECT')
    
    bpy.ops.import_scene.fbx(filepath = path+file)
    
    obj = bpy.context.view_layer.objects.active
    
    # TRANSFORMING
    obj.scale = (1,1,1)
    
    #RIGING
    for child in obj.children:
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = child
        
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.remove_doubles(threshold=0.001, use_unselected=True, use_sharp_edge_from_normals=True)
        bpy.ops.object.editmode_toggle()
        
        bpy.ops.object.select_all(action='DESELECT')
        child.select_set(True)
        bpy.context.view_layer.objects.active = child
        
        # SHADING
        
        nodes = bpy.context.active_object.active_material.node_tree.nodes
        links = bpy.context.active_object.active_material.node_tree.links
        
        for node in nodes:
            nodes.remove(node)
        
        output = nodes.new(type="ShaderNodeOutputMaterial")
        bsdf = nodes.new(type="ShaderNodeBsdfPrincipled")
        links.new(bsdf.outputs[0], output.inputs[0])

        mix_node = None
        alb_node = None
        inka_color = (inkA[0], inkA[1], inkA[2], 1)
        
        for img_path in path_iterator( path ):
            if img_path.lower().startswith(bpy.context.active_object.active_material.name.lower()+"_"):
                full_path = os.path.join( path, img_path )
                
                bpy.ops.image.open(filepath = full_path)
                        
                img_node = nodes.new(type="ShaderNodeTexImage")
                img_node.image = bpy.data.images[img_path]
            
                if img_path.endswith("tcl.png"):
                    mix_node = nodes.new(type="ShaderNodeMix")
                    mix_node.data_type = "RGBA"
                    
                    img_node.image.colorspace_settings.name = 'Non-Color'
                    
                    links.new(img_node.outputs[0], mix_node.inputs[0])
                    
                    if alb_node != None:
                        links.new(mix_node.outputs[0], bsdf.inputs[0])
                        links.new(alb_node.outputs[0], mix_node.inputs[6])
                        mix_node.inputs[6].default_value = inka_color
                
                if img_path.endswith("alb.png"):
                    alb_node = img_node
                    links.new(img_node.outputs[0], bsdf.inputs[0])
                    
                    if mix_node != None:
                        links.new(mix_node.outputs[0], bsdf.inputs[0])
                        links.new(img_node.outputs[0], mix_node.inputs[6])
                        mix_node.inputs[6].default_value = inka_color
                            
                if img_path.endswith("mtl.png"):
                    img_node.image.colorspace_settings.name = 'Non-Color'
                    links.new(img_node.outputs[0], bsdf.inputs[6])
                            
                if img_path.endswith("spc.png"):
                    img_node.image.colorspace_settings.name = 'Non-Color'
                    links.new(img_node.outputs[0], bsdf.inputs[7])
                            
                if img_path.endswith("rgh.png"):
                    img_node.image.colorspace_settings.name = 'Non-Color'
                    links.new(img_node.outputs[0], bsdf.inputs[9])
                            
                if img_path.endswith("emm.png"):
                    img_node.image.colorspace_settings.name = 'Non-Color'
                    links.new(img_node.outputs[0], bsdf.inputs[20])
                                
                if img_path.endswith("opa.png"):
                    img_node.image.colorspace_settings.name = 'Non-Color'
                    links.new(img_node.outputs[0], bsdf.inputs[21])
                    
                if img_path.endswith("alp.png"):
                    img_node.image.colorspace_settings.name = 'Non-Color'
                    links.new(img_node.outputs[0], bsdf.inputs[21])
            
                if img_path.endswith("nrm.png"):
                    nrm_node = nodes.new("ShaderNodeNormalMap")
                    img_node.image.colorspace_settings.name = 'Non-Color'
                    links.new(nrm_node.outputs[0], bsdf.inputs[22])
                    links.new(img_node.outputs[0], nrm_node.inputs[1])
    
    if not bsdf.inputs[0].links:
        bsdf.inputs[0].default_value = inka_color
    
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def import_clt(armature=None, path="", file="", inkA=(0,0,0)):
    bpy.ops.object.select_all(action='DESELECT')
    
    bpy.ops.import_scene.fbx(filepath = path+file)
    
    obj = bpy.context.view_layer.objects.active
    
    # TRANSFORMING
    bpy.ops.transform.resize(value=(4.85 * armature.scale.x, 4.85 * armature.scale.y, 4.85 * armature.scale.z))
    bpy.ops.rotation_euler = armature.rotation_euler
    bpy.ops.transform.translate(value=(0, 0.82 * armature.scale.y, 0), orient_axis_ortho='X', orient_type='LOCAL')
    
    #RIGING
    for child in obj.children:
        bpy.ops.object.select_all(action='DESELECT')
        child.select_set(True)
        
        bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
        
        armature.select_set(True)
        bpy.context.view_layer.objects.active = armature
        
        bpy.ops.object.parent_set(type='ARMATURE')
        
        bpy.ops.object.select_all(action='DESELECT')
        child.select_set(True)
        bpy.context.view_layer.objects.active = child

        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.remove_doubles(threshold=0.001, use_unselected=True, use_sharp_edge_from_normals=True)
        bpy.ops.object.editmode_toggle()
        
        bpy.ops.object.modifier_add(type='VERTEX_WEIGHT_MIX')
        bpy.context.object.modifiers[2].mix_set = 'ALL'
        bpy.context.object.modifiers[2].mix_mode = 'ADD'
        bpy.context.object.modifiers[2].vertex_group_a = "arm1_L"
        bpy.context.object.modifiers[2].vertex_group_b = "arm1sub_L"
        if bpy.context.object.modifiers["VertexWeightMix"].is_active == False:
            bpy.ops.object.modifier_apply(modifier="VertexWeightMix", report=True)
        else:
            bpy.ops.object.modifier_remove(modifier="VertexWeightMix", report=True)
        
        bpy.ops.object.modifier_add(type='VERTEX_WEIGHT_MIX')
        bpy.context.object.modifiers[2].mix_set = 'ALL'
        bpy.context.object.modifiers[2].mix_mode = 'ADD'
        bpy.context.object.modifiers[2].vertex_group_a = "arm1_R"
        bpy.context.object.modifiers[2].vertex_group_b = "arm1sub_R"
        if bpy.context.object.modifiers["VertexWeightMix"].is_active == False:
            bpy.ops.object.modifier_apply(modifier="VertexWeightMix", report=True)
        else:
            bpy.ops.object.modifier_remove(modifier="VertexWeightMix", report=True)
        
        bpy.ops.object.modifier_add(type='VERTEX_WEIGHT_MIX')
        bpy.context.object.modifiers[2].mix_set = 'ALL'
        bpy.context.object.modifiers[2].mix_mode = 'ADD'
        bpy.context.object.modifiers[2].vertex_group_a = "crotch_L"
        bpy.context.object.modifiers[2].vertex_group_b = "leg1_L"
        if bpy.context.object.modifiers["VertexWeightMix"].is_active == False:
            bpy.ops.object.modifier_apply(modifier="VertexWeightMix", report=True)
        else:
            bpy.ops.object.modifier_remove(modifier="VertexWeightMix", report=True)
        
        bpy.ops.object.modifier_add(type='VERTEX_WEIGHT_MIX')
        bpy.context.object.modifiers[2].mix_set = 'ALL'
        bpy.context.object.modifiers[2].mix_mode = 'ADD'
        bpy.context.object.modifiers[2].vertex_group_a = "crotch_R"
        bpy.context.object.modifiers[2].vertex_group_b = "leg1_R"
        if bpy.context.object.modifiers["VertexWeightMix"].is_active == False:
            bpy.ops.object.modifier_apply(modifier="VertexWeightMix", report=True)
        else:
            bpy.ops.object.modifier_remove(modifier="VertexWeightMix", report=True)

        
        name_list = [
            ['joint_root','Spawner_Root'],
            ['hip','Waist'],
            ['spine1','Spine_1'],
            ['spine2','Spine_2'],
            ['chest','Spine_3'],
            ['shoulder_L','Clavicle_L'],
            ['arm1_L','Arm_1_L'],
            ['arm2_L','Arm_2_L'],
            ['hand_L','Wrist_L'],
            ['shoulder_R','Clavicle_R'],
            ['arm1_R','Arm_1_R'],
            ['arm2_R','Arm_2_R'],
            ['hand_R','Wrist_R'],
            ['head','Head'],
            ['leg1_L','Leg_1_L'],
            ['leg1_R','Leg_1_R'],
        ]

        v_groups = child.vertex_groups
        for n in name_list:
            if n[0] in v_groups:
                if v_groups[n[0]] != None:
                    v_groups[n[0]].name = n[1]
        
        
        bpy.ops.object.select_all(action='DESELECT')
        child.select_set(True)
        bpy.context.view_layer.objects.active = child
                    
        bpy.ops.object.modifier_remove(modifier="Armature", report=True)
        
        # SHADING
        
        nodes = bpy.context.active_object.active_material.node_tree.nodes
        links = bpy.context.active_object.active_material.node_tree.links
        
        for node in nodes:
            nodes.remove(node)
        
        output = nodes.new(type="ShaderNodeOutputMaterial")
        bsdf = nodes.new(type="ShaderNodeBsdfPrincipled")
        links.new(bsdf.outputs[0], output.inputs[0])
        
        alb_node = None
        mix_node = None
        
        for img_path in path_iterator( path ):
            if img_path.lower().startswith(bpy.context.active_object.active_material.name.lower()+"_"):
                full_path = os.path.join( path, img_path )
                
                bpy.ops.image.open(filepath = full_path)
                        
                img_node = nodes.new(type="ShaderNodeTexImage")
                img_node.image = bpy.data.images[img_path]
            
                if img_path.endswith("tcl.png"):
                    mix_node = nodes.new(type="ShaderNodeMix")
                    mix_node.data_type = "RGBA"
                    
                    img_node.image.colorspace_settings.name = 'Non-Color'
                    
                    links.new(img_node.outputs[0], mix_node.inputs[0])
                    
                    if alb_node != None:
                        links.new(mix_node.outputs[0], bsdf.inputs[0])
                        links.new(alb_node.outputs[0], mix_node.inputs[6])
                
                if img_path.endswith("alb.png"):
                    alb_node = img_node
                    links.new(img_node.outputs[0], bsdf.inputs[0])
                    
                    if mix_node != None:
                        links.new(mix_node.outputs[0], bsdf.inputs[0])
                        links.new(img_node.outputs[0], mix_node.inputs[6])
                            
                if img_path.endswith("mtl.png"):
                    img_node.image.colorspace_settings.name = 'Non-Color'
                    links.new(img_node.outputs[0], bsdf.inputs[6])
                            
                if img_path.endswith("spc.png"):
                    img_node.image.colorspace_settings.name = 'Non-Color'
                    links.new(img_node.outputs[0], bsdf.inputs[7])
                            
                if img_path.endswith("rgh.png"):
                    img_node.image.colorspace_settings.name = 'Non-Color'
                    links.new(img_node.outputs[0], bsdf.inputs[9])
                            
                if img_path.endswith("emm.png"):
                    img_node.image.colorspace_settings.name = 'Non-Color'
                    links.new(img_node.outputs[0], bsdf.inputs[20])
                                
                if img_path.endswith("opa.png"):
                    img_node.image.colorspace_settings.name = 'Non-Color'
                    links.new(img_node.outputs[0], bsdf.inputs[21])
                    
                if img_path.endswith("alp.png"):
                    img_node.image.colorspace_settings.name = 'Non-Color'
                    links.new(img_node.outputs[0], bsdf.inputs[21])
            
                if img_path.endswith("nrm.png"):
                    nrm_node = nodes.new("ShaderNodeNormalMap")
                    img_node.image.colorspace_settings.name = 'Non-Color'
                    links.new(nrm_node.outputs[0], bsdf.inputs[22])
                    links.new(img_node.outputs[0], nrm_node.inputs[1])
    
    
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.delete(use_global=False)
    

# HAIR
def create_hair(index=0, armature=None, self=None, type="inkling_F"):
    
    hair_armature = None
    mesh = None
    
    bpy.ops.object.select_all(action='DESELECT')
    src_path=str(srcPath) + "/" + type + "_hair.blend"
 
    with bpy.data.libraries.load(src_path) as (data_from, data_to):
        data_to.objects = data_from.objects
 
    for obj in data_to.objects:
        if obj.name.startswith("Hair "+"{:02d}".format(index)):
            bpy.context.collection.objects.link(obj)
            if obj.type == "ARMATURE":
                hair_armature = obj
            else:
                mesh = obj
    
    bpy.ops.object.select_all(action='DESELECT')
    hair_armature.select_set(True)
    bpy.context.view_layer.objects.active = hair_armature

    bpy.ops.object.posemode_toggle()
    bpy.context.object.pose.bones["Head_Root"].constraints["Copy Transforms"].target = bpy.data.objects[armature.name]
    bpy.context.object.pose.bones["Head_Root"].constraints["Copy Transforms"].subtarget = "Head"
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.context.object.pose.bones["Head_Root"].constraints.new(type='COPY_SCALE')
    bpy.context.object.pose.bones["Head_Root"].constraints["Copy Scale"].target = bpy.data.objects[armature.name]
    bpy.context.object.pose.bones["Head_Root"].constraints["Copy Scale"].subtarget = "Hair_Scale"
    
    # MATERIALS
    inka_color = (self.ink_A[0], self.ink_A[1], self.ink_A[2], 1)
    inkb_color = (self.ink_B[0], self.ink_B[1], self.ink_B[2], 1)
    
    mesh.active_material = mesh.active_material.copy()
    hair_mat = mesh.active_material
    
    hair_mat.node_tree.nodes["Group"].inputs[0].default_value = inka_color
    hair_mat.node_tree.nodes["Group"].inputs[2].default_value = inkb_color
    hair_mat.node_tree.nodes["Group"].inputs[4].default_value = self.hair_emission
    
    bpy.ops.object.select_all(action='DESELECT')
    armature.select_set(True)
    bpy.context.view_layer.objects.active = armature
    
# EYEBLOW
def create_eyeblow(index=0, armature=None, self=None, type="inkling_F"):

    mesh = None
    
    bpy.ops.object.select_all(action='DESELECT')
    src_path=str(srcPath) + "/"+type+"_eyeblow.blend"
 
    with bpy.data.libraries.load(src_path) as (data_from, data_to):
        data_to.objects = data_from.objects
 
    for obj in data_to.objects:
        if obj.name.lower().startswith("eyeblow "+str(index)):
            bpy.context.collection.objects.link(obj)
            mesh = obj

    bpy.context.view_layer.objects.active = armature
    armature.select_set(True)
    mesh.select_set(True)

    bpy.ops.object.parent_set(type='ARMATURE')

    # MATERIALS
    inka_color = (self.ink_A[0], self.ink_A[1], self.ink_A[2], 1)
    inkb_color = (self.ink_B[0], self.ink_B[1], self.ink_B[2], 1)
    
    mesh.active_material = mesh.active_material.copy()
    eyeblow_mat = mesh.active_material
    eyeblow_mat.node_tree.nodes[1].inputs[0].default_value = inka_color
    eyeblow_mat.node_tree.nodes[1].inputs[1].default_value = inkb_color
    
    mesh.select_set(False)
    armature.select_set(True)
    bpy.context.view_layer.objects.active = armature
    
def create_bottom(index=0, armature=None, self=None):
    bpy.ops.object.select_all(action='DESELECT')
    
    maskIndex = ["00","06","05","02","05","07","08","07","00"]
    
    bpy.ops.object.mode_set(mode='OBJECT'),

    mesh = None
    
    bpy.ops.object.select_all(action='DESELECT')
    src_path=str(srcPath) + "/bottom_F.blend"
 
    with bpy.data.libraries.load(src_path) as (data_from, data_to):
        data_to.objects = data_from.objects
 
    for obj in data_to.objects:
        if obj.name.startswith("Bottom "+str(index)):
            bpy.context.collection.objects.link(obj)
            mesh = obj
    
    bpy.ops.object.select_all(action='DESELECT')
    mesh.select_set(True)
    bpy.context.view_layer.objects.active = armature

    bpy.ops.object.parent_set(type='ARMATURE')
    
    # FIND THE MESH
    for child in armature.children:
        if "Body" in child.name and not "Hif" in child.name:
            bpy.ops.object.select_all(action='DESELECT')
            child.select_set(True)
            bpy.context.view_layer.objects.active = child
    
    # Get THE IMAGE
    a = bpy.data.images.new("btm_"+"{:02d}".format(index)+"_opa.png", 500, 500)
    a.colorspace_settings.name = "Non-Color"
    # GET THE MATERIAL
    mat = bpy.context.view_layer.objects.active.active_material
    # Texture
    node_tex = mat.node_tree.nodes.new("ShaderNodeTexImage")
    node_tex.location = [-300,300]
    # LINK NODES
    links = mat.node_tree.links
    link = links.new(node_tex.outputs[0], mat.node_tree.nodes["Group"].inputs['Bottom_Mask'])
    #Find Texture
    for node in mat.node_tree.nodes:
        node.select = False
    
    node_tex.select = True
    mat.node_tree.nodes.active = node_tex

    node_tex.image = bpy.data.images.load(str(srcPath)+"/GearAlphaMask/btm_"+maskIndex[index]+"_opa.png")
    node_tex.image.colorspace_settings.name = 'Non-Color'

    # MATERIALS
    inka_color = (self.ink_A[0], self.ink_A[1], self.ink_A[2], 1)
    inkb_color = (self.ink_B[0], self.ink_B[1], self.ink_B[2], 1)
    
    mesh.active_material = mesh.active_material.copy()
    eyeblow_mat = mesh.active_material
    eyeblow_mat.node_tree.nodes["Group"].inputs[0].default_value = inka_color
    eyeblow_mat.node_tree.nodes["Group"].inputs[2].default_value = inkb_color
    
    bpy.ops.object.select_all(action='DESELECT')
    armature.select_set(True)
    bpy.context.view_layer.objects.active = armature


def create_inkling(self, context, type="inkling_F"):

    armature = None
    
    bpy.ops.object.select_all(action='DESELECT')
    src_path=str(srcPath) + "/"+type+"_body.blend"
 
    with bpy.data.libraries.load(src_path) as (data_from, data_to):
        data_to.objects = data_from.objects
 
    for obj in data_to.objects:
        bpy.context.collection.objects.link(obj)
        if obj.type == "ARMATURE":
            armature = obj
    
    bpy.ops.object.select_all(action='DESELECT')
    armature.name = self.name
    bpy.context.view_layer.objects.active = armature
    armature.select_set(True)

    # MATERIALS
    inka_color = (self.ink_A[0], self.ink_A[1], self.ink_A[2], 1)
    inkb_color = (self.ink_B[0], self.ink_B[1], self.ink_B[2], 1)
    
    #bpy.context.view_layer.objects.active.children[0].active_material = bpy.context.view_layer.objects.active.children[0].active_material.copy()
    body_mat = bpy.context.view_layer.objects.active.children[0].active_material
    skin_color = (self.skin[0], self.skin[1], self.skin[2], 1)
    cloth_color = (self.cloth[0], self.cloth[1], self.cloth[2], 1)
    eye_contour_color = (self.eye_contour[0], self.eye_contour[1], self.eye_contour[2], 1)
    body_mat.node_tree.nodes["Group"].inputs[0].default_value = skin_color
    body_mat.node_tree.nodes["Group"].inputs[1].default_value = cloth_color
    body_mat.node_tree.nodes["Group"].inputs[2].default_value = eye_contour_color
    body_mat.node_tree.nodes["Group"].inputs[3].default_value = inka_color
    body_mat.node_tree.nodes["Group"].inputs[5].default_value = inkb_color
    
    #bpy.context.view_layer.objects.active.children[5].active_material = bpy.context.view_layer.objects.active.children[5].active_material.copy()
    head_mat = bpy.context.view_layer.objects.active.children[5].active_material
    head_mat.node_tree.nodes["Group.002"].inputs[0].default_value = skin_color
    head_mat.node_tree.nodes["Group.002"].inputs[1].default_value = cloth_color
    head_mat.node_tree.nodes["Group.002"].inputs[2].default_value = eye_contour_color
    head_mat.node_tree.nodes["Group.002"].inputs[3].default_value = inka_color
    head_mat.node_tree.nodes["Group.002"].inputs[5].default_value = inkb_color
    
    #bpy.context.view_layer.objects.active.children[4].active_material = bpy.context.view_layer.objects.active.children[4].active_material.copy()
    bpy.context.view_layer.objects.active.children[4].active_material.node_tree.nodes[1].inputs[0].default_value = inka_color
    
    #bpy.context.view_layer.objects.active.children[2].active_material = bpy.context.view_layer.objects.active.children[2].active_material.copy()
    eyes_mat = bpy.context.view_layer.objects.active.children[2].active_material
    
    eye_texture = eyes_mat.node_tree.nodes[3].image = bpy.data.images.load(str(srcPath)+"/Eyes Textures/m_eye_alb."+ "{:02d}".format(self.eyes-1) +".png", check_existing=False)
    
    eyes_mat.node_tree.nodes[2].inputs[1].default_value = float(self.eyes)
    eyes_mat.node_tree.nodes[2].inputs[2].default_value = self.eyes_hue
    eyes_mat.node_tree.nodes[2].inputs[3].default_value = self.eyes_emission
    
    hif = bpy.context.view_layer.objects.active.children[3]
    hif.active_material.node_tree.nodes["Group"].inputs[0].default_value = inka_color
    
    # Hif
    # hif.data.shape_keys.key_blocks['Human'].driver_remove()
    driver = hif.data.shape_keys.key_blocks['Human'].driver_add("value")
    var1 = driver.driver.variables.new()
    var1.name = "var"
    var1.type = "TRANSFORMS"
    var1.targets[0].id = bpy.context.view_layer.objects.active
    var1.targets[0].transform_type = "LOC_Y"
    var1.targets[0].transform_space = "LOCAL_SPACE"
    var1.targets[0].bone_target = "Hif"
    driver.driver.expression = "var * -1 + 1"
    
    hif_mat = bpy.context.view_layer.objects.active.children[2].active_material
    # hif_mat.node_tree.nodes[1].inputs[3].driver_remove()
    driver2 = hif_mat.node_tree.nodes[1].inputs[3].driver_add("default_value")
    var2 = driver2.driver.variables.new()
    var2.name = "var"
    var2.type = "TRANSFORMS"
    var2.targets[0].id = bpy.context.view_layer.objects.active
    var2.targets[0].transform_type = "LOC_Y"
    var2.targets[0].transform_space = "LOCAL_SPACE"
    var2.targets[0].bone_target = "Hif"
    driver2.driver.expression = "var * -1 + 1"

    # Hair
    create_hair(self.hair, bpy.context.view_layer.objects.active, self, type)
    create_eyeblow(self.eyeblow, bpy.context.view_layer.objects.active, self, type)
    create_bottom(self.bottom, bpy.context.view_layer.objects.active, self)


class OBJECT_OT_add_inkling(Operator, AddObjectHelper):
    bl_idname = "mesh.player"
    bl_label = "Add Splatoon Player"
    bl_description = "Create a procedural Splatoon player."
    bl_options = {'REGISTER', 'UNDO'}
    
    type: bpy.props.EnumProperty(
        name="Type and Gender",
        description="Octoling/Inkling",
        items=(
            ('inkling_F', 'Inkling Female', 'An inkling girl'),
            ('inkling_M', 'Inkling Male', 'An inkling boy'),
            ('octoling_F', 'Octoling Female', 'An octoling girl'),
            ('octoling_M', 'Octoling Male', 'An octoling boy')
        )
    )
    name: bpy.props.StringProperty(
        name="Name",
        description="The player object name",
        maxlen=50,
        default="Inkling",
    )
    ink_A: FloatVectorProperty(  
       name="Ink Color",
       subtype='COLOR',
       default=(1, 0, 0),
       min=0.0, max=1.0,
       description="The player ink color"
    )
    ink_B: FloatVectorProperty(  
       name="Ennemie Ink Color",
       subtype='COLOR',
       default=(0, 1, 1),
       min=0.0, max=1.0,
       description="The player enemie ink color (when she take damages)"
    )
    skin: FloatVectorProperty(  
       name="Skin Tone",
       subtype='COLOR',
       default=(1, 0.59, 0.5),
       min=0.0, max=1.0,
       description="The player skin color"
    )
    cloth: FloatVectorProperty(  
       name="Cloth Color",
       subtype='COLOR',
       default=(0, 0, 0),
       min=0.0, max=1.0,
       description="The player cloth color"
    )
    eye_contour: FloatVectorProperty(  
       name="Eye Contour",
       subtype='COLOR',
       default=(0, 0, 0),
       min=0.0, max=1.0,
       description="The player eye_contour color"
    )
    eyes: bpy.props.IntProperty(  
        name="Eyes",
        description="The player eyes texture index",
        min=1, max=20,
        default=1
    )
    eyes_hue: bpy.props.FloatProperty(  
        name="Eyes Hue",
        default=0.5,
        min=0.0, max=1.0,
        description="The player eyes tone decalage"
    )
    eyes_emission: bpy.props.FloatProperty(  
        name="Eyes Emission",
        default=0,
        min=0.0, max=100.0,
        description="The player eyes luminosity"
    )
    hair: bpy.props.IntProperty(
        name="Hair",
        description="The hair index of the new player",
        min=0, max=15,
        default=0,
    )
    hair_emission: bpy.props.FloatProperty(  
        name="Hair Emission",
        default=0,
        min=0.0, max=100.0,
        description="The player hair luminosity"
    )
    eyeblow: bpy.props.IntProperty(
        name="Eyeblow",
        description="The eyeblow index of the new player",
        min=0, max=3,
        default=0,
    )
    bottom: bpy.props.IntProperty(
        name="Legwear",
        description="The legwear index of the new player",
        min=0, max=8,
        default=0,
    )

    def execute(self, context):
        create_inkling(self, context, self.type)
        return {'FINISHED'}


# Registration
def add_inkling_button(self, context):
    self.layout.operator(
        OBJECT_OT_add_inkling.bl_idname,
        text="Splatoon Player",
        icon='USER')

def register():
    bpy.utils.register_class(OBJECT_OT_add_inkling)
    bpy.types.VIEW3D_MT_mesh_add.append(add_inkling_button)
    
    #OTHER SCRIPTS :
    exec(compile(open(str(srcPath) + "/cloth_import.py").read(), "cloth_import.py", 'exec'))
    exec(compile(open(str(srcPath) + "/weapon_import.py").read(), "weapon_import.py", 'exec'))
    exec(compile(open(str(srcPath) + "/item_import.py").read(), "item_import.py", 'exec'))
    exec(compile(open(str(srcPath) + "/fast_squid.py").read(), "fast_squid.py", 'exec'))
    exec(compile(open(str(srcPath) + "/fast_octopus.py").read(), "fast_octopus.py", 'exec'))
def unregister():
    bpy.utils.unregister_class(OBJECT_OT_add_inkling)
    bpy.types.VIEW3D_MT_mesh_add.remove(add_inkling_button)

if __name__ == "__main__":
    register()