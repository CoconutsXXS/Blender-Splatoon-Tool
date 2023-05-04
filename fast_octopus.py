bl_info = {
    "name": "Splatoon Octopus",
    "author": "Coconuts XXS",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Add > Mesh > Octopus",
    "description": "Create a procedural Octopus in few clicks.",
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

def create_squid(self, context):

    armature = None
    
    bpy.ops.object.select_all(action='DESELECT')
    src_path=str(srcPath) + "/octopus.blend"
 
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
    
    body_mat = bpy.context.view_layer.objects.active.children[0].active_material
    body_mat.node_tree.nodes["Group"].inputs[0].default_value = inka_color
    body_mat.node_tree.nodes["Group"].inputs[2].default_value = inkb_color


class OBJECT_OT_add_squid(Operator, AddObjectHelper):
    bl_idname = "mesh.octopus"
    bl_label = "Add Octopus"
    bl_description = "Create a procedural Octopus."
    bl_options = {'REGISTER', 'UNDO'}
    
    name: bpy.props.StringProperty(
        name="Name",
        description="The octopus object name",
        maxlen=50,
        default="Octopus",
    )
    ink_A: FloatVectorProperty(  
       name="Ink Color",
       subtype='COLOR',
       default=(1, 0, 0),
       min=0.0, max=1.0,
       description="The octopus ink color"
    )
    ink_B: FloatVectorProperty(  
       name="Ennemie Ink Color",
       subtype='COLOR',
       default=(0, 1, 1),
       min=0.0, max=1.0,
       description="The octopus enemie ink color (when he take damages)"
    )

    def execute(self, context):
        create_squid(self, context)
        return {'FINISHED'}


# Registration
def add_squid_button(self, context):
    self.layout.operator(
        OBJECT_OT_add_squid.bl_idname,
        text="Octopus",
        icon='GHOST_ENABLED')

def register():
    bpy.utils.register_class(OBJECT_OT_add_squid)
    bpy.types.VIEW3D_MT_mesh_add.append(add_squid_button)
def unregister():
    bpy.utils.unregister_class(OBJECT_OT_add_squid)
    bpy.types.VIEW3D_MT_mesh_add.remove(add_squid_button)

if __name__ == "__main__":
    register()