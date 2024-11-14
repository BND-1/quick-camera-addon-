bl_info = {
    "name": "快速摄像机锁定",
    "author": "杨庭毅",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "3D视图 > 工具栏",
    "description": "快速添加摄像机并锁定到视图",
    "category": "Camera",
}

import bpy
from bpy.types import Operator, Panel

# 定义添加摄像机并朝向选中物体的操作
class OBJECT_OT_add_camera_to_selected(Operator):
    bl_idname = "object.add_camera_to_selected"
    bl_label = "添加摄像机"
    bl_description = "为选中的物体添加一个对准的摄像机"
    
    def execute(self, context):
        # 检查是否有选中的物体
        if not context.selected_objects:
            self.report({'WARNING'}, "No object selected")
            return {'CANCELLED'}
        
        # 获取选中的物体
        target_object = context.selected_objects[0]
        
        # 获取当前3D视图空间
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                view3d = area.spaces[0]
                region_3d = view3d.region_3d
                break
        
        # 获取当前视图的位置和旋转
        view_matrix = region_3d.view_matrix
        camera_location = view_matrix.inverted().translation
        camera_rotation = view_matrix.inverted().to_euler()
        
        # 添加摄像机并设置到当前视图的确切位置和方向
        bpy.ops.object.camera_add(
            location=camera_location,
            rotation=camera_rotation
        )
        camera = context.active_object
        
        # 将新创建的摄像机设置为场景活动摄像机
        context.scene.camera = camera
        
        # 添加Track To约束以保持对准
        constraint = camera.constraints.new(type='TRACK_TO')
        constraint.target = target_object
        constraint.track_axis = 'TRACK_NEGATIVE_Z'
        constraint.up_axis = 'UP_Y'

        # 切换到摄像机视角
        bpy.ops.view3d.view_camera()

        return {'FINISHED'}

# 定义锁定摄像机到视图的操作
class OBJECT_OT_lock_camera_to_view(Operator):
    bl_idname = "object.lock_camera_to_view"
    bl_label = "锁定摄像机视图"
    bl_description = "锁定或解锁摄像机到当前视图"

    def execute(self, context):
        scene = context.scene
        camera = scene.camera

        if camera is None:
            self.report({'WARNING'}, "No camera in the scene")
            return {'CANCELLED'}
        
        # 切换摄像机的锁定状态
        scene.lock_camera_to_view = not scene.lock_camera_to_view

        # 遍历所有 3D 视图区域以更新锁定状态
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                space = area.spaces[0]
                space.lock_camera = scene.lock_camera_to_view
                break

        return {'FINISHED'}

# 添加新的操作类来切换摄像机对齐状态
class OBJECT_OT_toggle_camera_alignment(Operator):
    bl_idname = "object.toggle_camera_alignment"
    bl_label = "切换摄像机对齐"
    bl_description = "切换摄像是否对齐到选中物体"

    def execute(self, context):
        camera = context.scene.camera
        if not camera:
            self.report({'WARNING'}, "No camera in the scene")
            return {'CANCELLED'}

        # 检查是否有Track To约束
        track_constraint = None
        for constraint in camera.constraints:
            if constraint.type == 'TRACK_TO':
                track_constraint = constraint
                break

        if track_constraint:
            # 如果存在约束，删除它
            camera.constraints.remove(track_constraint)
        else:
            # 如果没有约束，添加新的约束
            if not context.selected_objects:
                self.report({'WARNING'}, "Please select an object to track")
                return {'CANCELLED'}
            
            target_object = context.selected_objects[0]
            constraint = camera.constraints.new(type='TRACK_TO')
            constraint.target = target_object
            constraint.track_axis = 'TRACK_NEGATIVE_Z'
            constraint.up_axis = 'UP_Y'

        return {'FINISHED'}

# 定义左侧工具栏面板
class VIEW3D_PT_camera_tool_panel(Panel):
    bl_label = "摄像机工具"
    bl_idname = "VIEW3D_PT_camera_tool_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'

    def draw(self, context):
        layout = self.layout
        layout.operator("object.add_camera_to_selected", 
                       text="添加摄像机", 
                       icon='CAMERA_DATA')
        
        # 只有当场景中有摄像机时才显示这些按钮
        if context.scene.camera:
            layout.operator("object.lock_camera_to_view", 
                          text="锁定视图", 
                          icon='LOCKED' if context.scene.lock_camera_to_view else 'UNLOCKED')
            layout.operator("object.toggle_camera_alignment", 
                          text="切换对齐", 
                          icon='CON_TRACKTO')

# 注册和注销功能
def register():
    bpy.utils.register_class(OBJECT_OT_add_camera_to_selected)
    bpy.utils.register_class(OBJECT_OT_lock_camera_to_view)
    bpy.utils.register_class(OBJECT_OT_toggle_camera_alignment)
    bpy.utils.register_class(VIEW3D_PT_camera_tool_panel)
    
    bpy.types.Scene.lock_camera_to_view = bpy.props.BoolProperty(
        name="锁定摄像机到视图",
        description="锁定摄像机到当前视图方向",
        default=False
    )

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_add_camera_to_selected)
    bpy.utils.unregister_class(OBJECT_OT_lock_camera_to_view)
    bpy.utils.unregister_class(OBJECT_OT_toggle_camera_alignment)
    bpy.utils.unregister_class(VIEW3D_PT_camera_tool_panel)
    
    del bpy.types.Scene.lock_camera_to_view

if __name__ == "__main__":
    register()
