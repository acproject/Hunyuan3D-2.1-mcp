#!/usr/bin/env python3
"""
Blender MCP 完整场景创建示例

这个示例展示如何使用 Blender MCP 创建一个完整的 3D 场景，
包括多个对象、材质、灯光和相机设置。

使用方法:
    python complete_scene_example.py
"""

import asyncio
import logging
import sys
import json
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from blender_mcp.server import (
        start_blender_connection,
        get_scene_info,
        execute_blender_code,
        render_scene
    )
except ImportError as e:
    print(f"❌ 导入错误: {e}")
    print("请确保你在正确的目录中运行此脚本，并且已安装所需依赖")
    sys.exit(1)

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class MockContext:
    """模拟 MCP 上下文对象"""
    pass


class BlenderSceneBuilder:
    """
    Blender 场景构建器
    """
    
    def __init__(self):
        self.ctx = MockContext()
        self.objects_created = []
    
    async def initialize(self):
        """初始化 Blender 连接"""
        print("🔌 初始化 Blender 连接...")
        result = await start_blender_connection(self.ctx)
        print(f"连接结果: {result}")
        await asyncio.sleep(2)  # 等待 Blender 启动
        
        # 清理默认场景
        await self.clear_default_scene()
    
    async def clear_default_scene(self):
        """清理默认场景中的对象"""
        print("🧹 清理默认场景...")
        clear_script = """
import bpy

# 删除默认的立方体、灯光和相机
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# 清理孤立数据
bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)

print("默认场景已清理")
"""
        result = await execute_blender_code(self.ctx, clear_script)
        print(f"清理结果: {result}")
    
    async def create_ground_plane(self):
        """创建地面平面"""
        print("🏞️ 创建地面平面...")
        ground_script = """
import bpy
import bmesh

# 创建地面平面
bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, 0))
ground = bpy.context.active_object
ground.name = "Ground"

# 创建地面材质
mat = bpy.data.materials.new(name="GroundMaterial")
mat.use_nodes = True
bsdf = mat.node_tree.nodes["Principled BSDF"]
bsdf.inputs[0].default_value = (0.2, 0.8, 0.2, 1.0)  # 绿色
bsdf.inputs[7].default_value = 0.8  # 粗糙度

# 应用材质
ground.data.materials.append(mat)

print(f"地面平面已创建: {ground.name}")
"""
        result = await execute_blender_code(self.ctx, ground_script)
        self.objects_created.append("Ground")
        print(f"地面创建结果: {result}")
    
    async def create_building_blocks(self):
        """创建建筑积木"""
        print("🏗️ 创建建筑积木...")
        buildings_script = """
import bpy
import random

# 创建多个建筑积木
buildings = []
for i in range(5):
    # 随机位置和尺寸
    x = random.uniform(-8, 8)
    y = random.uniform(-8, 8)
    z_scale = random.uniform(1, 4)
    
    # 创建立方体
    bpy.ops.mesh.primitive_cube_add(
        size=2,
        location=(x, y, z_scale)
    )
    building = bpy.context.active_object
    building.name = f"Building_{i+1}"
    
    # 缩放建筑
    building.scale = (1, 1, z_scale)
    
    # 创建随机颜色材质
    mat = bpy.data.materials.new(name=f"BuildingMaterial_{i+1}")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    
    # 随机颜色
    color = (
        random.uniform(0.3, 0.9),
        random.uniform(0.3, 0.9),
        random.uniform(0.3, 0.9),
        1.0
    )
    bsdf.inputs[0].default_value = color
    bsdf.inputs[7].default_value = 0.3  # 粗糙度
    
    # 应用材质
    building.data.materials.append(mat)
    buildings.append(building.name)
    
    print(f"建筑 {building.name} 已创建在位置 ({x:.1f}, {y:.1f}, {z_scale:.1f})")

print(f"共创建了 {len(buildings)} 个建筑")
"""
        result = await execute_blender_code(self.ctx, buildings_script)
        for i in range(5):
            self.objects_created.append(f"Building_{i+1}")
        print(f"建筑创建结果: {result}")
    
    async def create_decorative_objects(self):
        """创建装饰对象"""
        print("🎨 创建装饰对象...")
        decorative_script = """
import bpy
import bmesh
import random
import math

# 创建一些球体作为装饰
for i in range(8):
    # 随机位置
    angle = (i / 8) * 2 * math.pi
    radius = random.uniform(6, 10)
    x = radius * math.cos(angle)
    y = radius * math.sin(angle)
    z = random.uniform(0.5, 2)
    
    # 创建球体
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=0.5,
        location=(x, y, z)
    )
    sphere = bpy.context.active_object
    sphere.name = f"Decoration_{i+1}"
    
    # 创建发光材质
    mat = bpy.data.materials.new(name=f"GlowMaterial_{i+1}")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    
    # 发光颜色
    emission_color = (
        random.uniform(0.5, 1.0),
        random.uniform(0.5, 1.0),
        random.uniform(0.5, 1.0),
        1.0
    )
    bsdf.inputs[0].default_value = emission_color
    bsdf.inputs[19].default_value = emission_color[:3]  # 发光颜色
    bsdf.inputs[20].default_value = 2.0  # 发光强度
    
    # 应用材质
    sphere.data.materials.append(mat)
    
    print(f"装饰球体 {sphere.name} 已创建")

# 创建一个中心的圆柱体
bpy.ops.mesh.primitive_cylinder_add(
    radius=1,
    depth=6,
    location=(0, 0, 3)
)
cylinder = bpy.context.active_object
cylinder.name = "CenterPillar"

# 为圆柱体创建金属材质
mat = bpy.data.materials.new(name="MetalMaterial")
mat.use_nodes = True
bsdf = mat.node_tree.nodes["Principled BSDF"]
bsdf.inputs[0].default_value = (0.8, 0.8, 0.9, 1.0)  # 金属色
bsdf.inputs[4].default_value = 1.0  # 金属度
bsdf.inputs[7].default_value = 0.1  # 粗糙度

cylinder.data.materials.append(mat)

print("装饰对象创建完成")
"""
        result = await execute_blender_code(self.ctx, decorative_script)
        for i in range(8):
            self.objects_created.append(f"Decoration_{i+1}")
        self.objects_created.append("CenterPillar")
        print(f"装饰对象创建结果: {result}")
    
    async def setup_lighting(self):
        """设置灯光"""
        print("💡 设置灯光系统...")
        lighting_script = """
import bpy
import math

# 创建太阳光
bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
sun = bpy.context.active_object
sun.name = "SunLight"
sun.data.energy = 3
sun.data.color = (1.0, 0.95, 0.8)  # 暖白色
sun.rotation_euler = (math.radians(45), 0, math.radians(45))

# 创建环境光
bpy.ops.object.light_add(type='AREA', location=(0, 0, 15))
area_light = bpy.context.active_object
area_light.name = "AreaLight"
area_light.data.energy = 50
area_light.data.size = 10
area_light.data.color = (0.8, 0.9, 1.0)  # 冷白色
area_light.rotation_euler = (0, 0, 0)

# 创建几个点光源作为装饰
for i in range(3):
    angle = (i / 3) * 2 * math.pi
    x = 8 * math.cos(angle)
    y = 8 * math.sin(angle)
    
    bpy.ops.object.light_add(type='POINT', location=(x, y, 4))
    point_light = bpy.context.active_object
    point_light.name = f"PointLight_{i+1}"
    point_light.data.energy = 100
    
    # 随机颜色
    if i == 0:
        point_light.data.color = (1.0, 0.3, 0.3)  # 红色
    elif i == 1:
        point_light.data.color = (0.3, 1.0, 0.3)  # 绿色
    else:
        point_light.data.color = (0.3, 0.3, 1.0)  # 蓝色

print("灯光系统设置完成")
"""
        result = await execute_blender_code(self.ctx, lighting_script)
        lights = ["SunLight", "AreaLight", "PointLight_1", "PointLight_2", "PointLight_3"]
        self.objects_created.extend(lights)
        print(f"灯光设置结果: {result}")
    
    async def setup_camera(self):
        """设置相机"""
        print("📷 设置相机...")
        camera_script = """
import bpy
import math

# 创建相机
bpy.ops.object.camera_add(location=(12, -12, 8))
camera = bpy.context.active_object
camera.name = "MainCamera"

# 设置相机朝向场景中心
camera.rotation_euler = (math.radians(60), 0, math.radians(45))

# 设置为活动相机
bpy.context.scene.camera = camera

# 调整相机设置
camera.data.lens = 35  # 焦距
camera.data.clip_start = 0.1
camera.data.clip_end = 1000

print(f"相机 {camera.name} 已设置")
"""
        result = await execute_blender_code(self.ctx, camera_script)
        self.objects_created.append("MainCamera")
        print(f"相机设置结果: {result}")
    
    async def setup_world_environment(self):
        """设置世界环境"""
        print("🌍 设置世界环境...")
        world_script = """
import bpy

# 设置世界环境
world = bpy.context.scene.world
world.use_nodes = True

# 获取世界节点
world_nodes = world.node_tree.nodes
world_links = world.node_tree.links

# 清除现有节点
world_nodes.clear()

# 创建背景节点
background_node = world_nodes.new(type='ShaderNodeBackground')
background_node.inputs[0].default_value = (0.1, 0.2, 0.4, 1.0)  # 深蓝色背景
background_node.inputs[1].default_value = 0.5  # 强度

# 创建输出节点
output_node = world_nodes.new(type='ShaderNodeOutputWorld')

# 连接节点
world_links.new(background_node.outputs[0], output_node.inputs[0])

print("世界环境设置完成")
"""
        result = await execute_blender_code(self.ctx, world_script)
        print(f"环境设置结果: {result}")
    
    async def add_animation(self):
        """添加简单动画"""
        print("🎬 添加动画...")
        animation_script = """
import bpy
import math

# 设置动画帧范围
bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = 120

# 为装饰球体添加旋转动画
for i in range(1, 9):
    obj_name = f"Decoration_{i}"
    if obj_name in bpy.data.objects:
        obj = bpy.data.objects[obj_name]
        
        # 设置关键帧
        bpy.context.scene.frame_set(1)
        obj.rotation_euler = (0, 0, 0)
        obj.keyframe_insert(data_path="rotation_euler", index=2)
        
        bpy.context.scene.frame_set(120)
        obj.rotation_euler = (0, 0, 2 * math.pi)
        obj.keyframe_insert(data_path="rotation_euler", index=2)
        
        # 设置插值为线性
        if obj.animation_data and obj.animation_data.action:
            for fcurve in obj.animation_data.action.fcurves:
                for keyframe in fcurve.keyframe_points:
                    keyframe.interpolation = 'LINEAR'

# 为中心柱子添加上下浮动动画
if "CenterPillar" in bpy.data.objects:
    pillar = bpy.data.objects["CenterPillar"]
    
    bpy.context.scene.frame_set(1)
    pillar.location[2] = 3
    pillar.keyframe_insert(data_path="location", index=2)
    
    bpy.context.scene.frame_set(60)
    pillar.location[2] = 4
    pillar.keyframe_insert(data_path="location", index=2)
    
    bpy.context.scene.frame_set(120)
    pillar.location[2] = 3
    pillar.keyframe_insert(data_path="location", index=2)
    
    # 设置插值为贝塞尔
    if pillar.animation_data and pillar.animation_data.action:
        for fcurve in pillar.animation_data.action.fcurves:
            for keyframe in fcurve.keyframe_points:
                keyframe.interpolation = 'BEZIER'

print("动画设置完成")
"""
        result = await execute_blender_code(self.ctx, animation_script)
        print(f"动画设置结果: {result}")
    
    async def render_scene_views(self):
        """渲染多个视角"""
        print("🎨 渲染场景...")
        
        # 设置渲染参数
        render_setup_script = """
import bpy

# 设置渲染引擎为 Cycles
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 64  # 降低采样以加快渲染

# 设置渲染分辨率
bpy.context.scene.render.resolution_x = 1280
bpy.context.scene.render.resolution_y = 720
bpy.context.scene.render.resolution_percentage = 100

# 设置输出格式
bpy.context.scene.render.image_settings.file_format = 'PNG'

print("渲染设置完成")
"""
        await execute_blender_code(self.ctx, render_setup_script)
        
        # 渲染主视角
        main_render_path = str(Path("./complete_scene_main.png").absolute())
        result = await render_scene(self.ctx, main_render_path, [1280, 720])
        print(f"主视角渲染结果: {result}")
        
        # 创建并渲染俯视角
        top_view_script = """
import bpy
import math

# 移动相机到俯视位置
camera = bpy.data.objects["MainCamera"]
camera.location = (0, 0, 20)
camera.rotation_euler = (0, 0, 0)

print("相机已移动到俯视位置")
"""
        await execute_blender_code(self.ctx, top_view_script)
        
        top_render_path = str(Path("./complete_scene_top.png").absolute())
        result = await render_scene(self.ctx, top_render_path, [1280, 720])
        print(f"俯视角渲染结果: {result}")
        
        # 恢复原始相机位置
        restore_camera_script = """
import bpy
import math

camera = bpy.data.objects["MainCamera"]
camera.location = (12, -12, 8)
camera.rotation_euler = (math.radians(60), 0, math.radians(45))

print("相机位置已恢复")
"""
        await execute_blender_code(self.ctx, restore_camera_script)
    
    async def get_final_scene_info(self):
        """获取最终场景信息"""
        print("📋 获取最终场景信息...")
        scene_info = await get_scene_info(self.ctx)
        
        # 解析场景信息
        try:
            info_data = json.loads(scene_info)
            print(f"\n📊 场景统计:")
            print(f"  - 对象总数: {len(info_data.get('objects', []))}")
            print(f"  - 网格对象: {len([obj for obj in info_data.get('objects', []) if obj.get('type') == 'MESH'])}")
            print(f"  - 灯光对象: {len([obj for obj in info_data.get('objects', []) if obj.get('type') == 'LIGHT'])}")
            print(f"  - 相机对象: {len([obj for obj in info_data.get('objects', []) if obj.get('type') == 'CAMERA'])}")
            print(f"  - 材质数量: {len(info_data.get('materials', []))}")
        except json.JSONDecodeError:
            print(f"场景信息: {scene_info[:500]}...")
    
    async def save_blend_file(self):
        """保存 Blender 文件"""
        print("💾 保存 Blender 文件...")
        save_script = f"""
import bpy
import os

# 保存文件
blend_path = r"{Path('./complete_scene.blend').absolute()}"
bpy.ops.wm.save_as_mainfile(filepath=blend_path)

print(f"场景已保存到: {{blend_path}}")
"""
        result = await execute_blender_code(self.ctx, save_script)
        print(f"保存结果: {result}")


async def main():
    """
    主函数 - 创建完整的 3D 场景
    """
    print("🎬 Blender MCP 完整场景创建示例")
    print("="*60)
    
    builder = BlenderSceneBuilder()
    
    try:
        # 初始化
        await builder.initialize()
        
        # 构建场景
        await builder.create_ground_plane()
        await builder.create_building_blocks()
        await builder.create_decorative_objects()
        await builder.setup_lighting()
        await builder.setup_camera()
        await builder.setup_world_environment()
        await builder.add_animation()
        
        # 渲染和保存
        await builder.render_scene_views()
        await builder.get_final_scene_info()
        await builder.save_blend_file()
        
        print("\n🎉 完整场景创建完成！")
        print("\n📁 生成的文件:")
        
        files_to_check = [
            "complete_scene_main.png",
            "complete_scene_top.png",
            "complete_scene.blend"
        ]
        
        for filename in files_to_check:
            filepath = Path(filename)
            if filepath.exists():
                print(f"  ✅ {filename} ({filepath.stat().st_size} bytes)")
            else:
                print(f"  ❌ {filename} (未找到)")
        
        print(f"\n📊 创建的对象: {len(builder.objects_created)}")
        print("对象列表:")
        for obj in builder.objects_created:
            print(f"  - {obj}")
        
    except Exception as e:
        logger.error(f"❌ 场景创建失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # 检查依赖
    try:
        import fastmcp
        print("✅ FastMCP 已安装")
    except ImportError:
        print("❌ FastMCP 未安装，请运行: pip install fastmcp")
        sys.exit(1)
    
    # 运行示例
    asyncio.run(main())