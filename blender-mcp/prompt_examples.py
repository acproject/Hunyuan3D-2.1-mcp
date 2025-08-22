#!/usr/bin/env python3
"""
Blender MCP + Hunyuan3D 提示词示例脚本

这个脚本提供了多个实际可用的提示词示例，展示如何通过 MCP 调用
Hunyuan3D-2.1 生成 3D 模型并在 Blender 中进行修改。

使用方法:
    python prompt_examples.py
"""

import time

def print_separator(title):
    """打印分隔符"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60 + "\n")

def print_prompt(title, prompt):
    """打印格式化的提示词"""
    print(f"📝 {title}")
    print("-" * 40)
    print(prompt)
    print("\n")

def main():
    """主函数 - 展示各种提示词示例"""
    
    print_separator("Blender MCP + Hunyuan3D 提示词示例集合")
    
    # 示例 1: 完整工作流程
    print_prompt(
        "示例 1: 完整工作流程 - 创建卡通角色",
        """
请使用完整的文本到3D工作流程创建一个可爱的机器人角色：

场景描述："可爱的小机器人，圆润的设计，蓝白配色，大眼睛，友好的表情，卡通风格"

请执行以下步骤：
1. 使用 create_3d_scene_from_text 工具
2. 生成高质量的机器人图像
3. 使用 Hunyuan3D 转换为 3D 模型
4. 导入到 Blender 场景中
5. 自动添加合适的灯光和相机设置
6. 获取最终场景的视口截图

参数设置：
- 图像尺寸：512x512
- 移除背景：是
- 生成纹理：是
- 种子：42（确保可重复性）
        """
    )
    
    # 示例 2: 分步骤 - 家具创建
    print_prompt(
        "示例 2: 分步骤工作流程 - 现代椅子",
        """
步骤 1 - 生成椅子图像：
请使用 generate_stable_diffusion_image 工具生成图像：

提示词："modern scandinavian chair, minimalist design, light wood, white cushion, white background, product photography, clean lines"
负面提示词："complex decorations, dark colors, cluttered background, low quality, blurry"
图像尺寸：512x512
推理步数：20
引导比例：7.5
种子：123

步骤 2 - 转换为 3D 模型：
请使用 generate_hunyuan3d_model 工具：

参数：
- 使用刚才生成的图像
- 移除背景：是
- 生成纹理：是
- 八叉树分辨率：256
- 推理步数：5
- 引导比例：5.0
- 种子：123

步骤 3 - Blender 场景设置：
请使用 execute_blender_code 执行以下操作：

1. 将椅子模型居中放置
2. 创建一个简单的展示环境
3. 添加三点照明设置
4. 调整相机角度
5. 应用木质材质
6. 获取多角度渲染
        """
    )
    
    # 示例 3: 建筑元素
    print_prompt(
        "示例 3: 建筑元素 - 古典柱子",
        """
请创建一个古典建筑柱子的 3D 模型：

使用 create_3d_scene_from_text 工具：

场景描述："古典希腊式大理石柱子，科林斯柱头，精美雕刻细节，白色大理石材质"
图像提示词："classical greek corinthian column, white marble, architectural detail, museum quality, white background, professional photography"
负面提示词："modern, plastic, low quality, dark, damaged"

特殊要求：
- 图像尺寸：768x768（更高分辨率以捕捉细节）
- 高质量纹理生成
- 在 Blender 中添加真实的大理石材质
- 创建博物馆展示环境
- 使用戏剧性照明突出雕刻细节
        """
    )
    
    # 示例 4: 批量创建
    print_prompt(
        "示例 4: 批量创建 - 餐具套装",
        """
请批量创建一套现代餐具的 3D 模型：

物品列表：
1. 盘子 - "modern white ceramic plate, minimalist design, white background"
2. 杯子 - "modern white ceramic mug, simple handle, white background"
3. 碗 - "modern white ceramic bowl, clean lines, white background"

对每个物品执行：
1. 使用 generate_stable_diffusion_image 生成产品图像
2. 使用 generate_hunyuan3d_model 转换为 3D 模型
3. 导入到同一个 Blender 场景中

最后在 Blender 中：
1. 将所有餐具排列在餐桌上
2. 统一应用陶瓷材质
3. 创建餐厅环境
4. 设置温暖的照明
5. 渲染产品展示图
        """
    )
    
    # 示例 5: 角色动画准备
    print_prompt(
        "示例 5: 角色模型 - 动画准备",
        """
请创建一个适合动画的卡通角色：

场景描述："可爱的卡通猫咪，橙色毛发，大眼睛，坐姿，简单的卡通风格，适合动画"

步骤：
1. 使用 create_3d_scene_from_text 生成基础模型
2. 在 Blender 中进行动画准备：

请执行以下 Blender 代码：
```python
import bpy

# 选择导入的猫咪模型
objs = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
if objs:
    cat = max(objs, key=lambda x: x.name)
    bpy.context.view_layer.objects.active = cat
    cat.select_set(True)
    
    # 添加骨骼系统
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # 添加简单的骨骼
    bpy.ops.object.armature_add(location=(0, 0, 0))
    armature = bpy.context.active_object
    
    # 设置父子关系
    cat.select_set(True)
    armature.select_set(True)
    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.parent_set(type='ARMATURE_AUTO')
    
    print("角色动画准备完成")
```

3. 创建简单的测试动画
4. 渲染动画预览
        """
    )
    
    # 示例 6: 复杂场景组合
    print_prompt(
        "示例 6: 复杂场景 - 客厅环境",
        """
请创建一个完整的现代客厅场景：

主要家具（分别生成）：
1. 沙发："modern grey sectional sofa, minimalist design, white background"
2. 茶几："modern glass coffee table, metal legs, white background"
3. 书架："modern wooden bookshelf, scandinavian style, white background"
4. 台灯："modern table lamp, white shade, metal base, white background"

场景组合步骤：
1. 分别为每个家具生成 3D 模型
2. 在 Blender 中组合场景：

```python
import bpy
import bmesh
from mathutils import Vector

# 创建房间基础结构
bpy.ops.mesh.primitive_cube_add(size=10, location=(0, 0, 2.5))
room = bpy.context.active_object
room.name = "Room"

# 创建地板材质
mat_floor = bpy.data.materials.new(name="Floor")
mat_floor.use_nodes = True
bsdf = mat_floor.node_tree.nodes["Principled BSDF"]
bsdf.inputs[0].default_value = (0.8, 0.7, 0.6, 1.0)  # 木地板颜色

# 添加窗户光照
bpy.ops.object.light_add(type='AREA', location=(5, 0, 3))
window_light = bpy.context.active_object
window_light.data.energy = 10
window_light.data.size = 3

# 设置相机位置
bpy.ops.object.camera_add(location=(8, -8, 4))
camera = bpy.context.active_object
# 让相机看向房间中心
direction = Vector((0, 0, 0)) - camera.location
camera.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()

print("客厅场景基础设置完成")
```

3. 排列家具位置
4. 添加装饰品和植物
5. 设置真实的照明
6. 渲染高质量图像
        """
    )
    
    # 示例 7: 材质和纹理定制
    print_prompt(
        "示例 7: 高级材质 - 金属质感",
        """
请为导入的 3D 模型创建高级金属材质：

假设我们已经有一个导入的模型，请执行以下 Blender 代码来应用金属材质：

```python
import bpy

# 选择最新导入的对象
objs = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
if objs:
    obj = max(objs, key=lambda x: x.name)
    
    # 创建金属材质
    mat = bpy.data.materials.new(name="MetalMaterial")
    mat.use_nodes = True
    
    # 获取材质节点
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    # 清除默认节点
    nodes.clear()
    
    # 添加 Principled BSDF
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.location = (0, 0)
    
    # 设置金属属性
    bsdf.inputs['Base Color'].default_value = (0.7, 0.7, 0.8, 1.0)  # 银色
    bsdf.inputs['Metallic'].default_value = 1.0  # 完全金属
    bsdf.inputs['Roughness'].default_value = 0.1  # 很光滑
    
    # 添加噪声纹理用于细节
    noise = nodes.new(type='ShaderNodeTexNoise')
    noise.location = (-300, 0)
    noise.inputs['Scale'].default_value = 50.0
    
    # 连接噪声到粗糙度
    links.new(noise.outputs['Fac'], bsdf.inputs['Roughness'])
    
    # 添加输出节点
    output = nodes.new(type='ShaderNodeOutputMaterial')
    output.location = (300, 0)
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    # 应用材质到对象
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)
    
    print(f"金属材质已应用到 {obj.name}")
```

然后设置环境照明来展示金属效果：
1. 添加 HDRI 环境贴图
2. 调整世界材质
3. 渲染材质球展示
        """
    )
    
    # 示例 8: 故障排除
    print_prompt(
        "示例 8: 故障排除和调试",
        """
如果遇到问题，请按以下步骤排查：

1. 检查服务器状态：
请使用以下命令检查各个服务的状态：

```
# 检查 Hunyuan3D API 服务器
请访问 http://localhost:8081/health 检查 API 服务器状态

# 检查 Blender MCP 连接
请使用 get_scene_info 工具测试 Blender 连接

# 检查可用的 MCP 工具
请列出所有可用的 MCP 工具
```

2. 如果图像生成失败：
- 检查提示词是否清晰具体
- 尝试调整负面提示词
- 增加推理步数
- 检查 GPU 内存是否足够

3. 如果 3D 转换失败：
- 确保输入图像质量良好
- 检查 Hunyuan3D API 服务器日志
- 尝试降低分辨率设置
- 检查网络连接

4. 如果 Blender 导入失败：
- 检查 Blender 插件是否正确安装
- 确认 MCP 服务器连接正常
- 检查模型文件格式
- 查看 Blender 控制台错误信息
        """
    )
    
    print_separator("提示词示例展示完成")
    print("💡 提示：")
    print("1. 复制上述任何提示词直接使用")
    print("2. 根据需要调整参数和描述")
    print("3. 确保所有服务都在运行")
    print("4. 查看 PROMPT_USAGE_GUIDE.md 获取更多详细信息")
    print("\n🚀 开始创建你的 3D 世界吧！")

if __name__ == "__main__":
    main()