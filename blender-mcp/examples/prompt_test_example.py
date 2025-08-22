#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Blender MCP 提示词测试示例

这个脚本展示如何使用 Blender MCP 的提示词功能来创建 3D 场景。
不需要复杂的客户端代码，只需要使用自然语言描述即可。
"""

import asyncio
import json
from pathlib import Path

# 示例提示词
EXAMPLE_PROMPTS = {
    "简单场景": {
        "description": "创建一个简单的室内场景",
        "prompt": """
请帮我创建一个简单的室内场景：
1. 添加一个地面平面作为地板
2. 创建一个立方体作为桌子，放在地面上
3. 在桌子上放一个球体作为装饰品
4. 添加适当的灯光
5. 设置相机角度以获得好的视图
6. 最后渲染场景
"""
    },
    
    "复杂场景": {
        "description": "创建一个复杂的户外场景",
        "prompt": """
请创建一个户外公园场景：
1. 创建一个大的地面平面作为草地
2. 添加几个圆柱体作为树干
3. 在树干顶部添加球体作为树冠
4. 创建一条路径（使用拉长的立方体）
5. 添加一些装饰性的立方体作为长椅
6. 设置天空环境和阳光
7. 调整相机位置获得鸟瞰图
8. 渲染最终场景
"""
    },
    
    "动画场景": {
        "description": "创建带有简单动画的场景",
        "prompt": """
创建一个带有动画的场景：
1. 创建一个中心球体
2. 围绕它创建4个小立方体
3. 为中心球体添加旋转动画
4. 为立方体添加上下浮动动画
5. 设置适当的材质和颜色
6. 添加动态灯光
7. 渲染动画序列的几个关键帧
"""
    },
    
    "文本到3D": {
        "description": "从文本描述生成3D模型",
        "prompt": """
请使用文本到3D功能：
1. 使用描述 "一只可爱的小猫坐着" 生成3D模型
2. 将生成的模型导入到Blender场景中
3. 为模型添加适当的材质
4. 创建一个简单的背景环境
5. 设置灯光突出模型特征
6. 渲染最终结果
"""
    },
    
    "图像到3D": {
        "description": "从图像生成3D模型",
        "prompt": """
请使用图像到3D功能：
1. 首先生成一张物体图像，描述："一个现代风格的椅子，白色背景"
2. 使用生成的图像创建3D模型
3. 将模型导入Blender
4. 创建一个室内环境来展示椅子
5. 添加适当的灯光和材质
6. 从多个角度渲染椅子
"""
    }
}

def print_prompt_examples():
    """
    打印所有示例提示词
    """
    print("🎨 Blender MCP 提示词测试示例")
    print("=" * 60)
    print("\n以下是一些可以直接在支持 MCP 的 AI 助手中使用的提示词示例：")
    print("(比如 Claude Desktop、Cline 等)\n")
    
    for i, (name, example) in enumerate(EXAMPLE_PROMPTS.items(), 1):
        print(f"{i}. {name}")
        print(f"   描述: {example['description']}")
        print(f"   提示词:")
        print("   " + "-" * 50)
        # 缩进提示词内容
        prompt_lines = example['prompt'].strip().split('\n')
        for line in prompt_lines:
            print(f"   {line}")
        print("   " + "-" * 50)
        print()

def save_prompts_to_file():
    """
    将提示词保存到文件中
    """
    output_file = Path("blender_mcp_prompts.md")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Blender MCP 提示词示例\n\n")
        f.write("这些提示词可以直接在支持 MCP 的 AI 助手中使用，比如 Claude Desktop、Cline 等。\n\n")
        
        for name, example in EXAMPLE_PROMPTS.items():
            f.write(f"## {name}\n\n")
            f.write(f"**描述**: {example['description']}\n\n")
            f.write("**提示词**:\n\n")
            f.write("```\n")
            f.write(example['prompt'].strip())
            f.write("\n```\n\n")
            f.write("---\n\n")
    
    print(f"✅ 提示词已保存到: {output_file.absolute()}")

def create_test_script():
    """
    创建一个可以直接复制粘贴的测试脚本
    """
    test_script = """
# 🧪 Blender MCP 快速测试脚本
# 将以下内容复制粘贴到支持 MCP 的 AI 助手中

请使用 Blender MCP 执行以下测试：

1. **连接测试**
   - 获取当前 Blender 场景信息
   - 确认 MCP 服务器正常工作

2. **基础建模测试**
   ```python
   # 创建一个简单的场景
   import bpy
   
   # 清理默认场景
   bpy.ops.object.select_all(action='SELECT')
   bpy.ops.object.delete(use_global=False)
   
   # 创建地面
   bpy.ops.mesh.primitive_plane_add(size=10, location=(0, 0, 0))
   ground = bpy.context.active_object
   ground.name = "Ground"
   
   # 创建立方体
   bpy.ops.mesh.primitive_cube_add(location=(0, 0, 1))
   cube = bpy.context.active_object
   cube.name = "TestCube"
   
   # 创建球体
   bpy.ops.mesh.primitive_uv_sphere_add(location=(2, 0, 1))
   sphere = bpy.context.active_object
   sphere.name = "TestSphere"
   
   print("基础几何体创建完成")
   ```

3. **材质和灯光测试**
   - 为对象添加不同颜色的材质
   - 添加灯光设置
   - 调整相机位置

4. **渲染测试**
   - 获取视口截图
   - 检查渲染结果

5. **高级功能测试**（如果可用）
   - 测试 Stable Diffusion 图像生成
   - 测试 Hunyuan3D 模型生成
   - 测试 PolyHaven 资源下载

请逐步执行这些测试，并报告每个步骤的结果。
"""
    
    output_file = Path("blender_mcp_test_script.md")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(test_script)
    
    print(f"✅ 测试脚本已保存到: {output_file.absolute()}")
    return test_script

def main():
    """
    主函数
    """
    print("🎯 Blender MCP 提示词测试工具")
    print("=" * 60)
    print()
    print("选择操作:")
    print("1. 显示提示词示例")
    print("2. 保存提示词到文件")
    print("3. 创建测试脚本")
    print("4. 显示快速测试提示词")
    print("5. 全部执行")
    print()
    
    try:
        choice = input("请输入选择 (1-5): ").strip()
        
        if choice == "1":
            print_prompt_examples()
        elif choice == "2":
            save_prompts_to_file()
        elif choice == "3":
            create_test_script()
        elif choice == "4":
            show_quick_test_prompt()
        elif choice == "5":
            print_prompt_examples()
            print("\n" + "=" * 60)
            save_prompts_to_file()
            create_test_script()
            show_quick_test_prompt()
        else:
            print("❌ 无效选择")
            
    except KeyboardInterrupt:
        print("\n\n👋 再见！")
    except Exception as e:
        print(f"❌ 错误: {e}")

def show_quick_test_prompt():
    """
    显示一个可以直接使用的快速测试提示词
    """
    quick_prompt = """
🚀 快速测试提示词（直接复制使用）:

请使用 Blender MCP 帮我创建一个简单的测试场景：

1. 首先获取当前 Blender 场景信息，确认连接正常
2. 清理场景中的默认对象
3. 创建一个地面平面（10x10 单位）
4. 在地面上添加一个立方体（位置 0,0,1）
5. 添加一个球体（位置 2,0,1）
6. 为立方体设置红色材质，为球体设置蓝色材质
7. 添加一个灯光源
8. 调整相机角度以获得好的视图
9. 获取视口截图查看结果
10. 最后获取更新后的场景信息

请逐步执行并报告每个步骤的结果。如果遇到任何错误，请说明具体的错误信息。
"""
    
    print(quick_prompt)
    
    # 也保存到文件
    output_file = Path("quick_test_prompt.txt")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(quick_prompt)
    
    print(f"\n✅ 快速测试提示词已保存到: {output_file.absolute()}")

if __name__ == "__main__":
    main()