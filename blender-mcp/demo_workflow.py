#!/usr/bin/env python3
"""
Blender MCP + Hunyuan3D 演示工作流程

这个脚本演示了如何通过 MCP 调用实际使用 Hunyuan3D-2.1 生成 3D 模型
并导入到 Blender 中进行修改的完整工作流程。

使用方法:
    1. 确保 Hunyuan3D API 服务器在 localhost:8081 运行
    2. 确保 Blender MCP 服务器运行
    3. 确保 Blender 中安装了 MCP 插件
    4. 运行: python demo_workflow.py
"""

import time
import sys
import os

# 添加 blender-mcp 到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def print_step(step_num, title, description=""):
    """打印步骤信息"""
    print(f"\n{'='*60}")
    print(f"步骤 {step_num}: {title}")
    if description:
        print(f"描述: {description}")
    print(f"{'='*60}")

def print_result(result):
    """打印结果"""
    print(f"\n📋 结果:")
    print(f"{result}")
    print(f"\n{'─'*40}")

def wait_for_user():
    """等待用户确认"""
    input("\n按 Enter 键继续...")

def demo_complete_workflow():
    """演示完整工作流程"""
    print("\n🚀 Blender MCP + Hunyuan3D 完整工作流程演示")
    print("\n这个演示将展示如何从文本描述创建完整的 3D 场景")
    
    # 提示词示例
    scene_description = "一只可爱的橙色卡通猫咪坐在绿色草地上"
    
    print_step(1, "准备工作", "检查服务状态和连接")
    
    print("\n📝 请在 MCP 客户端中执行以下提示词:")
    print("\n" + "─"*50)
    print("请检查系统状态:")
    print("1. 使用 get_scene_info 工具检查 Blender 连接")
    print("2. 检查 Hunyuan3D API 服务器是否在 localhost:8081 运行")
    print("3. 确认所有必要的服务都已启动")
    print("─"*50)
    
    wait_for_user()
    
    print_step(2, "完整工作流程", "使用一键式文本到3D场景转换")
    
    prompt = f"""
请使用完整的文本到3D工作流程创建场景:

场景描述: "{scene_description}"

请执行以下操作:
1. 使用 create_3d_scene_from_text 工具
2. 参数设置:
   - scene_description: "{scene_description}"
   - generate_image: true
   - image_prompt: "cute orange cartoon cat sitting on green grass, sunny day, 3D render style, white background"
   - negative_prompt: "dark, scary, realistic, low quality, blurry"
   - image_width: 512
   - image_height: 512
   - remove_background: true
   - texture: true
   - seed: 42

这将自动完成:
- 图像生成
- 3D 模型转换
- Blender 导入
- 场景设置
- 灯光和相机配置
    """
    
    print("\n📝 请在 MCP 客户端中执行以下提示词:")
    print("\n" + "─"*50)
    print(prompt)
    print("─"*50)
    
    wait_for_user()
    
    print_step(3, "场景增强", "在 Blender 中进行进一步修改")
    
    enhancement_prompt = """
请在 Blender 中对导入的猫咪模型进行以下增强:

使用 execute_blender_code 工具执行以下代码:

```python
import bpy
import bmesh
from mathutils import Vector

# 选择猫咪对象
objs = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH' and 'hunyuan3d' in obj.name.lower()]
if objs:
    cat = objs[0]
    bpy.context.view_layer.objects.active = cat
    cat.select_set(True)
    
    # 调整猫咪位置和大小
    cat.location = (0, 0, 0.5)
    cat.scale = (1.2, 1.2, 1.2)
    
    # 创建草地
    bpy.ops.mesh.primitive_plane_add(size=6, location=(0, 0, 0))
    grass = bpy.context.active_object
    grass.name = "Grass"
    
    # 创建草地材质
    grass_mat = bpy.data.materials.new(name="GrassMaterial")
    grass_mat.use_nodes = True
    bsdf = grass_mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs[0].default_value = (0.2, 0.8, 0.2, 1.0)  # 绿色
    grass.data.materials.append(grass_mat)
    
    # 添加太阳光
    bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
    sun = bpy.context.active_object
    sun.data.energy = 5
    sun.rotation_euler = (0.785, 0, 0.785)  # 45度角
    
    # 调整相机位置
    if bpy.context.scene.camera:
        camera = bpy.context.scene.camera
        camera.location = (4, -4, 3)
        # 让相机看向猫咪
        direction = cat.location - camera.location
        camera.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    
    print("场景增强完成: 添加了草地、阳光和优化的相机角度")
else:
    print("未找到导入的猫咪模型")
```
    """
    
    print("\n📝 请在 MCP 客户端中执行以下提示词:")
    print("\n" + "─"*50)
    print(enhancement_prompt)
    print("─"*50)
    
    wait_for_user()
    
    print_step(4, "获取最终结果", "截图和场景信息")
    
    final_prompt = """
请获取最终场景的结果:

1. 使用 get_viewport_screenshot 工具获取当前场景截图
2. 使用 get_scene_info 工具获取场景信息
3. 显示最终的场景组成
    """
    
    print("\n📝 请在 MCP 客户端中执行以下提示词:")
    print("\n" + "─"*50)
    print(final_prompt)
    print("─"*50)
    
    wait_for_user()

def demo_step_by_step():
    """演示分步骤工作流程"""
    print("\n🔧 分步骤工作流程演示")
    print("\n这个演示将展示如何分步骤创建和修改 3D 模型")
    
    print_step(1, "图像生成", "使用 Stable Diffusion 生成产品图像")
    
    image_prompt = """
请使用 generate_stable_diffusion_image 工具生成一张现代椅子的图像:

参数:
- prompt: "modern scandinavian chair, light wood, white cushion, minimalist design, white background, product photography"
- negative_prompt: "complex decorations, dark colors, cluttered, low quality"
- width: 512
- height: 512
- num_inference_steps: 20
- guidance_scale: 7.5
- seed: 123
    """
    
    print("\n📝 请在 MCP 客户端中执行以下提示词:")
    print("\n" + "─"*50)
    print(image_prompt)
    print("─"*50)
    
    wait_for_user()
    
    print_step(2, "3D 模型生成", "使用 Hunyuan3D 转换图像为 3D 模型")
    
    model_prompt = """
请使用 generate_hunyuan3d_model 工具将刚才生成的图像转换为 3D 模型:

参数:
- 使用刚才生成的图像路径
- remove_background: true
- texture: true
- seed: 123
- octree_resolution: 256
- num_inference_steps: 5
- guidance_scale: 5.0

这将自动将生成的 3D 模型导入到 Blender 中。
    """
    
    print("\n📝 请在 MCP 客户端中执行以下提示词:")
    print("\n" + "─"*50)
    print(model_prompt)
    print("─"*50)
    
    wait_for_user()
    
    print_step(3, "Blender 场景设置", "创建展示环境")
    
    scene_prompt = """
请在 Blender 中为椅子创建一个展示环境:

使用 execute_blender_code 工具执行以下代码:

```python
import bpy
from mathutils import Vector

# 选择导入的椅子
objs = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH' and 'hunyuan3d' in obj.name.lower()]
if objs:
    chair = objs[0]
    bpy.context.view_layer.objects.active = chair
    chair.select_set(True)
    
    # 居中椅子
    chair.location = (0, 0, 0)
    
    # 创建地板
    bpy.ops.mesh.primitive_plane_add(size=8, location=(0, 0, -0.1))
    floor = bpy.context.active_object
    floor.name = "Floor"
    
    # 地板材质
    floor_mat = bpy.data.materials.new(name="FloorMaterial")
    floor_mat.use_nodes = True
    bsdf = floor_mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs[0].default_value = (0.9, 0.9, 0.9, 1.0)  # 浅灰色
    floor.data.materials.append(floor_mat)
    
    # 三点照明设置
    # 主光源
    bpy.ops.object.light_add(type='AREA', location=(3, -3, 4))
    key_light = bpy.context.active_object
    key_light.data.energy = 100
    key_light.data.size = 2
    
    # 补光
    bpy.ops.object.light_add(type='AREA', location=(-2, -1, 2))
    fill_light = bpy.context.active_object
    fill_light.data.energy = 30
    fill_light.data.size = 1.5
    
    # 背景光
    bpy.ops.object.light_add(type='AREA', location=(0, 3, 2))
    back_light = bpy.context.active_object
    back_light.data.energy = 20
    back_light.data.size = 1
    
    # 设置相机
    bpy.ops.object.camera_add(location=(4, -4, 2.5))
    camera = bpy.context.active_object
    direction = chair.location - camera.location
    camera.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.camera = camera
    
    print("椅子展示环境设置完成")
else:
    print("未找到导入的椅子模型")
```
    """
    
    print("\n📝 请在 MCP 客户端中执行以下提示词:")
    print("\n" + "─"*50)
    print(scene_prompt)
    print("─"*50)
    
    wait_for_user()
    
    print_step(4, "材质优化", "应用高质量木质材质")
    
    material_prompt = """
请为椅子应用高质量的木质材质:

使用 execute_blender_code 工具执行以下代码:

```python
import bpy

# 选择椅子对象
objs = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH' and 'hunyuan3d' in obj.name.lower()]
if objs:
    chair = objs[0]
    
    # 创建木质材质
    wood_mat = bpy.data.materials.new(name="WoodMaterial")
    wood_mat.use_nodes = True
    nodes = wood_mat.node_tree.nodes
    links = wood_mat.node_tree.links
    
    # 获取 Principled BSDF
    bsdf = nodes["Principled BSDF"]
    
    # 设置木质属性
    bsdf.inputs['Base Color'].default_value = (0.8, 0.6, 0.4, 1.0)  # 木色
    bsdf.inputs['Roughness'].default_value = 0.3
    bsdf.inputs['Specular'].default_value = 0.2
    
    # 添加噪声纹理模拟木纹
    noise = nodes.new(type='ShaderNodeTexNoise')
    noise.location = (-300, 0)
    noise.inputs['Scale'].default_value = 20.0
    noise.inputs['Detail'].default_value = 10.0
    
    # 添加 ColorRamp 调整木纹对比度
    color_ramp = nodes.new(type='ShaderNodeValToRGB')
    color_ramp.location = (-150, 0)
    
    # 连接节点
    links.new(noise.outputs['Fac'], color_ramp.inputs['Fac'])
    links.new(color_ramp.outputs['Color'], bsdf.inputs['Base Color'])
    
    # 应用材质
    if chair.data.materials:
        chair.data.materials[0] = wood_mat
    else:
        chair.data.materials.append(wood_mat)
    
    print(f"木质材质已应用到 {chair.name}")
else:
    print("未找到椅子模型")
```
    """
    
    print("\n📝 请在 MCP 客户端中执行以下提示词:")
    print("\n" + "─"*50)
    print(material_prompt)
    print("─"*50)
    
    wait_for_user()

def main():
    """主函数"""
    print("🎯 Blender MCP + Hunyuan3D 工作流程演示")
    print("\n这个演示脚本将指导你完成完整的 3D 创建工作流程")
    print("\n⚠️  重要提醒:")
    print("1. 确保 Hunyuan3D API 服务器在 localhost:8081 运行")
    print("2. 确保 Blender MCP 服务器运行")
    print("3. 确保 Blender 中安装了 MCP 插件")
    print("4. 在 MCP 客户端中执行显示的提示词")
    
    while True:
        print("\n" + "="*60)
        print("请选择演示类型:")
        print("1. 完整工作流程演示 (推荐新手)")
        print("2. 分步骤工作流程演示 (适合学习)")
        print("3. 查看提示词示例")
        print("4. 退出")
        print("="*60)
        
        choice = input("\n请输入选择 (1-4): ").strip()
        
        if choice == "1":
            demo_complete_workflow()
        elif choice == "2":
            demo_step_by_step()
        elif choice == "3":
            print("\n📚 请查看以下文件获取更多提示词示例:")
            print("- prompt_examples.py - 详细的提示词示例")
            print("- PROMPT_USAGE_GUIDE.md - 完整使用指南")
            print("- examples/ 目录 - 更多示例代码")
        elif choice == "4":
            print("\n👋 感谢使用 Blender MCP + Hunyuan3D!")
            break
        else:
            print("\n❌ 无效选择，请重新输入")

if __name__ == "__main__":
    main()