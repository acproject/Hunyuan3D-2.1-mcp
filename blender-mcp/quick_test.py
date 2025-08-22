#!/usr/bin/env python3
"""
Blender MCP + Hunyuan3D 快速测试脚本

这个脚本提供了一个简单的测试界面，用于验证整个系统是否正常工作。

使用方法:
    python quick_test.py
"""

import requests
import json
import time
import os

def test_hunyuan3d_api():
    """测试 Hunyuan3D API 连接"""
    print("\n🔍 测试 Hunyuan3D API 连接...")
    try:
        response = requests.get("http://localhost:8081/health", timeout=5)
        if response.status_code == 200:
            print("✅ Hunyuan3D API 服务器连接正常")
            return True
        else:
            print(f"❌ Hunyuan3D API 服务器响应异常: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ 无法连接到 Hunyuan3D API 服务器: {e}")
        print("💡 请确保 Hunyuan3D API 服务器在 localhost:8081 运行")
        return False

def test_stable_diffusion_api():
    """测试 Stable Diffusion API 连接"""
    print("\n🔍 测试 Stable Diffusion API 连接...")
    try:
        response = requests.get("http://localhost:7860/", timeout=5)
        if response.status_code == 200:
            print("✅ Stable Diffusion API 服务器连接正常")
            return True
        else:
            print(f"❌ Stable Diffusion API 服务器响应异常: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ 无法连接到 Stable Diffusion API 服务器: {e}")
        print("💡 请确保 Stable Diffusion WebUI 在 localhost:7860 运行")
        return False

def generate_test_prompts():
    """生成测试提示词"""
    prompts = {
        "basic_test": """
# 基础连接测试
请执行以下测试来验证系统连接:

1. 使用 get_scene_info 工具检查 Blender 连接
2. 检查当前场景状态

如果成功，你应该看到当前 Blender 场景的详细信息。
        """,
        
        "simple_3d_generation": """
# 简单 3D 生成测试
请使用以下参数测试 3D 生成功能:

使用 create_3d_scene_from_text 工具:
- scene_description: "一个简单的红色立方体"
- generate_image: true
- image_prompt: "red cube, simple 3D object, white background"
- negative_prompt: "complex, detailed, realistic"
- image_width: 512
- image_height: 512
- remove_background: true
- texture: false
- seed: 42

这将测试完整的文本到3D工作流程。
        """,
        
        "step_by_step_test": """
# 分步骤测试
请按以下步骤测试分步骤工作流程:

步骤1 - 生成图像:
使用 generate_stable_diffusion_image 工具:
- prompt: "blue sphere, simple 3D object, white background"
- negative_prompt: "complex, realistic, detailed"
- width: 512
- height: 512
- seed: 123

步骤2 - 生成3D模型:
使用 generate_hunyuan3d_model 工具:
- 使用步骤1生成的图像路径
- remove_background: true
- texture: false
- seed: 123

步骤3 - 获取结果:
使用 get_viewport_screenshot 工具获取场景截图
        """,
        
        "scene_modification": """
# 场景修改测试
在导入3D模型后，请使用以下代码修改场景:

使用 execute_blender_code 工具:

```python
import bpy

# 获取所有导入的对象
imported_objs = [obj for obj in bpy.context.scene.objects 
                if obj.type == 'MESH' and 'hunyuan3d' in obj.name.lower()]

if imported_objs:
    obj = imported_objs[0]
    
    # 移动对象到中心
    obj.location = (0, 0, 1)
    
    # 添加简单的材质
    mat = bpy.data.materials.new(name="TestMaterial")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs[0].default_value = (0.8, 0.2, 0.2, 1.0)  # 红色
    
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)
    
    # 添加光源
    bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
    light = bpy.context.active_object
    light.data.energy = 5
    
    print(f"场景修改完成: {obj.name} 已移动并应用红色材质")
else:
    print("未找到导入的对象")
```
        """
    }
    
    return prompts

def save_test_prompts():
    """保存测试提示词到文件"""
    prompts = generate_test_prompts()
    
    # 创建测试目录
    test_dir = "test_prompts"
    os.makedirs(test_dir, exist_ok=True)
    
    # 保存每个测试提示词
    for name, prompt in prompts.items():
        filename = os.path.join(test_dir, f"{name}.md")
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(prompt)
        print(f"✅ 测试提示词已保存: {filename}")
    
    # 创建测试顺序说明
    readme_content = """
# 测试提示词使用指南

这些测试提示词按照复杂度递增的顺序排列，建议按以下顺序进行测试:

## 1. basic_test.md
- 测试基础连接
- 验证 Blender MCP 是否正常工作
- 预期结果: 显示当前 Blender 场景信息

## 2. simple_3d_generation.md
- 测试完整的文本到3D工作流程
- 使用简单的几何体进行测试
- 预期结果: 生成红色立方体并导入 Blender

## 3. step_by_step_test.md
- 测试分步骤工作流程
- 分别测试图像生成和3D转换
- 预期结果: 生成蓝色球体并导入 Blender

## 4. scene_modification.md
- 测试 Blender 场景修改功能
- 在导入模型后进行材质和光照设置
- 预期结果: 对象移动到中心并应用红色材质

## 使用方法

1. 确保所有服务都在运行:
   - Hunyuan3D API (localhost:8081)
   - Stable Diffusion WebUI (localhost:7860)
   - Blender MCP 服务器

2. 在 MCP 客户端中按顺序执行测试提示词

3. 观察每个测试的结果，确保功能正常

## 故障排除

如果测试失败，请检查:
- 服务器连接状态
- API 端点是否正确
- Blender 插件是否正确安装
- 网络连接是否正常
    """
    
    readme_path = os.path.join(test_dir, "README.md")
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    print(f"✅ 测试指南已保存: {readme_path}")

def run_connectivity_tests():
    """运行连接性测试"""
    print("\n🚀 开始系统连接性测试...")
    
    results = {
        "hunyuan3d": test_hunyuan3d_api(),
        "stable_diffusion": test_stable_diffusion_api()
    }
    
    print("\n📊 测试结果汇总:")
    print("─" * 40)
    
    all_passed = True
    for service, passed in results.items():
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{service:20} {status}")
        if not passed:
            all_passed = False
    
    print("─" * 40)
    
    if all_passed:
        print("\n🎉 所有服务连接正常！可以开始使用 MCP 提示词进行测试。")
        print("\n📝 建议的下一步:")
        print("1. 在 MCP 客户端中执行 test_prompts/basic_test.md 中的提示词")
        print("2. 按照 test_prompts/README.md 中的顺序进行完整测试")
    else:
        print("\n⚠️  部分服务连接失败，请检查服务状态后重试。")
        print("\n🔧 故障排除建议:")
        if not results["hunyuan3d"]:
            print("- 启动 Hunyuan3D API 服务器: python app.py")
        if not results["stable_diffusion"]:
            print("- 启动 Stable Diffusion WebUI: python launch.py --api")
    
    return all_passed

def main():
    """主函数"""
    print("🎯 Blender MCP + Hunyuan3D 快速测试工具")
    print("\n这个工具将帮助你验证整个系统是否正常工作")
    
    while True:
        print("\n" + "="*50)
        print("请选择操作:")
        print("1. 运行连接性测试")
        print("2. 生成测试提示词文件")
        print("3. 显示系统状态检查")
        print("4. 退出")
        print("="*50)
        
        choice = input("\n请输入选择 (1-4): ").strip()
        
        if choice == "1":
            run_connectivity_tests()
        elif choice == "2":
            print("\n📝 生成测试提示词文件...")
            save_test_prompts()
            print("\n✅ 测试提示词文件已生成在 test_prompts/ 目录中")
        elif choice == "3":
            print("\n🔍 系统状态检查清单:")
            print("\n必需服务:")
            print("□ Hunyuan3D API 服务器 (localhost:8081)")
            print("□ Stable Diffusion WebUI (localhost:7860)")
            print("□ Blender MCP 服务器")
            print("□ Blender 应用程序")
            print("\n可选服务:")
            print("□ MCP 客户端 (如 Claude Desktop)")
            print("\n配置文件:")
            print("□ Blender MCP 配置")
            print("□ API 密钥设置")
        elif choice == "4":
            print("\n👋 测试完成，祝你使用愉快！")
            break
        else:
            print("\n❌ 无效选择，请重新输入")

if __name__ == "__main__":
    main()