# Stable Diffusion Web UI - Hunyuan3D 2.1 Integration

这是一个集成了 **Hunyuan3D 2.1** 的 Stable Diffusion Web UI 版本，专为3D资产生成和纹理合成而优化。

![](screenshot.png)

## 🎯 项目概述

本项目是 [Hunyuan3D-2.1](https://github.com/Tencent-Hunyuan/Hunyuan3D-2.1) 工作区的一部分，提供了一个增强的 Stable Diffusion Web UI，支持：

- **3D形状生成**: 从图像生成高质量3D网格
- **PBR纹理合成**: 基于物理的渲染纹理生成
- **Blender集成**: 通过 BlenderMCP 直接与 Blender 交互
- **API服务**: 完整的REST API支持3D生成工作流

## 🔗 相关组件

- **主项目**: [Hunyuan3D-2.1](../README.md) - 腾讯混元3D 2.1 主要框架
- **Blender集成**: [BlenderMCP](../blender-mcp/README.md) - Blender与Claude AI的MCP集成
- **3D形状生成**: [hy3dshape](../hy3dshape/README.md) - 3D形状生成模块
- **纹理生成**: [hy3dpaint](../hy3dpaint/README.md) - PBR纹理合成模块


- [Segmind Stable Diffusion](https://huggingface.co/segmind/SSD-1B) support

## 🚀 安装和运行

### 系统要求

- **GPU内存**: 
  - 形状生成: 10GB VRAM
  - 纹理生成: 21GB VRAM  
  - 完整流程: 29GB VRAM
- **Python**: 3.10 或更高版本
- **PyTorch**: 2.5.1+cu124 (推荐)

### 快速开始

1. **安装依赖**:
```bash
# 安装PyTorch (CUDA 12.4)
pip install torch==2.5.1 torchvision==0.20.1 torchaudio==2.5.1 --index-url https://download.pytorch.org/whl/cu124

# 安装项目依赖
pip install -r requirements.txt
```

2. **编译自定义组件**:
```bash
# 编译纹理生成组件
cd hy3dpaint/custom_rasterizer
pip install -e .
cd ../..

# 编译渲染器
cd hy3dpaint/DifferentiableRenderer
bash compile_mesh_painter.sh
cd ../..
```

3. **下载预训练模型**:
```bash
# 下载RealESRGAN模型
wget https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth -P hy3dpaint/ckpt
```

4. **启动Web UI**:
```bash
# 标准模式
python webui.py

# 低显存模式
python webui.py --lowvram

# 集成Hunyuan3D模式
python ../gradio_app.py --model_path tencent/Hunyuan3D-2.1 --subfolder hunyuan3d-dit-v2-1 --texgen_model_path tencent/Hunyuan3D-2.1 --low_vram_mode
```

### 传统安装方式

如需使用原版Stable Diffusion WebUI功能，请参考:
- [NVidia GPU安装指南](https://github.com/AUTOMATIC1111/stable-diffusion-webui/wiki/Install-and-Run-on-NVidia-GPUs) (推荐)
- [AMD GPU安装指南](https://github.com/AUTOMATIC1111/stable-diffusion-webui/wiki/Install-and-Run-on-AMD-GPUs)
- [Intel处理器安装指南](https://github.com/openvinotoolkit/stable-diffusion-webui/wiki/Installation-on-Intel-Silicon)

### 在线服务

- [在线服务列表](https://github.com/AUTOMATIC1111/stable-diffusion-webui/wiki/Online-Services)
- [Hunyuan3D官方Demo](https://huggingface.co/spaces/tencent/Hunyuan3D-2.1)


## 🎨 Hunyuan3D 特色功能

### 3D资产生成工作流

```python
import sys
sys.path.insert(0, './hy3dshape')
sys.path.insert(0, './hy3dpaint')
from textureGenPipeline import Hunyuan3DPaintPipeline, Hunyuan3DPaintConfig
from hy3dshape.pipelines import Hunyuan3DDiTFlowMatchingPipeline

# 1. 生成3D网格
shape_pipeline = Hunyuan3DDiTFlowMatchingPipeline.from_pretrained('tencent/Hunyuan3D-2.1')
mesh_untextured = shape_pipeline(image='assets/demo.png')[0]

# 2. 生成PBR纹理
paint_pipeline = Hunyuan3DPaintPipeline(Hunyuan3DPaintConfig(max_num_view=6, resolution=512))
mesh_textured = paint_pipeline(mesh_path, image_path='assets/demo.png')
```

### API服务

启动API服务器:
```bash
python ../api_server.py
```

使用API生成3D模型:
```python
import requests

# 上传图像并生成3D模型
response = requests.post('http://localhost:8000/generate_3d', 
                        files={'image': open('input.jpg', 'rb')},
                        data={'prompt': 'a cute cat'})
result = response.json()
```

### Blender集成

通过BlenderMCP，可以直接在Blender中使用Claude AI进行3D建模:

1. 安装Blender插件: `../blender-mcp/addon.py`
2. 配置Claude Desktop MCP服务器
3. 在Claude中直接描述需要的3D模型，AI将自动在Blender中创建

### 模型性能

| 模型组件 | VRAM需求 | 生成时间 | 输出格式 |
|---------|----------|----------|----------|
| Hunyuan3D-Shape | 10GB | ~30秒 | .obj/.ply |
| Hunyuan3D-Paint | 21GB | ~60秒 | PBR材质 |
| 完整流程 | 29GB | ~90秒 | 带纹理3D模型 |

## 🤝 贡献指南

欢迎为本项目贡献代码！请参考:
- [原版贡献指南](https://github.com/AUTOMATIC1111/stable-diffusion-webui/wiki/Contributing)
- [Hunyuan3D项目贡献](https://github.com/Tencent-Hunyuan/Hunyuan3D-2.1)

## 📚 文档

- [原版WebUI文档](https://github.com/AUTOMATIC1111/stable-diffusion-webui/wiki)
- [Hunyuan3D技术报告](https://arxiv.org/pdf/2506.15442)
- [BlenderMCP集成指南](../blender-mcp/README.md)
- [API文档](../API_DOCUMENTATION.md)

## 🙏 致谢

### Hunyuan3D 2.1 集成

本集成版本基于以下优秀项目:

- **Hunyuan3D 2.1** - [Tencent Hunyuan3D Team](https://github.com/Tencent-Hunyuan/Hunyuan3D-2.1)
- **BlenderMCP** - Blender与Claude AI的MCP集成
- **原版Stable Diffusion WebUI** - [AUTOMATIC1111](https://github.com/AUTOMATIC1111/stable-diffusion-webui)

### 引用

如果您使用了本项目，请引用:

```bibtex
@misc{hunyuan3d2025hunyuan3d,
    title={Hunyuan3D 2.1: From Images to High-Fidelity 3D Assets with Production-Ready PBR Material},
    author={Tencent Hunyuan3D Team},
    year={2025},
    eprint={2506.15442},
    archivePrefix={arXiv},
    primaryClass={cs.CV}
}
```

### 原版致谢

许可证信息可在 `Settings -> Licenses` 界面和 `html/licenses.html` 文件中找到。