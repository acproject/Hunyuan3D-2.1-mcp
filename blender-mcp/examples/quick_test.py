#!/usr/bin/env python3
"""
Blender MCP 快速测试脚本

这个脚本提供了一个简单的方式来测试 Blender MCP 服务器的基本功能。
它会启动服务器并执行一些基本操作来验证一切正常工作。

使用方法:
    python quick_test.py
"""

import asyncio
import logging
import sys
import time
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from blender_mcp.server import (
        get_scene_info,
        execute_blender_code,
        get_object_info,
        get_viewport_screenshot
    )
except ImportError as e:
    print(f"❌ 导入错误: {e}")
    print("请确保你在正确的目录中运行此脚本，并且已安装所需依赖")
    sys.exit(1)

from fastmcp import Context

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class MockContext:
    """模拟 FastMCP Context"""
    def __init__(self):
        self.session = {}
        self.meta = {}
        
    def __repr__(self):
        return "<MockContext>"


async def test_basic_functionality():
    """
    测试基本功能
    """
    print("\n" + "="*60)
    print("🧪 Blender MCP 基本功能测试")
    print("="*60)
    
    ctx = MockContext()
    
    try:
        # 测试 1: 获取场景信息
        print("\n📋 测试 1: 获取场景信息...")
        scene_info = await get_scene_info(ctx)
        scene_info_text = scene_info.content[0].text if scene_info.content else str(scene_info)
        print(f"场景信息: {scene_info_text[:200]}..." if len(scene_info_text) > 200 else f"场景信息: {scene_info_text}")
        
        # 测试 2: 创建立方体
        print("\n📦 测试 2: 使用代码创建立方体...")
        cube_script = """
import bpy

# 创建立方体
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 1))
cube = bpy.context.active_object
cube.name = "TestCube"

print(f"立方体已创建: {cube.name}")
"""
        cube_result = await execute_blender_code(ctx, code=cube_script)
        cube_result_text = cube_result.content[0].text if cube_result.content else str(cube_result)
        print(f"创建结果: {cube_result_text}")
        
        # 测试 3: 获取对象信息
        print("\n🔍 测试 3: 获取立方体信息...")
        try:
            object_info = await get_object_info(ctx, object_name="TestCube")
            object_info_text = object_info.content[0].text if object_info.content else str(object_info)
            print(f"对象信息: {object_info_text[:200]}..." if len(object_info_text) > 200 else f"对象信息: {object_info_text}")
        except Exception as e:
            print(f"获取对象信息失败: {e}")
        
        # 测试 4: 获取视口截图
        print("\n📸 测试 4: 获取视口截图...")
        try:
            screenshot = await get_viewport_screenshot(ctx, max_size=400)
            print(f"截图获取成功，类型: {type(screenshot)}")
        except Exception as e:
            print(f"截图获取失败: {e}")
        
        # 测试 5: 删除对象
        print("\n🗑️ 测试 5: 删除测试立方体...")
        delete_script = """
import bpy

# 删除立方体
if "TestCube" in bpy.data.objects:
    bpy.data.objects.remove(bpy.data.objects["TestCube"], do_unlink=True)
    print("TestCube 已删除")
else:
    print("TestCube 不存在")
"""
        delete_result = await execute_blender_code(ctx, code=delete_script)
        delete_result_text = delete_result.content[0].text if delete_result.content else str(delete_result)
        print(f"删除结果: {delete_result_text}")
        
        # 测试 6: 再次获取场景信息
        print("\n📋 测试 6: 获取更新后的场景信息...")
        updated_scene = await get_scene_info(ctx)
        updated_scene_text = updated_scene.content[0].text if updated_scene.content else str(updated_scene)
        print(f"更新后场景: {updated_scene_text[:200]}..." if len(updated_scene_text) > 200 else f"更新后场景: {updated_scene_text}")
        
        print("\n✅ 所有基本功能测试完成！")
        
    except Exception as e:
        logger.error(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


async def test_multiple_objects():
    """
    测试创建多个对象
    """
    print("\n" + "="*60)
    print("🏗️ 多对象创建测试")
    print("="*60)
    
    ctx = MockContext()
    
    try:
        # 创建多个对象的脚本
        multi_objects_script = """
import bpy
import bmesh

# 清理现有对象
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# 创建多个立方体
objects_data = [
    {"name": "Cube1", "location": (2, 0, 0), "scale": (1, 1, 1)},
    {"name": "Cube2", "location": (-2, 0, 0), "scale": (1.5, 1.5, 1.5)},
    {"name": "Cube3", "location": (0, 2, 0), "scale": (0.5, 0.5, 2)},
    {"name": "Cube4", "location": (0, -2, 0), "scale": (2, 0.5, 0.5)},
]

created_objects = []
for obj_data in objects_data:
    bpy.ops.mesh.primitive_cube_add(
        size=2,
        location=obj_data["location"]
    )
    cube = bpy.context.active_object
    cube.name = obj_data["name"]
    cube.scale = obj_data["scale"]
    created_objects.append(cube.name)
    print(f"创建了 {cube.name} 在位置 {obj_data['location']}")

print(f"总共创建了 {len(created_objects)} 个对象: {created_objects}")
"""
        
        print("\n📦 创建多个对象...")
        result = await execute_blender_code(ctx, code=multi_objects_script)
        result_text = result.content[0].text if result.content else str(result)
        print(f"创建结果: {result_text}")
        
        # 获取场景信息
        print("\n📋 获取最终场景信息...")
        final_scene = await get_scene_info(ctx)
        final_scene_text = final_scene.content[0].text if final_scene.content else str(final_scene)
        print(f"最终场景: {final_scene_text[:300]}..." if len(final_scene_text) > 300 else f"最终场景: {final_scene_text}")
        
        # 获取视口截图
        print("\n📸 获取多对象场景截图...")
        try:
            screenshot = await get_viewport_screenshot(ctx, max_size=800)
            print(f"截图获取成功，类型: {type(screenshot)}")
        except Exception as e:
            print(f"截图获取失败: {e}")
        
        # 清理对象
        print("\n🗑️ 清理创建的对象...")
        cleanup_script = """
import bpy

# 删除所有网格对象
for obj in bpy.data.objects:
    if obj.type == 'MESH':
        bpy.data.objects.remove(obj, do_unlink=True)
        print(f"删除了对象: {obj.name}")

print("所有测试对象已清理")
"""
        cleanup_result = await execute_blender_code(ctx, code=cleanup_script)
        cleanup_result_text = cleanup_result.content[0].text if cleanup_result.content else str(cleanup_result)
        print(f"清理结果: {cleanup_result_text}")
        
        print("\n✅ 多对象测试完成！")
        
    except Exception as e:
        logger.error(f"❌ 多对象测试失败: {e}")
        import traceback
        traceback.print_exc()


async def test_error_handling():
    """
    测试错误处理
    """
    print("\n" + "="*60)
    print("🚨 错误处理测试")
    print("="*60)
    
    ctx = MockContext()
    
    try:
        # 测试获取不存在对象的信息
        print("\n🔍 测试获取不存在对象的信息...")
        try:
            result = await get_object_info(ctx, object_name="NonExistentObject")
            result_text = result.content[0].text if result.content else str(result)
            print(f"获取不存在对象信息的结果: {result_text}")
        except Exception as e:
            print(f"预期的错误: {e}")
        
        # 测试执行无效的 Blender 代码
        print("\n💻 测试执行无效的 Blender 代码...")
        try:
            invalid_script = """
# 这是一个会导致错误的脚本
import bpy
bpy.invalid_operation_that_does_not_exist()
"""
            result = await execute_blender_code(ctx, code=invalid_script)
            result_text = result.content[0].text if result.content else str(result)
            print(f"无效代码执行结果: {result_text}")
        except Exception as e:
            print(f"预期的错误: {e}")
        
        # 测试创建和删除对象的错误处理
        print("\n📦 测试对象操作的错误处理...")
        try:
            test_script = """
import bpy

# 创建一个测试立方体
bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
cube = bpy.context.active_object
cube.name = "TestCube"
print(f"创建了测试立方体: {cube.name}")

# 尝试创建同名对象（Blender会自动重命名）
bpy.ops.mesh.primitive_cube_add(location=(1, 1, 1))
cube2 = bpy.context.active_object
cube2.name = "TestCube"  # Blender会自动改为TestCube.001
print(f"创建了第二个立方体: {cube2.name}")

# 清理
for obj in bpy.data.objects:
    if obj.name.startswith("TestCube"):
        bpy.data.objects.remove(obj, do_unlink=True)
        print(f"删除了对象: {obj.name}")
"""
            result = await execute_blender_code(ctx, code=test_script)
            result_text = result.content[0].text if result.content else str(result)
            print(f"对象操作测试结果: {result_text}")
        except Exception as e:
            print(f"对象操作错误: {e}")
        
        print("\n✅ 错误处理测试完成！")
        
    except Exception as e:
        logger.error(f"❌ 错误处理测试失败: {e}")
        import traceback
        traceback.print_exc()


async def performance_test():
    """
    简单的性能测试
    """
    print("\n" + "="*60)
    print("⚡ 性能测试")
    print("="*60)
    
    ctx = MockContext()
    
    try:
        # 测试批量创建对象的性能
        num_objects = 10
        print(f"\n📦 批量创建 {num_objects} 个对象...")
        
        start_time = time.time()
        
        batch_create_script = f"""
import bpy

# 批量创建立方体
created_objects = []
for i in range({num_objects}):
    name = f"PerfTest_{{i}}"
    location = (i % 5, i // 5, 0)
    
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    cube = bpy.context.active_object
    cube.name = name
    cube.scale = (0.5, 0.5, 0.5)
    created_objects.append(cube.name)
    
print(f"批量创建了 {{len(created_objects)}} 个对象: {{created_objects}}")
"""
        
        result = await execute_blender_code(ctx, code=batch_create_script)
        creation_time = time.time() - start_time
        result_text = result.content[0].text if result.content else str(result)
        print(f"创建 {num_objects} 个对象耗时: {creation_time:.2f} 秒")
        print(f"平均每个对象: {creation_time/num_objects:.3f} 秒")
        print(f"创建结果: {result_text}")
        
        # 测试场景信息获取性能
        print("\n📋 测试场景信息获取性能...")
        start_time = time.time()
        
        for i in range(5):
            scene_info = await get_scene_info(ctx)
        
        info_time = time.time() - start_time
        print(f"获取场景信息 5 次耗时: {info_time:.2f} 秒")
        print(f"平均每次: {info_time/5:.3f} 秒")
        
        # 清理对象
        print("\n🗑️ 清理性能测试对象...")
        start_time = time.time()
        
        cleanup_script = """
import bpy

# 删除所有性能测试对象
deleted_count = 0
for obj in list(bpy.data.objects):
    if obj.name.startswith("PerfTest_"):
        bpy.data.objects.remove(obj, do_unlink=True)
        deleted_count += 1
        
print(f"删除了 {deleted_count} 个性能测试对象")
"""
        
        cleanup_result = await execute_blender_code(ctx, code=cleanup_script)
        deletion_time = time.time() - start_time
        cleanup_result_text = cleanup_result.content[0].text if cleanup_result.content else str(cleanup_result)
        print(f"删除对象耗时: {deletion_time:.2f} 秒")
        print(f"清理结果: {cleanup_result_text}")
        
        print("\n✅ 性能测试完成！")
        
    except Exception as e:
        logger.error(f"❌ 性能测试失败: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """
    主函数
    """
    print("🧪 Blender MCP 快速测试")
    print("这个脚本会测试 Blender MCP 服务器的各种功能")
    
    print("\n请选择测试:")
    print("1. 基本功能测试")
    print("2. 多对象创建测试")
    print("3. 错误处理测试")
    print("4. 性能测试")
    print("5. 运行所有测试")
    
    try:
        choice = input("\n输入选择 (1-5): ").strip()
        
        if choice == "1":
            await test_basic_functionality()
        elif choice == "2":
            await test_multiple_objects()
        elif choice == "3":
            await test_error_handling()
        elif choice == "4":
            await performance_test()
        elif choice == "5":
            await test_basic_functionality()
            await test_multiple_objects()
            await test_error_handling()
            await performance_test()
        else:
            print("❌ 无效选择，运行基本功能测试")
            await test_basic_functionality()
        
        print("\n🎉 测试完成！")
        print("\n📁 检查当前目录中的渲染文件:")
        for render_file in Path(".").glob("*render*.png"):
            print(f"  - {render_file}")
            
    except KeyboardInterrupt:
        print("\n👋 用户中断，退出")
    except Exception as e:
        logger.error(f"❌ 测试执行失败: {e}")
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
    
    # 运行测试
    asyncio.run(main())