# ##### BEGIN GPL LICENSE BLOCK #####
#
#    A simple Blender-Addon to render multiple objects in the same scene.
#    Copyright (C) 2021  Quacksilber
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
    "name": "Batch Render Objects",
    "author": "Quacksilber",
    "version": (1, 3),
    "blender": (3, 10, 0),
    "description": "Imports and renders a set of external 3D-models.",
    "category": "Render",
}


import bpy
import os
import time


class MyPanel(bpy.types.Panel):
    """TestTestTest"""
    bl_label = "Batch Render Objects"
    bl_idname = "SCENE_PT_layout"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "output"
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        layout.prop_search(scene, "selected_mat", bpy.data, "materials", text="Override Material")

        row = layout.row()
        row.scale_y = 2.0
        row.operator("object.batch_render_objects_import")
        
        
def override_materials_of_collection(context):
    scene = context.scene
    material = bpy.data.materials.get(scene.selected_mat)
    if material is None:
        return
    
    for collection in scene.collection.children:
        if collection.name == "tmp-collection-BRO-Addon":
            for obj in collection.all_objects:
                print("obj: ", obj.name)
                obj.active_material = material


def read_files(context, directory, files, axis_up_setting, axis_forward_setting):
    
    # try to set master-collection as active collection
    # (necessary for script to work, as tmp-collections are being created in the master-collection)
    scene_collection = bpy.context.view_layer.layer_collection
    bpy.context.view_layer.active_layer_collection = scene_collection
    
    
    def import_obj(filepath):
        try:
            #open obj file
            bpy.ops.import_scene.obj(filepath = filepath, axis_up = axis_up_setting, axis_forward = axis_forward_setting)

            for obj in bpy.context.selected_objects:
                collection.objects.link(obj)
                bpy.context.scene.collection.objects.unlink(obj)
                
        except Exception as e:
            print(e)
            
    def import_fbx(filepath):
        try:
            #open obj file
            bpy.ops.import_scene.fbx(filepath = filepath, axis_up = axis_up_setting, axis_forward = axis_forward_setting)

            for obj in bpy.context.selected_objects:
                collection.objects.link(obj)
                bpy.context.scene.collection.objects.unlink(obj)
                
        except Exception as e:
            print(e)
    
    def import_blend(filepath):
        try:
            #open .blend-files
            with bpy.data.libraries.load(filepath) as (data_from, data_to):
                data_to.objects = [name for name in data_from.objects]
            # link all objects
            for obj in data_to.objects:
                collection.objects.link(obj)
        except Exception as e:
            print(e)
    
    def import_stl(filepath):
        try:
            #open obj file
            bpy.ops.import_mesh.stl(filepath = filepath, axis_up = axis_up_setting, axis_forward = axis_forward_setting)
            
            for obj in bpy.context.selected_objects:
                collection.objects.link(obj)
                bpy.context.scene.collection.objects.unlink(obj)
                
        except Exception as e:
            print(e)
    
    for file in files: 
    
        filename, extension = os.path.splitext(file.name)
   
        filepath = os.path.join(directory, file.name)
   
        # create a temporary collection, to store the objects
        collection = bpy.data.collections.new("tmp-collection-BRO-Addon")
        scene = context.scene
        scene.collection.children.link(collection)
   
        if extension == ".blend":
            import_blend(filepath)
        elif extension == ".obj":
            import_obj(filepath)
        elif extension == ".stl":
            import_stl(filepath)
        elif extension == ".fbx":
            import_fbx(filepath)
        else:
            print("Unknown Extension!")
   
   
        # if an override material is set, apply it to each object in tmp collection
        override_materials_of_collection(context)
   
   
        # set output name
        scene.render.filepath = "//output/"+filename
        # render the image
        bpy.ops.render.render(write_still=True)
        
        # unlink all models from tmp-collection
        for c in scene.collection.children:
            if c.name == "tmp-collection-BRO-Addon":
                scene.collection.children.unlink(c)

        # remove all collections
        for c in bpy.data.collections:
            if not c.users:
                bpy.data.collections.remove(c)

    return {'FINISHED'}  




# ImportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ImportHelper
from bpy.props import CollectionProperty, StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator
class ImportExportBatchRenderObjects(Operator, ImportHelper):
    """Imports and renders a set of external 3D-models."""
    bl_idname = "object.batch_render_objects_import"
    bl_label = "Select Files to Render"


    # ImportHelper mixin class uses this
    filename_ext = ".blend;.obj;.stl;.fbx"

    files: CollectionProperty(
                type=bpy.types.OperatorFileListElement,
                options={'HIDDEN'}
            )


    directory = StringProperty(subtype='DIR_PATH')
    
    axis_up_setting: EnumProperty(
            name="Up",
            items=(('X', "X Up", ""),
                   ('Y', "Y Up", ""),
                   ('Z', "Z Up", ""),
                   ('-X', "-X Up", ""),
                   ('-Y', "-Y Up", ""),
                   ('-Z', "-Z Up", ""),
                   ),
            default='Y',
            )
    
    axis_forward_setting: EnumProperty(
            name="Forward",
            items=(('X', "X Forward", ""),
                   ('Y', "Y Forward", ""),
                   ('Z', "Z Forward", ""),
                   ('-X', "-X Forward", ""),
                   ('-Y', "-Y Forward", ""),
                   ('-Z', "-Z Forward", ""),
                   ),
            default='-Z',
            )

    filter_glob: StringProperty(
        default="*.blend;*.obj;*.stl;*.fbx",
         #default='*.jpg;*.jpeg;*.png;*.tif;*.tiff;*.bmp',
        options={'HIDDEN'}
    )


    def execute(self, context):
        
        # get path from filepath
        path, file = os.path.split(self.filepath)
        
        return read_files(context, path, self.files, self.axis_up_setting, self.axis_forward_setting)



# Only needed if you want to add into a dynamic menu
def menu_func_import(self, context):
    self.layout.operator(ImportSomeData.bl_idname, text="Text Import Operator")


def register():
    bpy.utils.register_class(ImportExportBatchRenderObjects)
    bpy.utils.register_class(MyPanel)
    bpy.types.Scene.selected_mat = StringProperty(default="None") 

def unregister():
    bpy.utils.unregister_class(ImportExportBatchRenderObjects)
    bpy.utils.unregister_class(MyPanel)

if __name__ == "__main__":
    register()
