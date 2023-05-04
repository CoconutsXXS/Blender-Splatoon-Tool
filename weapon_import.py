bl_info = {
    "name": "Splatoon Weapon",
    "author": "Coconuts XXS",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "File > Import > Splatoon Weapon",
    "description": "Recreate a splatoon weapon model with the .fbx file and the textures",
    "warning": "",
    "doc_url": "",
    "category": "Import",
}

import bpy
import os

def path_iterator(folder_path):
    for fp in os.listdir(folder_path):
        if fp.endswith( tuple( bpy.path.extensions_image ) ):
            yield fp

def create_weapon(self):
    path = str(os.path.split(self.filepath)[0]) + "/"
    file = str(os.path.split(self.filepath)[1])
    
    bpy.ops.object.select_all(action='DESELECT')
    
    bpy.ops.import_scene.fbx(filepath = path+file)
    
    obj = bpy.context.view_layer.objects.active
    
    #RIGING
    if obj.type == "ARMATURE":
        bpy.ops.object.editmode_toggle()
        bpy.ops.armature.select_all(action='DESELECT')
        for bone in obj.data.edit_bones:
            if len(bone.children) > 0:
                bpy.ops.armature.select_all(action='DESELECT')
                
                bone.tail = bone.children[0].head
                
                bone.select = True
                bone.children[0].select = True
                obj.data.edit_bones.active = bone
                bpy.ops.armature.parent_set(type='CONNECTED')
                
                bpy.ops.armature.select_all(action='DESELECT')
        bpy.ops.armature.symmetrize()
        bpy.ops.object.editmode_toggle()
    
    # TRANSFORMING
    obj.name = file[:-4]
    obj.scale = (1,1,1)
    
    edited_body = False
    edited_tank = False
    edited_roll = False
    mat_body = None
    mat_tank = None
    mat_roll = None
    
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
        
        base_name = bpy.context.active_object.active_material.name
        to_edit=True
        
        if bpy.context.active_object.active_material.name.startswith("M_Body") or bpy.context.active_object.active_material.name.endswith("Body"):
            if edited_body==True:
                to_edit = False
                bpy.context.active_object.active_material = mat_body
            else:
                base_name = "m_body"
                bpy.context.active_object.active_material.name = file[:-4] + " Body"
                mat_body = bpy.context.active_object.active_material
                edited_body=True
                to_edit = True
                
        if bpy.context.active_object.active_material.name.startswith("M_Tank") or bpy.context.active_object.active_material.name.endswith("Tank"):
            if edited_tank==True:
                to_edit = False
                bpy.context.active_object.active_material = mat_tank
            else:
                base_name = "m_tank"
                bpy.context.active_object.active_material.name = file[:-4] + " Tank"
                mat_tank = bpy.context.active_object.active_material
                edited_tank=True
                to_edit = True
                
        if bpy.context.active_object.active_material.name.startswith("M_Roll") or bpy.context.active_object.active_material.name.endswith("Roll"):
            if edited_roll==True:
                to_edit = False
                bpy.context.active_object.active_material = mat_roll
            else:
                base_name = "m_roll"
                bpy.context.active_object.active_material.name = file[:-4] + " Roll"
                mat_roll = bpy.context.active_object.active_material
                edited_roll=True
                to_edit = True
                
        if bpy.context.active_object.active_material.name.startswith("Obj_"):
            bpy.context.active_object.active_material.name = bpy.context.active_object.active_material.name[4:]
            base_name = bpy.context.active_object.active_material.name
        if bpy.context.active_object.active_material.name.endswith(".001") or bpy.context.active_object.active_material.name.endswith(".002") or bpy.context.active_object.active_material.name.endswith(".003"):
            bpy.context.active_object.active_material = bpy.data.materials[bpy.context.active_object.active_material.name[:-4]]
            to_edit=False
        
        if to_edit==True:
            
            nodes = bpy.context.active_object.active_material.node_tree.nodes
            links = bpy.context.active_object.active_material.node_tree.links
        
            for node in nodes:
                nodes.remove(node)
        
            output = nodes.new(type="ShaderNodeOutputMaterial")
            bsdf = nodes.new(type="ShaderNodeBsdfPrincipled")
            links.new(bsdf.outputs[0], output.inputs[0])

            mix_node = None
            alb_node = None
            inka_color = (self.ink_A[0], self.ink_A[1], self.ink_A[2], 1)
        
            for img_path in path_iterator( path ):
                if img_path.lower().startswith(base_name.lower()+"_"):
                    full_path = os.path.join( path, img_path )
                
                    bpy.ops.image.open(filepath = full_path)
                        
                    img_node = nodes.new(type="ShaderNodeTexImage")
                    img_node.image = bpy.data.images[img_path]
            
                    if img_path.endswith("tcl.png"):
                        mix_node = nodes.new(type="ShaderNodeMix")
                        mix_node.data_type = "RGBA"
                    
                        img_node.image.name = bpy.context.active_object.active_material.name + "_tcl"
                        img_node.image.colorspace_settings.name = 'Non-Color'
                        links.new(img_node.outputs[0], mix_node.inputs[0])
                    
                        if alb_node != None:
                            links.new(alb_node.outputs[0], mix_node.inputs[6])
                            mix_node.inputs[7].default_value = inka_color
                
                    if img_path.endswith("alb.png"):
                        
                        alb_node = img_node
                    
                        if mix_node != None:
                            img_node.image.name = bpy.context.active_object.active_material.name + "_alb"
                            links.new(img_node.outputs[0], mix_node.inputs[6])
                            mix_node.inputs[7].default_value = inka_color
                            
                    if img_path.endswith("mtl.png"):
                        img_node.image.name = bpy.context.active_object.active_material.name + "_mtl"
                        img_node.image.colorspace_settings.name = 'Non-Color'
                        links.new(img_node.outputs[0], bsdf.inputs[6])
                            
                    if img_path.endswith("spc.png"):
                        img_node.image.name = bpy.context.active_object.active_material.name + "_spc"
                        img_node.image.colorspace_settings.name = 'Non-Color'
                        links.new(img_node.outputs[0], bsdf.inputs[7])
                            
                    if img_path.endswith("rgh.png"):
                        img_node.image.name = bpy.context.active_object.active_material.name + "_rgh"
                        img_node.image.colorspace_settings.name = 'Non-Color'
                        links.new(img_node.outputs[0], bsdf.inputs[9])
                            
                    if img_path.endswith("emm.png"):
                        img_node.image.name = bpy.context.active_object.active_material.name + "_emm"
                        img_node.image.colorspace_settings.name = 'Non-Color'
                        links.new(img_node.outputs[0], bsdf.inputs[20])
                                
                    if img_path.endswith("opa.png"):
                        img_node.image.name = bpy.context.active_object.active_material.name + "_opa"
                        img_node.image.colorspace_settings.name = 'Non-Color'
                        links.new(img_node.outputs[0], bsdf.inputs[21])
                    
                    if img_path.endswith("alp.png"):
                        img_node.image.name = bpy.context.active_object.active_material.name + "_alp"
                        img_node.image.colorspace_settings.name = 'Non-Color'
                        links.new(img_node.outputs[0], bsdf.inputs[21])
            
                    if img_path.endswith("nrm.png"):
                        img_node.image.name = bpy.context.active_object.active_material.name + "_nrm"
                        nrm_node = nodes.new("ShaderNodeNormalMap")
                        img_node.image.colorspace_settings.name = 'Non-Color'
                        links.new(nrm_node.outputs[0], bsdf.inputs[22])
                        links.new(img_node.outputs[0], nrm_node.inputs[1])
                    
        
                if mix_node != None:
                    links.new(mix_node.outputs[2], bsdf.inputs["Base Color"])
                elif alb_node != None:
                    alb_node.image.name = bpy.context.active_object.active_material.name + "_alb"
                    links.new(alb_node.outputs["Color"], bsdf.inputs["Base Color"])
                elif mix_node == None and alb_node == None:
                    bsdf.inputs["Base Color"].default_value = inka_color
    
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    
    return {'FINISHED'}


from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty, FloatVectorProperty
from bpy.types import Operator

class import_weapon(Operator, ImportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "import_splatoon.weapon"
    bl_label = "Import Weapon"


    filter_glob: StringProperty(
        default="*.fbx",
        options={'HIDDEN'},
        maxlen=255,
    )

    ink_A: FloatVectorProperty(
        name="Team Color",
        description="The ink color of the imported weapon",
        default=(1, 0, 0),
        min=0.0, max=1.0,
        subtype='COLOR'
    )

    def execute(self, context):
        return create_weapon(self)


def menu_func_import(self, context):
    self.layout.operator(import_weapon.bl_idname, text="Splatoon Weapon")

def register():
    bpy.utils.register_class(import_weapon)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
def unregister():
    bpy.utils.unregister_class(import_weapon)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
if __name__ == "__main__":
    register()
