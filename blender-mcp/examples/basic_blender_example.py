#!/usr/bin/env python3
"""
Blender MCP 基础使用示例

这个脚本展示了如何使用 Blender MCP 服务器的基本功能：
- 启动 Blender 连接
- 创建基本几何体
- 获取场景信息
- 渲染场景

使用方法:
    1. 确保 Blender 已安装并在 PATH 中
    2. 启动 Blender MCP 服务器
    3. 运行此脚本
"""

import asyncio
import json
import logging
import time
from pathlib import Path

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class BlenderMCPClient:
    """
    Blender MCP 客户端示例
    
    这个类展示了如何与 Blender MCP 服务器交互
    """
    
    def __init__(self):
        self.connected = False
        
    async def connect_to_blender(self):
        """
        连接到 Blender
        
        在实际使用中，这里会调用 MCP 服务器的 start_blender_connection 工具
        """
        logger.info("正在连接到 Blender...")
        
        # 模拟连接过程
        await asyncio.sleep(2)
        
        # 在实际实现中，这里会调用 MCP 工具
        # result = await mcp_client.call_tool("start_blender_connection", {})
        
        self.connected = True
        logger.info("✅ 成功连接到 Blender")
        return True
    
    async def get_scene_info(self):
        """
        获取当前场景信息
        """
        if not self.connected:
            logger.error("❌ 未连接到 Blender")
            return None
            
        logger.info("获取场景信息...")
        
        # 模拟场景信息
        scene_info = {
            "scene_name": "Scene",
            "objects": [
                {
                    "name": "Camera",
                    "type": "CAMERA",
                    "location": [7.36, -6.93, 4.96],
                    "rotation": [1.11, 0.0, 0.81],
                    "scale": [1.0, 1.0, 1.0]
                },
                {
                    "name": "Light",
                    "type": "LIGHT",
                    "location": [4.08, 1.01, 5.90],
                    "rotation": [0.65, 0.055, -0.11],
                    "scale": [1.0, 1.0, 1.0]
                },
                {
                    "name": "Cube",
                    "type": "MESH",
                    "location": [0.0, 0.0, 0.0],
                    "rotation": [0.0, 0.0, 0.0],
                    "scale": [1.0, 1.0, 1.0]
                }
            ],
            "materials": ["Material"],
            "cameras": ["Camera"],
            "lights": ["Light"]
        }
        
        logger.info(f"场景包含 {len(scene_info['objects'])} 个对象")
        return scene_info
    
    async def create_cube(self, name="MyCube", location=[0, 0, 0], scale=[1, 1, 1]):
        """
        创建一个立方体
        
        Args:
            name: 立方体名称
            location: 位置 [x, y, z]
            scale: 缩放 [x, y, z]
        """
        if not self.connected:
            logger.error("❌ 未连接到 Blender")
            return False
            
        logger.info(f"创建立方体 '{name}' 在位置 {location}，缩放 {scale}")
        
        # 在实际实现中，这里会调用 MCP 工具
        # result = await mcp_client.call_tool("create_cube", {
        #     "name": name,
        #     "location": location,
        #     "scale": scale
        # })
        
        await asyncio.sleep(1)  # 模拟创建时间
        logger.info(f"✅ 成功创建立方体 '{name}'")
        return True
    
    async def delete_object(self, object_name):
        """
        删除对象
        
        Args:
            object_name: 要删除的对象名称
        """
        if not self.connected:
            logger.error("❌ 未连接到 Blender")
            return False
            
        logger.info(f"删除对象 '{object_name}'")
        
        # 在实际实现中，这里会调用 MCP 工具
        # result = await mcp_client.call_tool("delete_object", {
        #     "object_name": object_name
        # })
        
        await asyncio.sleep(0.5)  # 模拟删除时间
        logger.info(f"✅ 成功删除对象 '{object_name}'")
        return True
    
    async def render_scene(self, output_path="./render.png", resolution=[1920, 1080]):
        """
        渲染场景
        
        Args:
            output_path: 输出文件路径
            resolution: 分辨率 [width, height]
        """
        if not self.connected:
            logger.error("❌ 未连接到 Blender")
            return False
            
        logger.info(f"渲染场景到 '{output_path}'，分辨率 {resolution[0]}x{resolution[1]}")
        
        # 在实际实现中，这里会调用 MCP 工具
        # result = await mcp_client.call_tool("render_scene", {
        #     "output_path": output_path,
        #     "resolution": resolution
        # })
        
        await asyncio.sleep(3)  # 模拟渲染时间
        logger.info(f"✅ 渲染完成，保存到 '{output_path}'")
        return True


async def basic_example():
    """
    基础示例：创建简单的3D场景
    """
    print("\n" + "="*50)
    print("🎯 基础示例：创建简单的3D场景")
    print("="*50)
    
    client = BlenderMCPClient()
    
    try:
        # 1. 连接到 Blender
        await client.connect_to_blender()
        
        # 2. 获取初始场景信息
        scene_info = await client.get_scene_info()
        if scene_info:
            print(f"\n📋 当前场景信息:")
            print(f"   场景名称: {scene_info['scene_name']}")
            print(f"   对象数量: {len(scene_info['objects'])}")
            print(f"   摄像机: {', '.join(scene_info['cameras'])}")
            print(f"   灯光: {', '.join(scene_info['lights'])}")
        
        # 3. 创建一些基本几何体
        await client.create_cube("RedCube", [2, 0, 0], [1, 1, 1])
        await client.create_cube("BlueCube", [-2, 0, 0], [1.5, 1.5, 1.5])
        await client.create_cube("GreenCube", [0, 2, 0], [0.5, 0.5, 2])
        
        # 4. 获取更新后的场景信息
        print("\n📋 添加对象后的场景信息:")
        updated_scene = await client.get_scene_info()
        if updated_scene:
            print(f"   对象数量: {len(updated_scene['objects'])}")
            for obj in updated_scene['objects']:
                if obj['type'] == 'MESH':
                    print(f"   - {obj['name']}: {obj['location']}")
        
        # 5. 渲染场景
        output_path = Path("./examples/renders/basic_scene.png")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        await client.render_scene(str(output_path), [1280, 720])
        
        print(f"\n🎉 基础示例完成！渲染图像保存到: {output_path}")
        
    except Exception as e:
        logger.error(f"❌ 示例执行失败: {e}")


async def advanced_example():
    """
    高级示例：创建复杂场景并进行动画
    """
    print("\n" + "="*50)
    print("🚀 高级示例：创建复杂场景")
    print("="*50)
    
    client = BlenderMCPClient()
    
    try:
        # 1. 连接到 Blender
        await client.connect_to_blender()
        
        # 2. 清理默认场景
        await client.delete_object("Cube")
        
        # 3. 创建一个小型城市场景
        print("\n🏗️ 创建城市场景...")
        
        # 创建地面
        await client.create_cube("Ground", [0, 0, -0.5], [10, 10, 0.1])
        
        # 创建建筑物
        buildings = [
            ("Building1", [2, 2, 1], [1, 1, 2]),
            ("Building2", [-2, 2, 1.5], [1, 1, 3]),
            ("Building3", [2, -2, 0.75], [1, 1, 1.5]),
            ("Building4", [-2, -2, 2], [1, 1, 4]),
            ("Building5", [0, 0, 1.25], [1.5, 1.5, 2.5])
        ]
        
        for name, location, scale in buildings:
            await client.create_cube(name, location, scale)
            await asyncio.sleep(0.2)  # 小延迟以便观察创建过程
        
        # 4. 创建多个视角的渲染
        render_configs = [
            ("overview", [1920, 1080]),
            ("closeup", [1280, 720]),
            ("wide", [2560, 1440])
        ]
        
        print("\n📸 渲染多个视角...")
        for view_name, resolution in render_configs:
            output_path = Path(f"./examples/renders/city_{view_name}.png")
            output_path.parent.mkdir(parents=True, exist_ok=True)
            await client.render_scene(str(output_path), resolution)
            await asyncio.sleep(1)
        
        print("\n🎉 高级示例完成！")
        print("📁 渲染文件保存在: ./examples/renders/")
        
    except Exception as e:
        logger.error(f"❌ 高级示例执行失败: {e}")


async def interactive_example():
    """
    交互式示例：让用户选择操作
    """
    print("\n" + "="*50)
    print("🎮 交互式示例")
    print("="*50)
    
    client = BlenderMCPClient()
    await client.connect_to_blender()
    
    while True:
        print("\n请选择操作:")
        print("1. 获取场景信息")
        print("2. 创建立方体")
        print("3. 删除对象")
        print("4. 渲染场景")
        print("5. 退出")
        
        try:
            choice = input("\n输入选择 (1-5): ").strip()
            
            if choice == "1":
                scene_info = await client.get_scene_info()
                if scene_info:
                    print(json.dumps(scene_info, indent=2, ensure_ascii=False))
            
            elif choice == "2":
                name = input("立方体名称: ").strip() or "NewCube"
                x = float(input("X坐标 (默认0): ") or "0")
                y = float(input("Y坐标 (默认0): ") or "0")
                z = float(input("Z坐标 (默认0): ") or "0")
                scale = float(input("缩放 (默认1): ") or "1")
                
                await client.create_cube(name, [x, y, z], [scale, scale, scale])
            
            elif choice == "3":
                name = input("要删除的对象名称: ").strip()
                if name:
                    await client.delete_object(name)
            
            elif choice == "4":
                output = input("输出路径 (默认./render.png): ").strip() or "./render.png"
                width = int(input("宽度 (默认1920): ") or "1920")
                height = int(input("高度 (默认1080): ") or "1080")
                
                await client.render_scene(output, [width, height])
            
            elif choice == "5":
                print("👋 再见！")
                break
            
            else:
                print("❌ 无效选择，请重试")
                
        except KeyboardInterrupt:
            print("\n👋 用户中断，退出")
            break
        except Exception as e:
            print(f"❌ 操作失败: {e}")


async def main():
    """
    主函数：运行所有示例
    """
    print("🎨 Blender MCP 使用示例")
    print("这些示例展示了如何使用 Blender MCP 服务器进行3D场景创建")
    
    print("\n请选择要运行的示例:")
    print("1. 基础示例 - 创建简单3D场景")
    print("2. 高级示例 - 创建复杂城市场景")
    print("3. 交互式示例 - 手动控制")
    print("4. 运行所有示例")
    
    try:
        choice = input("\n输入选择 (1-4): ").strip()
        
        if choice == "1":
            await basic_example()
        elif choice == "2":
            await advanced_example()
        elif choice == "3":
            await interactive_example()
        elif choice == "4":
            await basic_example()
            await advanced_example()
        else:
            print("❌ 无效选择，运行基础示例")
            await basic_example()
            
    except KeyboardInterrupt:
        print("\n👋 用户中断，退出")
    except Exception as e:
        logger.error(f"❌ 程序执行失败: {e}")


if __name__ == "__main__":
    # 创建必要的目录
    Path("./examples/renders").mkdir(parents=True, exist_ok=True)
    
    # 运行示例
    asyncio.run(main())