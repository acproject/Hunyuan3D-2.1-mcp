# AUTOMATIC1111 WebUI Integration Guide

本指南详细介绍如何在 Blender MCP 项目中使用 AUTOMATIC1111 WebUI 进行文本生成图像功能。

## 🚀 功能概述

本项目现已集成完整的 AUTOMATIC1111 WebUI 支持，提供以下功能：

### 核心功能
- **文本生成图像 (txt2img)** - 从文本描述生成高质量图像
- **图像增强 (img2img)** - 基于现有图像进行修改和增强
- **批量生成** - 同时生成多个不同提示词的图像
- **高分辨率放大** - 支持高分辨率图像生成和放大
- **面部修复** - 自动修复生成图像中的面部细节
- **状态监控** - 实时检查 WebUI 服务器状态和能力

### 增强功能
- **参数保存** - 自动保存生成参数到 JSON 文件
- **错误处理** - 完善的错误处理和重试机制
- **进度监控** - 实时显示生成进度
- **模型管理** - 自动检测可用模型和采样器

## 📋 前置要求

### 1. AUTOMATIC1111 WebUI 安装

首先需要安装并配置 AUTOMATIC1111 WebUI：

```bash
# 克隆仓库
git clone https://github.com/AUTOMATIC1111/stable-diffusion-webui.git
cd stable-diffusion-webui

# 安装依赖（首次运行会自动安装）
# Windows
webui.bat --api

# Linux/Mac
./webui.sh --api
```

**重要：必须使用 `--api` 参数启动 WebUI 以启用 API 功能！**

### 2. Python 依赖

确保安装了必要的 Python 包：

```bash
pip install requests pillow base64 json pathlib
```

### 3. 模型下载

在 WebUI 中下载至少一个 Stable Diffusion 模型，推荐：
- **v1-5-pruned-emaonly.safetensors** (基础模型)
- **deliberate_v2.safetensors** (高质量模型)
- **realisticVisionV60_v60B1VAE.safetensors** (写实风格)

## 🛠️ 配置说明

### 默认配置

- **WebUI API 地址**: `http://localhost:7860`
- **默认图像尺寸**: 512x512
- **默认采样步数**: 20
- **默认引导系数**: 7.0
- **默认采样器**: "DPM++ 2M Karras"

### 自定义配置

可以通过函数参数自定义所有设置：

```python
# 高质量设置
result = enhanced_txt2img(
    prompt="your prompt here",
    width=768,
    height=768,
    steps=30,
    cfg_scale=8.0,
    enable_hr=True,
    hr_scale=2.0,
    restore_faces=True
)
```

## 🎨 使用方法

### 1. 基础文本生成图像

使用 `enhanced_txt2img` 工具生成图像：

```python
# 基础用法
result = enhanced_txt2img(
    prompt="a beautiful landscape with mountains and lake, digital art, high quality",
    negative_prompt="blurry, low quality, distorted"
)
```

### 2. 高质量图像生成

启用高分辨率和面部修复功能：

```python
result = enhanced_txt2img(
    prompt="portrait of a beautiful woman, detailed face, professional photography",
    width=768,
    height=768,
    steps=30,
    cfg_scale=8.0,
    enable_hr=True,
    hr_scale=1.5,
    restore_faces=True,
    sampler_name="DPM++ SDE Karras"
)
```

### 3. 批量生成

使用 `batch_txt2img` 同时生成多个图像：

```python
result = batch_txt2img(
    prompts="red apple, blue car, green tree, yellow flower",
    batch_count=2,  # 每个提示词生成2张图
    width=512,
    height=512
)
```

### 4. 图像增强

使用 `enhance_image` 修改现有图像：

```python
result = enhance_image(
    image_path="/path/to/your/image.png",
    prompt="make it more colorful and vibrant",
    denoising_strength=0.7,
    steps=25
)
```

### 5. 状态检查

使用 `check_webui_status` 检查 WebUI 状态：

```python
status = check_webui_status()
print(status)  # 显示详细的状态信息
```

### 6. 完整 3D 场景创建

使用 `create_enhanced_3d_scene` 创建完整的 3D 场景：

```python
result = create_enhanced_3d_scene(
    scene_description="a medieval castle on a hill",
    use_enhanced_generation=True,
    image_width=1024,
    image_height=1024,
    enable_hr=True,
    hr_scale=2.0
)
```

## 📊 参数详解

### 图像生成参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `prompt` | str | - | 图像描述提示词 |
| `negative_prompt` | str | "blurry, low quality..." | 负面提示词 |
| `width` | int | 512 | 图像宽度 (推荐: 512, 768, 1024) |
| `height` | int | 512 | 图像高度 (推荐: 512, 768, 1024) |
| `steps` | int | 20 | 采样步数 (10-50) |
| `cfg_scale` | float | 7.0 | 引导系数 (1-20) |
| `seed` | int | -1 | 随机种子 (-1 为随机) |
| `sampler_name` | str | "DPM++ 2M Karras" | 采样器名称 |

### 高级参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `batch_size` | int | 1 | 批次大小 |
| `n_iter` | int | 1 | 迭代次数 |
| `restore_faces` | bool | False | 启用面部修复 |
| `enable_hr` | bool | False | 启用高分辨率 |
| `hr_scale` | float | 2.0 | 高分辨率放大倍数 |
| `denoising_strength` | float | 0.7 | 去噪强度 (img2img) |

## 🎯 最佳实践

### 提示词编写技巧

1. **具体描述**: 使用具体、详细的描述
   ```
   好: "a red sports car parked in front of a modern glass building, sunset lighting, professional photography"
   差: "car"
   ```

2. **质量关键词**: 添加质量提升关键词
   ```
   "high quality, detailed, professional, 4k, masterpiece, best quality"
   ```

3. **风格指定**: 明确指定艺术风格
   ```
   "digital art, oil painting, photorealistic, anime style, concept art"
   ```

4. **负面提示词**: 使用有效的负面提示词
   ```
   "blurry, low quality, distorted, deformed, ugly, bad anatomy, extra limbs"
   ```

### 参数优化建议

1. **图像尺寸**:
   - 512x512: 快速生成，适合测试
   - 768x768: 平衡质量和速度
   - 1024x1024: 高质量，需要更多时间

2. **采样步数**:
   - 10-15: 快速预览
   - 20-30: 标准质量
   - 30-50: 高质量精细化

3. **引导系数 (CFG Scale)**:
   - 5-7: 更自然，创意性强
   - 7-10: 平衡
   - 10-15: 严格遵循提示词

4. **高分辨率设置**:
   - 启用条件: 需要大尺寸高质量图像
   - 放大倍数: 1.5-2.0 (过高可能导致问题)

## 🔧 故障排除

### 常见问题

1. **连接失败**
   ```
   错误: Cannot connect to WebUI API at http://localhost:7860
   解决: 确保 WebUI 使用 --api 参数启动
   ```

2. **生成失败**
   ```
   错误: Generation failed with status: 500
   解决: 检查提示词长度，确保模型已加载
   ```

3. **内存不足**
   ```
   错误: CUDA out of memory
   解决: 降低图像尺寸或批次大小
   ```

4. **模型未找到**
   ```
   错误: Model not found
   解决: 在 WebUI 中下载并选择模型
   ```

### 性能优化

1. **GPU 设置**: 确保 WebUI 使用 GPU 加速
2. **内存管理**: 适当设置 `--medvram` 或 `--lowvram` 参数
3. **批次处理**: 使用批量生成提高效率
4. **缓存清理**: 定期清理生成的临时文件

## 📁 文件结构

```
blender-mcp/
├── src/blender_mcp/
│   └── server.py                    # 主服务器文件（已更新）
├── enhanced_webui_integration.py    # WebUI 客户端类
├── enhanced_webui_tools.py          # 增强工具函数
├── test_webui_integration.py        # 完整测试套件
├── simple_webui_test.py            # 简化测试脚本
└── WEBUI_INTEGRATION_GUIDE.md      # 本指南
```

## 🔄 工作流程示例

### 完整的文本到3D工作流程

1. **生成概念图像**
   ```python
   image_result = enhanced_txt2img(
       prompt="medieval castle on a mountain, fantasy art, detailed architecture",
       width=768,
       height=768,
       enable_hr=True
   )
   ```

2. **创建3D模型**
   ```python
   scene_result = create_enhanced_3d_scene(
       scene_description="medieval castle on a mountain",
       use_enhanced_generation=True,
       image_width=1024,
       image_height=1024
   )
   ```

3. **在Blender中完善**
   - 调整模型比例和位置
   - 添加光照和材质
   - 创建环境和背景

## 📞 技术支持

如果遇到问题，请检查：

1. **WebUI 状态**: 运行 `check_webui_status()` 检查连接
2. **日志文件**: 查看 WebUI 控制台输出
3. **测试脚本**: 运行 `simple_webui_test.py` 进行诊断
4. **依赖检查**: 确保所有 Python 包已正确安装

## 🎉 总结

通过本集成，您现在可以：
- 直接在 Blender MCP 中生成高质量图像
- 使用先进的 AI 图像生成技术
- 创建完整的文本到3D工作流程
- 享受专业级的图像生成功能

开始创作您的 AI 艺术作品吧！🎨✨