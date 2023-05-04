bl_info = {
    "name": "Splatoon Cloth",
    "author": "Coconuts XXS",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "File > Import > Splatoon Cloth",
    "description": "Recreate a splatoon cloth model auto rigged for your model with the .fbx file and the textures",
    "warning": "",
    "doc_url": "",
    "category": "Import",
}

import bpy
import os
from pathlib import Path
from bpy.utils import resource_path

USER = Path(resource_path('USER'))
ADDON = "Splatoon Tools"

srcPath = USER / "scripts" / "addons" / ADDON

def path_iterator(folder_path):
    for fp in os.listdir(folder_path):
        if fp.endswith( tuple( bpy.path.extensions_image ) ):
            yield fp

def import_clt(self):
    path = str(os.path.split(self.filepath)[0]) + "/"
    file = str(os.path.split(self.filepath)[1])
    armature = bpy.context.view_layer.objects.active
    inka_color = (self.ink_A[0], self.ink_A[1], self.ink_A[2], 1)
    
    if armature != None:
        if armature.type != "ARMATURE":
            self.report({'ERROR'}, 'Please, select the armature of your Inkling/Octoling before import clothes')
            return
    else:
        self.report({'ERROR'}, 'Please, select the armature of your Inkling/Octoling before import clothes')
        return
    
    mask_path = str(srcPath) + "/GearAlphaMask/" + self.mask_type
    mask_shs_path = str(srcPath) + "/GearAlphaMask/" + self.mask_type_shs
    
    bpy.ops.object.select_all(action='DESELECT')
    
    bpy.ops.import_scene.fbx(filepath = path+file)
    
    obj = bpy.context.view_layer.objects.active
    obj.location = armature.location
    
    body_mesh = None
    
    for armature_child in armature.children:
        if "Body" in armature_child.active_material.name and not "Hif" in armature_child.active_material.name:
            body_mesh = armature_child
            body_mesh.name = "FINDED"
    
    # CLOTH :
    if self.cloth_type == "clt":
        # TRANSFORMING
        bpy.ops.transform.resize(value=(4.85 * armature.scale.x, 4.85 * armature.scale.y, 4.85 * armature.scale.z))
        bpy.ops.rotation_euler = armature.rotation_euler
        bpy.ops.transform.translate(value=(0, 0.82 * armature.scale.y, 0), orient_axis_ortho='X', orient_type='LOCAL')
    
        # MASK
        if self.mask_type != "none" and body_mesh != None:
            bpy.ops.image.open(filepath = mask_path)
        
            mask_node = body_mesh.active_material.node_tree.nodes.new(type="ShaderNodeTexImage")
            mask_node.image = bpy.data.images[self.mask_type]
            mask_node.image.colorspace_settings.name = 'Non-Color'
            body_mesh.active_material.node_tree.links.new(mask_node.outputs[0], body_mesh.active_material.node_tree.nodes["Group"].inputs[9])
    
    # SHOOES
    if self.cloth_type == "shs":
        # TRANSFORMING
        bpy.ops.transform.resize(value=(5.1 * armature.scale.x, 5.1 * armature.scale.y, 5.1 * armature.scale.z))
        bpy.ops.rotation_euler = armature.rotation_euler
        bpy.ops.transform.translate(value=(0.097/2, 0.4213, 0.04), orient_axis_ortho='X', orient_type='LOCAL')
    
    
        # MASK
        if self.mask_type_shs != "none" and body_mesh != None:
            bpy.ops.image.open(filepath = mask_shs_path)
        
            mask_node = body_mesh.active_material.node_tree.nodes.new(type="ShaderNodeTexImage")
            mask_node.image = bpy.data.images[self.mask_type_shs]
            mask_node.image.colorspace_settings.name = 'Non-Color'
            body_mesh.active_material.node_tree.links.new(mask_node.outputs[0], body_mesh.active_material.node_tree.nodes["Group"].inputs[10])
            
    # HEAD
    if self.cloth_type == "head":
        # TRANSFORMING
        bpy.ops.transform.resize(value=(4.85 * armature.scale.x, 4.85 * armature.scale.y, 4.85 * armature.scale.z))
        bpy.ops.rotation_euler = armature.rotation_euler
        bpy.ops.transform.translate(value=(0, 1.2523 * armature.scale.y, 0), orient_axis_ortho='X', orient_type='LOCAL')
    
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
        
        if self.cloth_type == "clt":
            bpy.context.object.location = (armature.location.x, armature.location.y, 0.82 + armature.location.z)
            bpy.context.object.scale = (0.125*armature.scale.x, 0.125*armature.scale.y, 0.125*armature.scale.z)
        elif self.cloth_type == "shs":
            bpy.context.object.location = (0.097+armature.location.x, armature.location.y+-0.04, 0.4213 + armature.location.z)
            bpy.context.object.scale = (0.125*armature.scale.x, 0.125*armature.scale.y, 0.125*armature.scale.z)
        elif self.cloth_type == "head":
            bpy.context.object.location = (armature.location.x, armature.location.y, 1.2523 + armature.location.z)
            bpy.context.object.scale = (0.1195*armature.scale.x, 0.1195*armature.scale.y, 0.1195*armature.scale.z)
        
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
            ['root', 'Head'],
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
            ['fingerA1_L', 'Finger_B_1_L'],
            ['fingerA2_L', 'Finger_B_2_L'],
            ['fingerB1_L', 'Finger_C_1_L'],
            ['fingerB2_L', 'Finger_C_2_L'],
            ['thumb_L', 'Finger_A_1_L'],
            ['fingerA1_R', 'Finger_B_1_R'],
            ['fingerA2_R', 'Finger_B_2_R'],
            ['fingerB1_R', 'Finger_C_1_R'],
            ['fingerB2_R', 'Finger_C_2_R'],
            ['thumb_R', 'Finger_A_1_R'],
            ['leg2sub_L', 'Leg_2_L'],
            ['foot_L', 'Ankle_L'],
            ['toe_L', 'Toe_L'],
            ['leg2sub_R', 'Leg_2_R'],
            ['foot_R', 'Ankle_R'],
            ['toe_R', 'Toe_R'],
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
        
        if bpy.context.active_object.active_material.name.lower().endswith("glass"):
            bsdf.inputs['Transmission'].default_value = 1
            bsdf.inputs['Transmission Roughness'].default_value = 1
            bsdf.inputs['Alpha'].default_value = 0.3
        
        alb_node = None
        mix_node = None
        hue_node = None
        ink_node = None
        
        if bpy.context.active_object.active_material.name.startswith("Obj_"):
            bpy.context.active_object.active_material.name = bpy.context.active_object.active_material.name[4:]
            base_name = bpy.context.active_object.active_material.name
        if bpy.context.active_object.active_material.name.endswith("hood"):
            bpy.context.active_object.active_material.name = bpy.context.active_object.active_material.name[:-4]
            base_name = bpy.context.active_object.active_material.name
        if bpy.context.active_object.active_material.name.endswith(".001") or bpy.context.active_object.active_material.name.endswith(".002") or bpy.context.active_object.active_material.name.endswith(".003"):
            bpy.context.active_object.active_material = bpy.data.materials[bpy.context.active_object.active_material.name[:-4]]
        
        for img_path in path_iterator( path ):
            if img_path.lower().startswith(bpy.context.active_object.active_material.name.lower()+"_"):
                full_path = os.path.join( path, img_path )
                
                bpy.ops.image.open(filepath = full_path)
                        
                img_node = nodes.new(type="ShaderNodeTexImage")
                img_node.image = bpy.data.images[img_path]
            
                if img_path.endswith("tcl.png"):
                    mix_node = nodes.new(type="ShaderNodeMix")
                    mix_node.data_type = "RGBA"
                    mix_node.inputs[7].default_value = inka_color
                    
                    img_node.image.colorspace_settings.name = 'Non-Color'
                    
                    links.new(img_node.outputs[0], mix_node.inputs[0])
                    
                    if hue_node != None:
                        links.new(hue_node.outputs[0], mix_node.inputs[6])
                        links.new(mix_node.outputs[2], bsdf.inputs[0])
                
                if img_path.endswith("alb.png"):
                    alb_node = img_node
                    
                    hue_node = nodes.new(type="ShaderNodeHueSaturation")
                    hue_node.inputs[0].default_value = self.hue
                    hue_node.inputs[1].default_value = self.saturation
                    hue_node.inputs[2].default_value = self.value
                    
                    links.new(img_node.outputs[0], hue_node.inputs[4])
                    links.new(hue_node.outputs[0], bsdf.inputs[0])
                    
                    nodes.active = alb_node
                    
                    if mix_node != None:
                        links.new(hue_node.outputs[0], mix_node.inputs[6])
                        links.new(mix_node.outputs[2], bsdf.inputs[0])
                            
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
                    
                if img_path.endswith("2cl.png"):
                    img_node.image.colorspace_settings.name = 'Non-Color'
                    ink_node = img_node
                    
        if ink_node != None and False==True:
            # ALBEDO
            mix_alb = nodes.new(type="ShaderNodeMix")
            alb_input = bsdf.inputs[0].links[0].from_node
            mix_alb.data_type = "RGBA"
            
            links.new(ink_node.outputs[0], mix_alb.inputs[5])
            links.new(alb_input.outputs[0], mix_alb.inputs[6])
            mix_alb.inputs[7].default_value = inka_color
            links.new(mix_alb.outputs[0], bsdf.inputs[0])
            
            # SPECULAR
            mix_spc = nodes.new(type="ShaderNodeMix")
            if len(bsdf.inputs[7].links) > 0:
                spc_input = bsdf.inputs[7].links[0].from_node
                links.new(spc_input.outputs[0], mix_spc.inputs[1])
            else:
                mix_spc.inputs[1].default_value = 0.5
            
            links.new(ink_node.outputs[0], mix_spc.inputs[0])
            mix_spc.inputs[2].default_value = 0.7
            links.new(mix_spc.outputs[0], bsdf.inputs[7])
            
            # ROUGHNESS
            mix_rgh = nodes.new(type="ShaderNodeMix")
            
            if len(bsdf.inputs[9].links[0].from_node) > 0:
                rgh_input = bsdf.inputs[9].links[0].from_node
                links.new(rgh_input.outputs[0], mix_rgh.inputs[1])
            else:
                mix_spc.inputs[1].default_value = 0.3
            
            links.new(ink_node.outputs[0], mix_rgh.inputs[0])
            mix_rgh.inputs[2].default_value = 0.3
            links.new(mix_rgh.outputs[0], bsdf.inputs[9])
            
            # NORMAL
            mix_nrm = nodes.new(type="ShaderNodeBump")
            nrm_input = bsdf.inputs[22].links[0].from_node
            
            links.new(ink_node.outputs[0], mix_nrm.inputs[2])
            links.new(nrm_input.outputs[0], mix_nrm.inputs[3])
            links.new(mix_nrm.outputs[0], bsdf.inputs[22])
        
        if self.cloth_type == "shs":
            # the new object is created with the old object's data, which makes it "linked"
            new_child = bpy.data.objects.new(child.name+"_R", child.data)
            
            bpy.ops.object.make_single_user(object=True, obdata=True, material=False, animation=False, obdata_animation=False)
            
            child.name = child.name+"_L"
            bpy.context.collection.objects.link(new_child)
            new_child.scale = child.scale
            new_child.location = child.location
            new_child.rotation_euler = child.rotation_euler
            
            new_child.scale = (-1 * new_child.scale.x, 1 * new_child.scale.y, 1 * new_child.scale.z)
            
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
            
            bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.normals_make_consistent(inside=False)
            bpy.ops.object.editmode_toggle()
            
            new_child.location[0] = -0.097*armature.scale.x + armature.location.x
            bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.remove_doubles(threshold=0.001, use_unselected=True, use_sharp_edge_from_normals=True)
            bpy.ops.object.editmode_toggle()
            
            name_list2 = [
                ['Leg_2_L', 'Leg_2_R'],
                ['Ankle_L', 'Ankle_R'],
                ['Toe_L', 'Toe_R']
            ]

            v_groups2 = new_child.vertex_groups
            for n in name_list2:
                if n[0] in v_groups2:
                    if v_groups2[n[0]] != None:
                        v_groups2[n[0]].name = n[1]
                        
            bpy.ops.object.select_all(action='DESELECT')
            new_child.select_set(True)
            armature.select_set(True)
            bpy.context.view_layer.objects.active = armature
            bpy.ops.object.parent_set(type='ARMATURE')

    
    
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.delete(use_global=False)
    
    bpy.ops.object.select_all(action='DESELECT')
    armature.select_set(True)
    bpy.context.view_layer.objects.active = armature
    
    return {'FINISHED'}


from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty, FloatVectorProperty, FloatProperty
from bpy.types import Operator

class import_cloth(Operator, ImportHelper):
    bl_idname = "import_splatoon.cloth"
    bl_label = "Import Cloth"


    filter_glob: bpy.props.StringProperty(
        default="*.fbx",
        options={'HIDDEN'},
        maxlen=255,
    )

    ink_A: FloatVectorProperty(
        name="Team Color",
        description="The ink color of the imported cloth",
        default=(1, 0, 0),
        min=0.0, max=1.0,
        subtype='COLOR'
    )
    
    cloth_type: EnumProperty(
        name="Cloth Type",
        description="The type of the imported cloth.",
        items=(
            ('head', 'Head Accessory', 'Hat, Mask, Glasses, Earring, etc'),
            ('clt', 'Body Cloth', 'T-shirt, Jacket, Parka, Sweater, Vest, etc'),
            ('shs', 'Shooes', 'Boots, Baskets, Sandals, etc')
        )
    )
    
    mask_type: EnumProperty(
        name="Alpha Mask (Cloth)",
        description="Choose the mask to hide the skin behind the clothes",
        items=(
            ('none', "Nothing", "No Mask"),
            ('clt_00_big_opa.png', "Body and Shoulders", "Mask 00 big"),
            ('clt_00_wide_opa.png', "Body and 1/4 Arms", "Mask 00 wide"),
            ('clt_01_opa.png', "Body and 1/2 Arms", "Mask 01"),
            ('clt_02_opa.png', "Body and Arms", "Mask 02"),
            ('clt_03_opa.png', 'Belly', "Mask 03"),
            ('clt_04_opa.png', 'Body, Shoulders and 1/2 Fingers', "Mask 04"),
            ('clt_05_opa.png', 'Body and Arms without Shoulders', "Mask 05"),
            ('clt_06_opa.png', 'Body and Arms without Shoulders', "Mask 06"),
            ('clt_07_opa.png', 'Body, Arms and 1/2 Fingers', "Mask 07"),
            ('clt_08_opa.png', 'Torso, Wrists and 1/2 Fingers', "Mask 08"),
            ('clt_09_opa.png', 'Body, Arms and Hands', "Mask 09"),
            ('clt_10_opa.png', 'Body, 1/2 Arms without Neck', "Mask 10"),
            ('clt_11_opa.png', 'Body, 1/2 Arms without Bowl', "Mask 11"),
            ('clt_12_opa.png', 'Belly, Torso and Hands', "Mask 12"),
            ('clt_13_opa.png', 'Belly and Torso', "Mask 13"),
            ('clt_14_opa.png', 'Body, Arms and 1/2 Fingers', "Mask 14"),
            ('clt_15_opa.png', 'Neck and Torso', "Mask 15"),
            ('clt_16_opa.png', 'Neck, Torso and 1/2 Belly', "Mask 16"),
            ('clt_17_opa.png', 'Body, Neck and 1/2 Arms', "Mask 17"),
            ('clt_18_opa.png', 'Body, Neck and Arms', "Mask 18"),
            ('clt_19_opa.png', 'Asymmetric', "Mask 19"),
            ('clt_20_opa.png', 'Entire Body without Neck and Head', "Mask 20"),
            ('clt_21_opa.png', 'Body, 1/2 Arms without Neck and Torso', "Mask 21"),
            ('clt_22_opa.png', 'Right Wrists and 1/2 Fingers', "Mask 22"),
            ('clt_23_opa.png', 'All Neck, Body and Arms', "Mask 23"),
            ('clt_24_opa.png', 'Body, Shoulders without Chest', "Mask 24"),
            ('clt_25_opa.png', 'Body without Arms', "Mask 25"),
            ('clt_26_opa.png', 'Body, 3/4 Arms and 1/2 Fingers', "Mask 26"),
            ('clt_27_opa.png', 'Body, 3/4 Arms without belly', "Mask 27"),
            ('clt_28_opa.png', 'Torso, Neck, 1/2 Arms and Wrists', "Mask 28"),
            ('clt_29_opa.png', 'Body, 3/4 Arms whithout Neck', "Mask 29"),
            ('clt_30_opa.png', 'Body, Shoulders whithout Neck', "Mask 30"),
            ('clt_31_opa.png', 'Body, Shoulders whithout Neck and without 1/2 Torso', "Mask 31"),
            ('clt_32_opa.png', 'Body, Right Wrist', "Mask 32"),
            ('clt_33_opa.png', 'Torso and Righth 1/2 Arm', "Mask 33")
        ),
        default='none',
    )
    mask_type_shs: EnumProperty(
        name="Alpha Mask (Shooes)",
        description="Choose the mask to hide the skin behind the shooes",
        items=(
            ('none', "Nothing", "No Mask"),
            ('shs_00_opa.png', "Toe and Bottom", "Mask 00"),
            ('shs_01_opa.png', "Toe, 1/2 Foot and Bottom", "Mask 01"),
            ('shs_02_opa.png', "Foot", "Mask 02"),
            ('shs_03_opa.png', "Foot and Ankle", "Mask 03"),
            ('shs_04_opa.png', "Foot, Ankle and 1/2 Leg", "Mask 04"),
            ('shs_05_opa.png', "Foot, Ankle and 1/4 Leg", "Mask 05"),
            ('shs_06_opa.png', "1/3 Foot", "Mask 06")
        ),
        default='none',
    )
    
    hue: FloatProperty(
        name="Hue",
        description="The hue decalage of the texture",
        default=0.5,
        min=0.0, max=1.0,
    )
    saturation: FloatProperty(
        name="Saturation",
        description="The saturation of the texture",
        default=1,
        min=0.0, max=10.0,
    )
    value: FloatProperty(
        name="Value",
        description="The value of the texture",
        default=1,
        min=0.0, max=10.0,
    )

    def execute(self, context):
        return import_clt(self)


def menu_func_import(self, context):
    self.layout.operator(import_cloth.bl_idname, text="Splatoon Cloth")

def register():
    bpy.utils.register_class(import_cloth)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
def unregister():
    bpy.utils.unregister_class(import_cloth)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
if __name__ == "__main__":
    register()
