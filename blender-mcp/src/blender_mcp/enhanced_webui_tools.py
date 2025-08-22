#!/usr/bin/env python3
"""
增强版AUTOMATIC1111 WebUI MCP工具集成
为blender-mcp服务器提供更完整的文本生成图像功能
"""

import os
import sys
import tempfile
import time
import base64
from typing import Optional, List, Dict, Any
import logging

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.insert(0, project_root)

from enhanced_webui_integration import AutomaticWebUIClient, generate_image_with_webui

logger = logging.getLogger(__name__)

def enhanced_generate_stable_diffusion_image(
    prompt: str,
    negative_prompt: str = "blurry, low quality, distorted, deformed",
    width: int = 512,
    height: int = 512,
    steps: int = 20,
    cfg_scale: float = 7.0,
    seed: int = -1,
    sampler_name: str = "DPM++ 2M Karras",
    batch_size: int = 1,
    n_iter: int = 1,
    restore_faces: bool = False,
    enable_hr: bool = False,
    hr_scale: float = 2.0,
    api_url: str = "http://localhost:7860",
    output_dir: Optional[str] = None,
    save_parameters: bool = True
) -> str:
    """
    使用AUTOMATIC1111 WebUI生成高质量图像的增强版函数
    
    Parameters:
    - prompt: 图像描述提示词
    - negative_prompt: 负面提示词，用于避免不想要的元素
    - width: 图像宽度 (建议: 512, 768, 1024)
    - height: 图像高度 (建议: 512, 768, 1024)
    - steps: 推理步数 (建议: 20-50)
    - cfg_scale: CFG引导系数 (建议: 7-15)
    - seed: 随机种子 (-1为随机)
    - sampler_name: 采样器名称
    - batch_size: 批次大小
    - n_iter: 迭代次数
    - restore_faces: 是否修复面部
    - enable_hr: 是否启用高分辨率修复
    - hr_scale: 高分辨率缩放比例
    - api_url: WebUI API地址
    - output_dir: 输出目录
    - save_parameters: 是否保存生成参数
    
    Returns:
    - 生成结果的描述信息
    """
    try:
        logger.info(f"Starting enhanced image generation with prompt: {prompt[:100]}...")
        
        # 创建WebUI客户端
        client = AutomaticWebUIClient(api_url)
        
        # 检查服务器健康状态
        if not client.check_health():
            return f"❌ Error: AUTOMATIC1111 WebUI server at {api_url} is not responding.\n" \
                   f"Please start the WebUI server first.\n" \
                   f"Command: python launch.py --api --listen"
        
        # 获取可用模型和采样器信息
        models = client.get_models()
        samplers = client.get_samplers()
        
        logger.info(f"Available models: {len(models)}, Available samplers: {len(samplers)}")
        
        # 验证采样器
        if sampler_name not in samplers and samplers:
            logger.warning(f"Sampler '{sampler_name}' not available. Using first available: {samplers[0]}")
            sampler_name = samplers[0]
        
        # 生成图像
        result = client.txt2img(
            prompt=prompt,
            negative_prompt=negative_prompt,
            width=width,
            height=height,
            steps=steps,
            cfg_scale=cfg_scale,
            seed=seed,
            sampler_name=sampler_name,
            batch_size=batch_size,
            n_iter=n_iter,
            restore_faces=restore_faces,
            enable_hr=enable_hr,
            hr_scale=hr_scale
        )
        
        # 保存图像
        saved_paths = client.save_images(result["images"], output_dir)
        
        # 保存生成参数
        if save_parameters and saved_paths:
            params_file = os.path.join(os.path.dirname(saved_paths[0]), "generation_params.json")
            import json
            params = {
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "width": width,
                "height": height,
                "steps": steps,
                "cfg_scale": cfg_scale,
                "seed": seed,
                "sampler_name": sampler_name,
                "batch_size": batch_size,
                "n_iter": n_iter,
                "restore_faces": restore_faces,
                "enable_hr": enable_hr,
                "hr_scale": hr_scale,
                "timestamp": time.time(),
                "api_url": api_url
            }
            
            try:
                with open(params_file, 'w', encoding='utf-8') as f:
                    json.dump(params, f, indent=2, ensure_ascii=False)
                logger.info(f"Parameters saved to: {params_file}")
            except Exception as e:
                logger.warning(f"Failed to save parameters: {e}")
        
        # 构建返回信息
        total_images = len(saved_paths)
        result_info = f"✅ Successfully generated {total_images} image(s) using AUTOMATIC1111 WebUI\n\n"
        result_info += f"📝 Generation Parameters:\n"
        result_info += f"  • Prompt: {prompt}\n"
        result_info += f"  • Negative: {negative_prompt}\n"
        result_info += f"  • Size: {width}x{height}\n"
        result_info += f"  • Steps: {steps}, CFG: {cfg_scale}\n"
        result_info += f"  • Sampler: {sampler_name}\n"
        result_info += f"  • Seed: {seed}\n\n"
        
        result_info += f"💾 Saved Images:\n"
        for i, path in enumerate(saved_paths, 1):
            result_info += f"  {i}. {path}\n"
        
        result_info += f"\n🎯 Next Steps:\n"
        result_info += f"  • Use generate_hunyuan3d_model with these images to create 3D models\n"
        result_info += f"  • Import the 3D models into Blender for further editing\n"
        result_info += f"  • Create complete 3D scenes using create_3d_scene_from_text\n"
        
        return result_info
        
    except Exception as e:
        error_msg = f"❌ Error generating image with AUTOMATIC1111 WebUI: {str(e)}\n\n"
        error_msg += f"🔧 Troubleshooting:\n"
        error_msg += f"  1. Make sure AUTOMATIC1111 WebUI is running at {api_url}\n"
        error_msg += f"  2. Start WebUI with API enabled: python launch.py --api --listen\n"
        error_msg += f"  3. Check if the server is accessible from this machine\n"
        error_msg += f"  4. Verify the prompt and parameters are valid\n"
        
        logger.error(f"Enhanced image generation failed: {str(e)}")
        return error_msg


def batch_generate_images(
    prompts: List[str],
    negative_prompt: str = "blurry, low quality, distorted, deformed",
    width: int = 512,
    height: int = 512,
    steps: int = 20,
    cfg_scale: float = 7.0,
    sampler_name: str = "DPM++ 2M Karras",
    api_url: str = "http://localhost:7860",
    output_dir: Optional[str] = None
) -> str:
    """
    批量生成多个图像
    
    Parameters:
    - prompts: 提示词列表
    - negative_prompt: 负面提示词
    - width: 图像宽度
    - height: 图像高度
    - steps: 推理步数
    - cfg_scale: CFG引导系数
    - sampler_name: 采样器名称
    - api_url: WebUI API地址
    - output_dir: 输出目录
    
    Returns:
    - 批量生成结果的描述信息
    """
    try:
        if not prompts:
            return "❌ Error: No prompts provided for batch generation"
        
        logger.info(f"Starting batch generation for {len(prompts)} prompts")
        
        client = AutomaticWebUIClient(api_url)
        
        if not client.check_health():
            return f"❌ Error: AUTOMATIC1111 WebUI server at {api_url} is not responding"
        
        all_saved_paths = []
        failed_prompts = []
        
        for i, prompt in enumerate(prompts, 1):
            try:
                logger.info(f"Generating image {i}/{len(prompts)}: {prompt[:50]}...")
                
                result = client.txt2img(
                    prompt=prompt,
                    negative_prompt=negative_prompt,
                    width=width,
                    height=height,
                    steps=steps,
                    cfg_scale=cfg_scale,
                    sampler_name=sampler_name,
                    seed=-1  # 每个图像使用不同的随机种子
                )
                
                saved_paths = client.save_images(result["images"], output_dir)
                all_saved_paths.extend(saved_paths)
                
            except Exception as e:
                logger.error(f"Failed to generate image for prompt {i}: {e}")
                failed_prompts.append((i, prompt, str(e)))
        
        # 构建结果信息
        result_info = f"📊 Batch Generation Results:\n\n"
        result_info += f"✅ Successfully generated: {len(all_saved_paths)} images\n"
        result_info += f"❌ Failed: {len(failed_prompts)} prompts\n\n"
        
        if all_saved_paths:
            result_info += f"💾 Generated Images:\n"
            for i, path in enumerate(all_saved_paths, 1):
                result_info += f"  {i}. {path}\n"
            result_info += "\n"
        
        if failed_prompts:
            result_info += f"⚠️ Failed Prompts:\n"
            for i, prompt, error in failed_prompts:
                result_info += f"  {i}. {prompt[:50]}... - {error}\n"
        
        return result_info
        
    except Exception as e:
        logger.error(f"Batch generation failed: {str(e)}")
        return f"❌ Error in batch generation: {str(e)}"


def img2img_enhance(
    input_image_path: str,
    prompt: str,
    negative_prompt: str = "blurry, low quality, distorted, deformed",
    denoising_strength: float = 0.75,
    width: int = 512,
    height: int = 512,
    steps: int = 20,
    cfg_scale: float = 7.0,
    seed: int = -1,
    sampler_name: str = "DPM++ 2M Karras",
    api_url: str = "http://localhost:7860",
    output_dir: Optional[str] = None
) -> str:
    """
    使用图像到图像功能增强或修改现有图像
    
    Parameters:
    - input_image_path: 输入图像路径
    - prompt: 修改描述提示词
    - negative_prompt: 负面提示词
    - denoising_strength: 去噪强度 (0.0-1.0)
    - width: 输出图像宽度
    - height: 输出图像高度
    - steps: 推理步数
    - cfg_scale: CFG引导系数
    - seed: 随机种子
    - sampler_name: 采样器名称
    - api_url: WebUI API地址
    - output_dir: 输出目录
    
    Returns:
    - 图像增强结果的描述信息
    """
    try:
        if not os.path.exists(input_image_path):
            return f"❌ Error: Input image not found: {input_image_path}"
        
        logger.info(f"Starting img2img enhancement for: {input_image_path}")
        
        client = AutomaticWebUIClient(api_url)
        
        if not client.check_health():
            return f"❌ Error: AUTOMATIC1111 WebUI server at {api_url} is not responding"
        
        # 读取并编码输入图像
        with open(input_image_path, "rb") as f:
            image_data = f.read()
            image_b64 = base64.b64encode(image_data).decode('utf-8')
        
        # 执行img2img
        result = client.img2img(
            init_images=[image_b64],
            prompt=prompt,
            negative_prompt=negative_prompt,
            width=width,
            height=height,
            steps=steps,
            cfg_scale=cfg_scale,
            seed=seed,
            sampler_name=sampler_name,
            denoising_strength=denoising_strength
        )
        
        # 保存结果图像
        saved_paths = client.save_images(result["images"], output_dir)
        
        result_info = f"✅ Successfully enhanced image using img2img\n\n"
        result_info += f"📝 Enhancement Parameters:\n"
        result_info += f"  • Input: {input_image_path}\n"
        result_info += f"  • Prompt: {prompt}\n"
        result_info += f"  • Denoising Strength: {denoising_strength}\n"
        result_info += f"  • Size: {width}x{height}\n"
        result_info += f"  • Steps: {steps}, CFG: {cfg_scale}\n\n"
        
        result_info += f"💾 Enhanced Images:\n"
        for i, path in enumerate(saved_paths, 1):
            result_info += f"  {i}. {path}\n"
        
        return result_info
        
    except Exception as e:
        logger.error(f"img2img enhancement failed: {str(e)}")
        return f"❌ Error in img2img enhancement: {str(e)}"


def get_webui_status(api_url: str = "http://localhost:7860") -> str:
    """
    获取AUTOMATIC1111 WebUI的详细状态信息
    
    Parameters:
    - api_url: WebUI API地址
    
    Returns:
    - WebUI状态信息
    """
    try:
        client = AutomaticWebUIClient(api_url)
        
        if not client.check_health():
            return f"❌ AUTOMATIC1111 WebUI Status: OFFLINE\n" \
                   f"Server at {api_url} is not responding\n\n" \
                   f"🔧 To start WebUI:\n" \
                   f"  1. Navigate to your AUTOMATIC1111 directory\n" \
                   f"  2. Run: python launch.py --api --listen\n" \
                   f"  3. Wait for server to start on port 7860"
        
        # 获取详细信息
        models = client.get_models()
        samplers = client.get_samplers()
        progress = client.get_progress()
        
        status_info = f"✅ AUTOMATIC1111 WebUI Status: ONLINE\n\n"
        status_info += f"🌐 Server URL: {api_url}\n"
        status_info += f"🎨 Available Models: {len(models)}\n"
        status_info += f"⚙️ Available Samplers: {len(samplers)}\n\n"
        
        if models:
            status_info += f"📋 Models (first 5):\n"
            for model in models[:5]:
                status_info += f"  • {model}\n"
            if len(models) > 5:
                status_info += f"  ... and {len(models) - 5} more\n"
            status_info += "\n"
        
        if samplers:
            status_info += f"🔧 Samplers (first 10):\n"
            for sampler in samplers[:10]:
                status_info += f"  • {sampler}\n"
            if len(samplers) > 10:
                status_info += f"  ... and {len(samplers) - 10} more\n"
            status_info += "\n"
        
        if progress and progress.get('progress', 0) > 0:
            status_info += f"🔄 Current Progress: {progress.get('progress', 0):.1%}\n"
            if progress.get('eta_relative'):
                status_info += f"⏱️ ETA: {progress.get('eta_relative'):.1f}s\n"
        
        status_info += f"✨ WebUI is ready for image generation!"
        
        return status_info
        
    except Exception as e:
        logger.error(f"Failed to get WebUI status: {str(e)}")
        return f"❌ Error checking WebUI status: {str(e)}"


if __name__ == "__main__":
    # 测试增强版功能
    print("Testing Enhanced AUTOMATIC1111 WebUI Integration...")
    
    # 测试状态检查
    print("\n" + "="*50)
    print("WebUI Status Check:")
    print("="*50)
    print(get_webui_status())
    
    # 测试图像生成
    print("\n" + "="*50)
    print("Image Generation Test:")
    print("="*50)
    result = enhanced_generate_stable_diffusion_image(
        prompt="a beautiful sunset over mountains, highly detailed, photorealistic",
        negative_prompt="blurry, low quality",
        width=512,
        height=512,
        steps=20
    )
    print(result)