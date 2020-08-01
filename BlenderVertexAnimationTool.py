bl_info = {
    "name": "blenderVertexAnimationTool",
    "author": "Silver Bullet",
    "version": (1, 0),
    "blender": (2, 83, 1),
    "location": "View3D > Object",
    "description": "Bake Vertex Animation and Normal Image",
    "warning": "",
    "doc_url": "",
    "category": "Animation",
}

import bpy
import bmesh
from bpy.types import Operator,Panel,PropertyGroup,AddonPreferences
from time import time
from itertools import chain
 
 
class Vertex_Animation(Operator):
    bl_idname = "object.vertex"
    bl_label = "bake"
    bl_space_type="VIEW_3D"
    bl_region_tape="UI"
    bl_description="bake vertex animation and normal"
    bl_options = {'REGISTER', 'UNDO'} 
    # Image information. Change these to your liking.
    def execute(self, context):
        NAME   = 'Vertex Animation Image'
        NORMAL = 'Normal Image'
        WIDTH  = len(bpy.context.active_object.data.vertices)
        HEIGHT = bpy.context.scene.frame_end - bpy.context.scene.frame_start + 1
        USE_ALPHA = True
        #edit uv
        ob = bpy.context.active_object
        me = ob.data
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.uv_texture_add() 
        bm = bmesh.from_edit_mesh(me)

        uv_layer = bm.loops.layers.uv.verify()

        # adjust uv coordinates
        for face in bm.faces:
            for loop in face.loops:
                loop_uv = loop[uv_layer]
                # use xy position of the vertex as a uv coordinate
                loop_uv.uv.x = loop.vert.index/WIDTH + (1/(2*WIDTH))
                loop_uv.uv.y = 0.5
                print(loop.vert.index)
        bmesh.update_edit_mesh(me) 
     
        # Optional, delete the image if it already exists.
        oldImage = bpy.data.images.get(NAME, None)
        if oldImage:
            bpy.data.images.remove(oldImage)
     
        # Create a new image.
        newImage = bpy.data.images.new(NAME, WIDTH, HEIGHT, alpha=USE_ALPHA)
     
     
        def generatePixels():
            for y in range(HEIGHT):
                bpy.context.scene.frame_set(HEIGHT-y)
                ob.update_from_editmode()
                depsgraph = bpy.context.evaluated_depsgraph_get()
                ob_eval = ob.evaluated_get(depsgraph)
                me = ob_eval.to_mesh()
                print(me.vertices[0].co)  
                print(bpy.context.scene.frame_current)  
                for a in range(WIDTH):
                    red = ((me.vertices[a].co.x-ob.data.vertices[a].co.x)+1) / 2 
                    green = ((me.vertices[a].co.y-ob.data.vertices[a].co.y)+1) / -2
                    blue = ((me.vertices[a].co.z-ob.data.vertices[a].co.z)+1) / 2
                    alpha = 1.0
                    yield red, green, blue, alpha
                ob_eval.to_mesh_clear()   
                
     
        start = time()
       
        newImage.pixels = tuple(chain.from_iterable(generatePixels()))
        print(newImage.pixels)
        newImage.update()
       
        print('TIME TAKEN: %f seconds' % (time() - start)) # Outputs to the system console.
     
        # All done.
        oldNormal = bpy.data.images.get(NORMAL, None)
        if oldNormal:
            bpy.data.images.remove(oldNormal)
     
        # Create a new image Nromal.
        newNormal = bpy.data.images.new(NORMAL, WIDTH, HEIGHT, alpha=USE_ALPHA)
     
     
        def generatePixelsNormal():
            for y in range(HEIGHT):
                bpy.context.scene.frame_set(HEIGHT-y)
                #ob = bpy.context.object
                ob.update_from_editmode()
                depsgraph = bpy.context.evaluated_depsgraph_get()
                ob_eval = ob.evaluated_get(depsgraph)
                me = ob_eval.to_mesh()
                for a in range(WIDTH):
                    red = (me.vertices[a].normal.x)*0.5 +0.5
                    green = (me.vertices[a].normal.y * -1)*0.5 +0.5
                    blue = (me.vertices[a].normal.z)*0.5 +0.5
                    alpha = 1.0
                    yield red, green, blue, alpha
                ob_eval.to_mesh_clear()   
                
       
        newNormal.pixels = tuple(chain.from_iterable(generatePixelsNormal()))
        newNormal.update() 
        
        for area in bpy.context.screen.areas:
            if area.type == 'IMAGE_EDITOR':
                for space in area.spaces:
                    if space.type == 'IMAGE_EDITOR':
                        space.image = newNormal
                    
        print('TIME TAKEN: %f seconds' % (time() - start)) # Outputs to the system console.  
        bpy.ops.object.mode_set(mode='OBJECT')
        return {'FINISHED'}
    
    
    
def menu_func(self, context):
    self.layout.operator(
        Vertex_Animation.bl_idname,
        text="bake vertex animation",
        icon='PLUGIN')

def register():
    bpy.utils.register_class(Vertex_Animation)
    #bpy.utils.register_manual_map(add_object_manual_map)
    bpy.types.VIEW3D_MT_object.append(menu_func)


def unregister():
    bpy.utils.unregister_class(Vertex_Animation)
    #bpy.utils.unregister_manual_map(add_object_manual_map)
    bpy.types.VIEW3D_MT_object.remove(menu_func)


if __name__ == "__main__":
    register()


