# Hunyuan3D-2.1 与 Blender MCP 集成指南

本文档介绍如何使用集成了 Hunyuan3D-2.1 和 Stable Diffusion 功能的 Blender MCP 服务器。

## 🚀 功能特性

### 核心功能
- **文本到3D场景**: 从文本描述直接生成完整的3D场景
- **图像到3D模型**: 将2D图像转换为高质量3D模型
- **Stable Diffusion集成**: 支持本地和云端图像生成
- **Blender自动化**: 自动导入模型并设置场景

### 支持的工作流程
1. **完整工作流程**: 文本 → 图像生成 → 3D模型 → Blender场景
2. **图像到3D**: 现有图像 → 3D模型 → Blender导入
3. **异步生成**: 支持长时间3D生成任务的异步处理

## 📋 系统要求

### 硬件要求
- **GPU**: NVIDIA GPU (推荐8GB+ VRAM)
- **内存**: 16GB+ RAM
- **存储**: 10GB+ 可用空间

### 软件要求
- Python 3.8+
- Blender 3.0+
- CUDA 11.8+ (用于GPU加速)

## 🛠️ 安装配置

### 1. 安装依赖

```bash
# 安装Hunyuan3D依赖
cd Hunyuan3D-2.1
pip install -r requirements.txt

# 安装blender-mcp依赖
cd blender-mcp
pip install -e .
```

### 2. 启动服务

#### 启动Hunyuan3D API服务器
```bash
cd Hunyuan3D-2.1
python api_server.py --host 0.0.0.0 --port 8081 --device cuda
```

#### 启动Stable Diffusion (可选)
如果需要文本生成图像功能，请启动AUTOMATIC1111 WebUI：
```bash
# 下载并启动AUTOMATIC1111 WebUI
# 默认运行在 http://localhost:7860
```

#### 启动Blender MCP服务器
```bash
cd blender-mcp
python -m blender_mcp.server
```

### 3. 验证安装

运行集成测试脚本：
```bash
cd Hunyuan3D-2.1
python test_integration.py
```

## 🎯 使用方法

### MCP工具列表

#### 1. `create_3d_scene_from_text`
从文本描述创建完整3D场景

**参数:**
- `text_prompt`: 场景描述文本
- `use_local_sd_api`: 是否使用本地Stable Diffusion API
- `sd_api_url`: Stable Diffusion API地址 (默认: http://localhost:7860)
- `use_async_hunyuan`: 是否使用异步3D生成
- `num_chunks`: 3D生成分块数量 (默认: 4)
- `face_count`: 模型面数 (默认: 10000)

**示例:**
```python
# 通过MCP调用
result = mcp_client.call_tool("create_3d_scene_from_text", {
    "text_prompt": "一把现代木质椅子，简约设计",
    "use_local_sd_api": True,
    "use_async_hunyuan": True
})
```

#### 2. `generate_hunyuan3d_model`
从图像生成3D模型

**参数:**
- `image_input`: 图像输入 (文件路径、URL或base64)
- `remove_background`: 是否移除背景
- `texture`: 是否生成纹理
- `use_async`: 是否异步生成
- `num_chunks`: 分块数量
- `face_count`: 面数

#### 3. `generate_stable_diffusion_image`
生成图像

**参数:**
- `prompt`: 文本提示词
- `use_local_api`: 是否使用本地API
- `api_url`: API地址
- `width/height`: 图像尺寸
- `num_inference_steps`: 推理步数

#### 4. `poll_hunyuan3d_status`
查询异步3D生成状态

**参数:**
- `task_id`: 任务ID
- `api_url`: API地址

### 使用示例

#### 示例1: 创建简单物体
```python
# 创建一把椅子
result = create_3d_scene_from_text(
    text_prompt="一把现代办公椅，黑色皮革，金属支架",
    use_local_sd_api=True
)
```

#### 示例2: 创建复杂场景
```python
# 创建客厅场景
result = create_3d_scene_from_text(
    text_prompt="现代客厅，包含沙发、茶几、地毯，温暖照明",
    use_async_hunyuan=True,
    face_count=15000
)
```

#### 示例3: 从现有图像生成3D
```python
# 从图像文件生成3D模型
result = generate_hunyuan3d_model(
    image_input="/path/to/chair.jpg",
    remove_background=True,
    texture=True
)
```

## ⚙️ 配置选项

### Hunyuan3D API配置
- **默认地址**: `http://localhost:8081`
- **同步端点**: `/generate` (直接返回文件)
- **异步端点**: `/send` (返回任务ID)
- **状态查询**: `/status/{uid}`

### Stable Diffusion配置
- **默认地址**: `http://localhost:7860`
- **支持模型**: AUTOMATIC1111 WebUI兼容API
- **备选方案**: 内置diffusers库

### Blender集成
- **自动导入**: 生成的模型自动导入到Blender
- **场景设置**: 自动添加照明和相机
- **材质应用**: 支持纹理材质

## 🔧 故障排除

### 常见问题

#### 1. Hunyuan3D API连接失败
```
❌ 无法连接到Hunyuan3D API服务器
```
**解决方案:**
- 确认API服务器已启动
- 检查端口8081是否被占用
- 验证GPU驱动和CUDA安装

#### 2. Stable Diffusion不可用
```
⚠️ 无法连接到Stable Diffusion API服务器
```
**解决方案:**
- 启动AUTOMATIC1111 WebUI
- 检查端口7860是否可访问
- 或设置 `use_local_api=False` 使用内置diffusers

#### 3. 3D生成超时
```
⏰ 等待超时
```
**解决方案:**
- 降低 `face_count` 参数
- 增加 `num_chunks` 以并行处理
- 检查GPU内存使用情况

#### 4. Blender导入失败
```
❌ 模型导入Blender失败
```
**解决方案:**
- 确认Blender已启动并连接MCP
- 检查生成的模型文件格式
- 验证文件路径权限

### 性能优化

#### GPU内存优化
```bash
# 启用低显存模式
python api_server.py --low_vram_mode
```

#### 并发控制
```bash
# 限制并发任务数
python api_server.py --limit-model-concurrency 2
```

#### 缓存设置
```bash
# 设置缓存目录
python api_server.py --cache-path ./cache
```

## 📚 API参考

### Hunyuan3D API端点

#### POST `/generate`
同步生成3D模型，直接返回文件

#### POST `/send`
异步提交3D生成任务，返回任务ID

#### GET `/status/{uid}`
查询异步任务状态和结果

#### GET `/health`
服务器健康检查

### 响应格式

#### 成功响应
```json
{
  "status": "completed",
  "model_base64": "<base64编码的GLB文件>"
}
```

#### 错误响应
```json
{
  "status": "error",
  "message": "错误描述"
}
```

## 🤝 贡献指南

欢迎提交Issue和Pull Request来改进这个集成系统！

### 开发环境设置
1. Fork本仓库
2. 创建开发分支
3. 安装开发依赖
4. 运行测试
5. 提交更改

## 📄 许可证

本项目遵循相应组件的许可证：
- Hunyuan3D-2.1: Tencent Hunyuan Non-Commercial License
- Blender MCP: MIT License
- Stable Diffusion: CreativeML Open RAIL-M License

## 🙏 致谢

感谢以下项目的贡献：
- [Hunyuan3D-2.1](https://github.com/Tencent/Hunyuan3D) by Tencent
- [Stable Diffusion](https://github.com/Stability-AI/stablediffusion)
- [AUTOMATIC1111 WebUI](https://github.com/AUTOMATIC1111/stable-diffusion-webui)
- [Blender](https://www.blender.org/)

---

🎉 **开始创建你的3D世界吧！**