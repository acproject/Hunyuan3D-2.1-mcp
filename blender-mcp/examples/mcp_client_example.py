#!/usr/bin/env python3
"""
Blender MCP 客户端示例

这个脚本展示了如何作为 MCP 客户端连接到 Blender MCP 服务器，
并调用各种工具来控制 Blender。

使用方法:
    1. 启动 Blender MCP 服务器: python -m blender_mcp.server
    2. 在另一个终端运行此客户端: python mcp_client_example.py
"""

import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class MCPClient:
    """
    简单的 MCP 客户端实现
    
    这个类展示了如何与 MCP 服务器进行通信
    """
    
    def __init__(self):
        self.reader = None
        self.writer = None
        self.request_id = 0
        
    async def connect(self, command: List[str]):
        """
        连接到 MCP 服务器
        
        Args:
            command: 启动服务器的命令列表
        """
        try:
            # 启动服务器进程
            process = await asyncio.create_subprocess_exec(
                *command,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            self.reader = process.stdout
            self.writer = process.stdin
            
            # 发送初始化请求
            await self._send_request("initialize", {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "roots": {"listChanged": True},
                    "sampling": {}
                },
                "clientInfo": {
                    "name": "blender-mcp-example",
                    "version": "1.0.0"
                }
            })
            
            # 读取初始化响应
            response = await self._read_response()
            logger.info(f"服务器初始化响应: {response}")
            
            # 发送 initialized 通知
            await self._send_notification("notifications/initialized", {})
            
            logger.info("✅ 成功连接到 MCP 服务器")
            return True
            
        except Exception as e:
            logger.error(f"❌ 连接失败: {e}")
            return False
    
    async def _send_request(self, method: str, params: Dict[str, Any]) -> int:
        """
        发送 JSON-RPC 请求
        """
        self.request_id += 1
        request = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": method,
            "params": params
        }
        
        message = json.dumps(request) + "\n"
        self.writer.write(message.encode())
        await self.writer.drain()
        
        return self.request_id
    
    async def _send_notification(self, method: str, params: Dict[str, Any]):
        """
        发送 JSON-RPC 通知（无需响应）
        """
        notification = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params
        }
        
        message = json.dumps(notification) + "\n"
        self.writer.write(message.encode())
        await self.writer.drain()
    
    async def _read_response(self) -> Dict[str, Any]:
        """
        读取 JSON-RPC 响应
        """
        line = await self.reader.readline()
        if not line:
            raise Exception("连接已关闭")
        
        return json.loads(line.decode().strip())
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """
        获取可用工具列表
        """
        await self._send_request("tools/list", {})
        response = await self._read_response()
        
        if "error" in response:
            raise Exception(f"获取工具列表失败: {response['error']}")
        
        return response.get("result", {}).get("tools", [])
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Any:
        """
        调用工具
        
        Args:
            name: 工具名称
            arguments: 工具参数
        
        Returns:
            工具执行结果
        """
        await self._send_request("tools/call", {
            "name": name,
            "arguments": arguments
        })
        
        response = await self._read_response()
        
        if "error" in response:
            raise Exception(f"工具调用失败: {response['error']}")
        
        return response.get("result", {})
    
    async def close(self):
        """
        关闭连接
        """
        if self.writer:
            self.writer.close()
            await self.writer.wait_closed()


async def demo_basic_operations():
    """
    演示基本操作
    """
    print("\n" + "="*60)
    print("🎯 演示基本 Blender 操作")
    print("="*60)
    
    client = MCPClient()
    
    try:
        # 连接到服务器
        server_command = [sys.executable, "-m", "blender_mcp.server"]
        if not await client.connect(server_command):
            return
        
        # 获取可用工具
        print("\n📋 获取可用工具...")
        tools = await client.list_tools()
        print(f"可用工具数量: {len(tools)}")
        for tool in tools:
            print(f"  - {tool['name']}: {tool['description']}")
        
        # 启动 Blender 连接
        print("\n🔌 启动 Blender 连接...")
        result = await client.call_tool("start_blender_connection", {})
        print(f"连接结果: {result}")
        
        # 获取场景信息
        print("\n📋 获取场景信息...")
        scene_info = await client.call_tool("get_scene_info", {})
        print(f"场景信息: {scene_info}")
        
        # 创建立方体
        print("\n📦 创建立方体...")
        cube_result = await client.call_tool("create_cube", {
            "name": "DemoCube",
            "location": [2, 0, 0],
            "scale": [1.5, 1.5, 1.5]
        })
        print(f"创建结果: {cube_result}")
        
        # 再次获取场景信息
        print("\n📋 获取更新后的场景信息...")
        updated_scene = await client.call_tool("get_scene_info", {})
        print(f"更新后的场景: {updated_scene}")
        
        # 渲染场景
        print("\n🎨 渲染场景...")
        render_path = str(Path("./examples/renders/demo_render.png").absolute())
        Path(render_path).parent.mkdir(parents=True, exist_ok=True)
        
        render_result = await client.call_tool("render_scene", {
            "output_path": render_path,
            "resolution": [1280, 720]
        })
        print(f"渲染结果: {render_result}")
        
        print("\n🎉 基本操作演示完成！")
        
    except Exception as e:
        logger.error(f"❌ 演示失败: {e}")
    finally:
        await client.close()


async def demo_scene_creation():
    """
    演示场景创建
    """
    print("\n" + "="*60)
    print("🏗️ 演示场景创建")
    print("="*60)
    
    client = MCPClient()
    
    try:
        # 连接到服务器
        server_command = [sys.executable, "-m", "blender_mcp.server"]
        if not await client.connect(server_command):
            return
        
        # 启动 Blender
        await client.call_tool("start_blender_connection", {})
        
        # 删除默认立方体
        print("\n🗑️ 清理默认场景...")
        await client.call_tool("delete_object", {"object_name": "Cube"})
        
        # 创建一个简单的场景
        print("\n🏗️ 创建场景元素...")
        
        # 地面
        await client.call_tool("create_cube", {
            "name": "Ground",
            "location": [0, 0, -1],
            "scale": [5, 5, 0.1]
        })
        
        # 建筑物
        buildings = [
            {"name": "Tower1", "location": [2, 2, 1], "scale": [0.8, 0.8, 2]},
            {"name": "Tower2", "location": [-2, 2, 1.5], "scale": [0.8, 0.8, 3]},
            {"name": "Tower3", "location": [2, -2, 0.75], "scale": [0.8, 0.8, 1.5]},
            {"name": "Tower4", "location": [-2, -2, 2], "scale": [0.8, 0.8, 4]},
        ]
        
        for building in buildings:
            print(f"  创建 {building['name']}...")
            await client.call_tool("create_cube", building)
            await asyncio.sleep(0.5)  # 小延迟
        
        # 获取最终场景信息
        print("\n📋 最终场景信息...")
        final_scene = await client.call_tool("get_scene_info", {})
        print(f"场景对象数量: {len(json.loads(final_scene).get('objects', []))}")
        
        # 渲染最终场景
        print("\n🎨 渲染最终场景...")
        render_path = str(Path("./examples/renders/scene_demo.png").absolute())
        await client.call_tool("render_scene", {
            "output_path": render_path,
            "resolution": [1920, 1080]
        })
        
        print(f"\n🎉 场景创建完成！渲染保存到: {render_path}")
        
    except Exception as e:
        logger.error(f"❌ 场景创建失败: {e}")
    finally:
        await client.close()


async def interactive_demo():
    """
    交互式演示
    """
    print("\n" + "="*60)
    print("🎮 交互式 Blender MCP 演示")
    print("="*60)
    
    client = MCPClient()
    
    try:
        # 连接到服务器
        server_command = [sys.executable, "-m", "blender_mcp.server"]
        if not await client.connect(server_command):
            return
        
        # 启动 Blender
        print("\n🔌 启动 Blender...")
        await client.call_tool("start_blender_connection", {})
        
        while True:
            print("\n" + "-"*40)
            print("请选择操作:")
            print("1. 获取场景信息")
            print("2. 创建立方体")
            print("3. 删除对象")
            print("4. 渲染场景")
            print("5. 列出所有工具")
            print("6. 退出")
            
            try:
                choice = input("\n输入选择 (1-6): ").strip()
                
                if choice == "1":
                    result = await client.call_tool("get_scene_info", {})
                    print(f"\n场景信息:\n{json.dumps(json.loads(result), indent=2, ensure_ascii=False)}")
                
                elif choice == "2":
                    name = input("立方体名称: ").strip() or "NewCube"
                    x = float(input("X坐标 (默认0): ") or "0")
                    y = float(input("Y坐标 (默认0): ") or "0")
                    z = float(input("Z坐标 (默认0): ") or "0")
                    scale = float(input("缩放 (默认1): ") or "1")
                    
                    result = await client.call_tool("create_cube", {
                        "name": name,
                        "location": [x, y, z],
                        "scale": [scale, scale, scale]
                    })
                    print(f"\n创建结果: {result}")
                
                elif choice == "3":
                    name = input("要删除的对象名称: ").strip()
                    if name:
                        result = await client.call_tool("delete_object", {
                            "object_name": name
                        })
                        print(f"\n删除结果: {result}")
                
                elif choice == "4":
                    output = input("输出路径 (默认./render.png): ").strip() or "./render.png"
                    width = int(input("宽度 (默认1920): ") or "1920")
                    height = int(input("高度 (默认1080): ") or "1080")
                    
                    result = await client.call_tool("render_scene", {
                        "output_path": str(Path(output).absolute()),
                        "resolution": [width, height]
                    })
                    print(f"\n渲染结果: {result}")
                
                elif choice == "5":
                    tools = await client.list_tools()
                    print("\n可用工具:")
                    for tool in tools:
                        print(f"  - {tool['name']}: {tool['description']}")
                
                elif choice == "6":
                    print("\n👋 再见！")
                    break
                
                else:
                    print("❌ 无效选择，请重试")
                    
            except KeyboardInterrupt:
                print("\n👋 用户中断，退出")
                break
            except Exception as e:
                print(f"❌ 操作失败: {e}")
    
    except Exception as e:
        logger.error(f"❌ 交互式演示失败: {e}")
    finally:
        await client.close()


async def main():
    """
    主函数
    """
    print("🎨 Blender MCP 客户端演示")
    print("这个演示展示了如何作为客户端连接到 Blender MCP 服务器")
    
    # 确保渲染目录存在
    Path("./examples/renders").mkdir(parents=True, exist_ok=True)
    
    print("\n请选择演示:")
    print("1. 基本操作演示")
    print("2. 场景创建演示")
    print("3. 交互式演示")
    print("4. 运行所有演示")
    
    try:
        choice = input("\n输入选择 (1-4): ").strip()
        
        if choice == "1":
            await demo_basic_operations()
        elif choice == "2":
            await demo_scene_creation()
        elif choice == "3":
            await interactive_demo()
        elif choice == "4":
            await demo_basic_operations()
            await demo_scene_creation()
        else:
            print("❌ 无效选择，运行基本操作演示")
            await demo_basic_operations()
            
    except KeyboardInterrupt:
        print("\n👋 用户中断，退出")
    except Exception as e:
        logger.error(f"❌ 程序执行失败: {e}")


if __name__ == "__main__":
    asyncio.run(main())