# Blender MCP 示例集合

这个目录包含了使用 Blender MCP 的各种示例，从基础功能测试到复杂的 3D 场景创建。

## 📋 示例列表

### 1. 快速测试 (`quick_test.py`)

**用途**: 测试 Blender MCP 服务器的基本功能

**功能**:
- 基本功能测试（连接、创建、删除、渲染）
- 多对象创建测试
- 错误处理测试
- 性能测试

**使用方法**:
```bash
cd blender-mcp/examples
python quick_test.py
```

**交互式菜单**:
1. 基本功能测试
2. 多对象创建测试
3. 错误处理测试
4. 性能测试
5. 运行所有测试

### 2. 完整场景示例 (`complete_scene_example.py`)

**用途**: 创建一个完整的 3D 场景，展示 Blender MCP 的高级功能

**功能**:
- 创建地面平面
- 生成随机建筑积木
- 添加装饰对象（发光球体、金属柱子）
- 设置多种灯光（太阳光、区域光、点光源）
- 配置相机和世界环境
- 添加动画效果
- 渲染多个视角
- 保存 Blender 文件

**使用方法**:
```bash
cd blender-mcp/examples
python complete_scene_example.py
```

**生成文件**:
- `complete_scene_main.png` - 主视角渲染
- `complete_scene_top.png` - 俯视角渲染
- `complete_scene.blend` - Blender 项目文件

### 3. 基础客户端示例 (`basic_blender_example.py`)

**用途**: 演示如何模拟 MCP 客户端调用

**功能**:
- 模拟 MCP 服务器调用
- 基础操作示例
- 高级场景创建
- 交互式操作

### 4. MCP 客户端示例 (`mcp_client_example.py`)

**用途**: 真实的 MCP 客户端实现

**功能**:
- 通过 stdio 连接到 MCP 服务器
- 发送和接收 MCP 消息
- 调用服务器工具
- 处理响应

### 5. 文本转 3D 示例 (`text_to_3d_example.py`)

**用途**: 展示 Blender MCP + Hunyuan3D 的集成功能

**功能**:
- 从文本描述生成图像
- 从图像生成 3D 模型
- 导入到 Blender 场景
- 完整的工作流程

## 🚀 快速开始

### 前置条件

1. **安装依赖**:
   ```bash
   pip install fastmcp
   ```

2. **确保 Blender 可访问**:
   - 系统 PATH 中有 Blender
   - 或者在环境变量中设置 `BLENDER_PATH`

3. **启动 Blender MCP 服务器**:
   ```bash
   cd blender-mcp/src
   python -m blender_mcp.server
   ```

### 运行示例

1. **新手推荐 - 快速测试**:
   ```bash
   python quick_test.py
   ```
   选择 "1" 进行基本功能测试

2. **进阶用户 - 完整场景**:
   ```bash
   python complete_scene_example.py
   ```
   自动创建复杂的 3D 场景

3. **开发者 - MCP 客户端**:
   ```bash
   python mcp_client_example.py
   ```
   了解 MCP 协议的使用

## 📖 详细说明

### 测试流程

1. **连接测试**: 验证与 Blender 的连接
2. **基础操作**: 创建、删除、修改对象
3. **场景信息**: 获取和解析场景数据
4. **渲染测试**: 生成图像输出
5. **错误处理**: 测试异常情况

### 场景创建流程

1. **初始化**: 清理默认场景
2. **基础几何**: 创建地面和基础对象
3. **材质系统**: 应用颜色和材质
4. **灯光设置**: 配置多种光源
5. **相机配置**: 设置视角和参数
6. **动画添加**: 创建简单动画
7. **渲染输出**: 生成最终图像

### 自定义和扩展

#### 修改场景参数

在 `complete_scene_example.py` 中，你可以修改：

```python
# 建筑数量
for i in range(5):  # 改为你想要的数量

# 装饰球体数量
for i in range(8):  # 改为你想要的数量

# 渲染分辨率
bpy.context.scene.render.resolution_x = 1280  # 宽度
bpy.context.scene.render.resolution_y = 720   # 高度

# 动画帧数
bpy.context.scene.frame_end = 120  # 总帧数
```

#### 添加新的对象类型

```python
async def create_custom_objects(self):
    """创建自定义对象"""
    custom_script = """
import bpy

# 创建圆环
bpy.ops.mesh.primitive_torus_add(
    major_radius=2,
    minor_radius=0.5,
    location=(0, 0, 5)
)
torus = bpy.context.active_object
torus.name = "CustomTorus"

# 添加材质...
"""
    result = await execute_blender_code(self.ctx, custom_script)
    return result
```

#### 自定义材质

```python
# 创建玻璃材质
mat = bpy.data.materials.new(name="GlassMaterial")
mat.use_nodes = True
bsdf = mat.node_tree.nodes["Principled BSDF"]
bsdf.inputs[0].default_value = (0.8, 0.9, 1.0, 1.0)  # 颜色
bsdf.inputs[15].default_value = 1.0  # 透明度
bsdf.inputs[4].default_value = 0.0   # 金属度
bsdf.inputs[7].default_value = 0.0   # 粗糙度
```

## 🔧 故障排除

### 常见问题

1. **ModuleNotFoundError: No module named 'fastmcp'**
   ```bash
   pip install fastmcp
   ```

2. **Blender 连接失败**
   - 检查 Blender 是否在 PATH 中
   - 尝试设置 `BLENDER_PATH` 环境变量
   - 确保 Blender 版本兼容（推荐 3.0+）

3. **渲染失败**
   - 检查输出路径权限
   - 确保有足够的磁盘空间
   - 降低渲染质量设置

4. **性能问题**
   - 减少对象数量
   - 降低渲染采样数
   - 使用更简单的材质

### 调试技巧

1. **启用详细日志**:
   ```python
   logging.basicConfig(level=logging.DEBUG)
   ```

2. **检查 Blender 输出**:
   ```python
   # 在脚本中添加更多 print 语句
   print(f"当前对象数量: {len(bpy.data.objects)}")
   ```

3. **分步执行**:
   - 注释掉部分代码
   - 逐步测试每个功能

## 📚 进一步学习

- [Blender Python API 文档](https://docs.blender.org/api/current/)
- [MCP 协议规范](https://modelcontextprotocol.io/)
- [FastMCP 文档](https://github.com/jlowin/fastmcp)

## 🤝 贡献

欢迎提交新的示例和改进！请确保：

1. 代码有适当的注释
2. 包含使用说明
3. 测试过基本功能
4. 遵循现有的代码风格

## 📄 许可证

这些示例遵循项目的主许可证。