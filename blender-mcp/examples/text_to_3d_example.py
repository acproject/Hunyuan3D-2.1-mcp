#!/usr/bin/env python3
"""
文本到3D场景生成示例

这个脚本展示了如何使用整合后的 Blender-MCP + Hunyuan3D 系统
从文本描述创建完整的3D场景。

使用方法:
    python text_to_3d_example.py
"""

import asyncio
import logging
from fastmcp import FastMCP
from blender_mcp.server import (
    create_3d_scene_from_text,
    generate_stable_diffusion_image,
    generate_hunyuan3d_model,
    execute_blender_code
)

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def example_complete_workflow():
    """
    示例1: 完整工作流程 - 从文本创建3D场景
    """
    print("\n=== 示例1: 完整工作流程 ===")
    print("创建一个可爱的卡通猫咪场景...")
    
    try:
        # 使用统一工作流程工具
        result = await create_3d_scene_from_text(
            ctx=None,  # 在实际使用中，这里需要传入正确的上下文
            scene_description="一只可爱的橙色卡通猫咪坐在绿色草地上，阳光明媚的日子",
            generate_image=True,
            image_prompt="cute orange cartoon cat sitting on green grass, sunny day, 3D render style",
            negative_prompt="dark, scary, realistic, low quality",
            image_width=512,
            image_height=512,
            remove_background=True,
            texture=True,
            seed=42
        )
        
        print(f"结果: {result}")
        
    except Exception as e:
        print(f"错误: {e}")


async def example_step_by_step():
    """
    示例2: 分步骤工作流程
    """
    print("\n=== 示例2: 分步骤工作流程 ===")
    print("分步骤创建现代椅子模型...")
    
    try:
        # 步骤1: 生成图像
        print("步骤1: 生成图像...")
        image_result = await generate_stable_diffusion_image(
            ctx=None,
            prompt="modern minimalist chair, white background, product photography, clean design",
            negative_prompt="complex decorations, dark background, cluttered",
            width=512,
            height=512,
            seed=123
        )
        print(f"图像生成结果: {image_result}")
        
        # 从结果中提取图像路径（实际实现中需要解析结果）
        # 这里假设我们有图像路径
        image_path = "temp_generated_image.png"  # 实际路径需要从上面的结果中提取
        
        # 步骤2: 转换为3D模型
        print("步骤2: 转换为3D模型...")
        model_result = await generate_hunyuan3d_model(
            ctx=None,
            image_path=image_path,
            remove_background=True,
            texture=True,
            seed=123
        )
        print(f"3D模型生成结果: {model_result}")
        
        # 步骤3: 在Blender中进一步编辑
        print("步骤3: 添加自定义材质...")
        blender_code = """
import bpy

# 选择最新导入的对象
objs = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
if objs:
    obj = max(objs, key=lambda x: x.name)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    
    # 创建新材质
    mat = bpy.data.materials.new(name="ModernChairMaterial")
    mat.use_nodes = True
    
    # 清除默认节点
    mat.node_tree.nodes.clear()
    
    # 添加节点
    bsdf = mat.node_tree.nodes.new(type='ShaderNodeBsdfPrincipled')
    output = mat.node_tree.nodes.new(type='ShaderNodeOutputMaterial')
    
    # 连接节点
    mat.node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    # 设置材质属性
    bsdf.inputs['Base Color'].default_value = (0.9, 0.9, 0.9, 1.0)  # 浅灰色
    bsdf.inputs['Metallic'].default_value = 0.1
    bsdf.inputs['Roughness'].default_value = 0.3
    
    # 应用材质
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)
    
    print(f"材质已应用到对象: {obj.name}")
else:
    print("未找到网格对象")
"""
        
        code_result = await execute_blender_code(
            ctx=None,
            code=blender_code
        )
        print(f"Blender代码执行结果: {code_result}")
        
    except Exception as e:
        print(f"错误: {e}")


async def example_batch_processing():
    """
    示例3: 批量处理多个对象
    """
    print("\n=== 示例3: 批量处理 ===")
    print("批量创建水果3D模型...")
    
    fruits = [
        {"name": "苹果", "color": "红色", "seed": 100},
        {"name": "香蕉", "color": "黄色", "seed": 200},
        {"name": "橙子", "color": "橙色", "seed": 300}
    ]
    
    for fruit in fruits:
        try:
            print(f"\n创建 {fruit['name']} 3D模型...")
            
            description = f"一个新鲜的{fruit['color']}{fruit['name']}，白色背景，产品摄影风格，高质量渲染"
            
            result = await create_3d_scene_from_text(
                ctx=None,
                scene_description=description,
                generate_image=True,
                image_width=512,
                image_height=512,
                remove_background=True,
                texture=True,
                seed=fruit['seed']
            )
            
            print(f"{fruit['name']} 创建完成: {result[:100]}...")  # 只显示前100个字符
            
        except Exception as e:
            print(f"创建 {fruit['name']} 时出错: {e}")


async def example_custom_scene_setup():
    """
    示例4: 自定义场景设置
    """
    print("\n=== 示例4: 自定义场景设置 ===")
    print("创建带有自定义环境的场景...")
    
    try:
        # 首先创建主要对象
        result = await create_3d_scene_from_text(
            ctx=None,
            scene_description="一个现代风格的咖啡杯，白色陶瓷材质",
            generate_image=True,
            seed=500
        )
        
        print("主要对象创建完成，现在设置自定义环境...")
        
        # 添加自定义环境设置
        environment_code = """
import bpy
import bmesh
from mathutils import Vector

# 清除默认立方体（如果存在）
if "Cube" in bpy.data.objects:
    bpy.data.objects.remove(bpy.data.objects["Cube"], do_unlink=True)

# 添加地面
bpy.ops.mesh.primitive_plane_add(size=10, location=(0, 0, -1))
ground = bpy.context.active_object
ground.name = "Ground"

# 为地面创建材质
ground_mat = bpy.data.materials.new(name="GroundMaterial")
ground_mat.use_nodes = True
bsdf = ground_mat.node_tree.nodes["Principled BSDF"]
bsdf.inputs['Base Color'].default_value = (0.8, 0.8, 0.9, 1.0)  # 浅蓝灰色
bsdf.inputs['Roughness'].default_value = 0.8
ground.data.materials.append(ground_mat)

# 设置更好的照明
# 删除默认灯光
if "Light" in bpy.data.objects:
    bpy.data.objects.remove(bpy.data.objects["Light"], do_unlink=True)

# 添加主光源
bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
sun = bpy.context.active_object
sun.data.energy = 5
sun.data.angle = 0.1
sun.name = "MainSun"

# 添加补光
bpy.ops.object.light_add(type='AREA', location=(-3, 2, 5))
fill_light = bpy.context.active_object
fill_light.data.energy = 2
fill_light.data.size = 3
fill_light.name = "FillLight"

# 添加背景光
bpy.ops.object.light_add(type='AREA', location=(0, -5, 3))
back_light = bpy.context.active_object
back_light.data.energy = 1
back_light.data.size = 4
back_light.name = "BackLight"

# 设置相机位置
if "Camera" in bpy.data.objects:
    camera = bpy.data.objects["Camera"]
    camera.location = (4, -4, 3)
    camera.rotation_euler = (1.1, 0, 0.785)

# 设置渲染引擎为Cycles以获得更好的效果
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 128

# 设置世界环境
world = bpy.context.scene.world
world.use_nodes = True
world_nodes = world.node_tree.nodes
world_nodes.clear()

# 添加环境纹理
env_tex = world_nodes.new(type='ShaderNodeTexEnvironment')
background = world_nodes.new(type='ShaderNodeBackground')
output = world_nodes.new(type='ShaderNodeOutputWorld')

# 连接节点
world.node_tree.links.new(background.outputs['Background'], output.inputs['Surface'])
background.inputs['Strength'].default_value = 0.5
background.inputs['Color'].default_value = (0.05, 0.05, 0.1, 1.0)  # 深蓝色背景

print("自定义环境设置完成")
"""
        
        code_result = await execute_blender_code(
            ctx=None,
            code=environment_code
        )
        
        print(f"环境设置完成: {code_result}")
        
    except Exception as e:
        print(f"错误: {e}")


async def main():
    """
    主函数 - 运行所有示例
    """
    print("Blender-MCP + Hunyuan3D 整合系统示例")
    print("=" * 50)
    
    # 注意: 在实际使用中，需要确保:
    # 1. Blender 正在运行并加载了 MCP 插件
    # 2. Hunyuan3D API 服务器在 http://localhost:8081 运行
    # 3. 所有必要的依赖已安装
    
    print("\n注意: 这些示例需要以下服务正在运行:")
    print("1. Blender (加载了 MCP 插件)")
    print("2. Hunyuan3D API 服务器 (http://localhost:8081)")
    print("3. 足够的 GPU 内存用于 Stable Diffusion")
    
    # 运行示例（在实际环境中取消注释）
    # await example_complete_workflow()
    # await example_step_by_step()
    # await example_batch_processing()
    # await example_custom_scene_setup()
    
    print("\n所有示例代码已准备就绪！")
    print("请确保所有服务正在运行，然后取消注释相应的示例函数调用。")


if __name__ == "__main__":
    asyncio.run(main())