
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
