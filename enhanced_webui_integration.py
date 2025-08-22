#!/usr/bin/env python3
"""
增强版AUTOMATIC1111 WebUI集成模块
提供更完整的文本生成图像功能，包括高级参数配置和错误处理
"""

import requests
import base64
import json
import time
import os
import tempfile
from typing import Optional, Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class AutomaticWebUIClient:
    """AUTOMATIC1111 WebUI API客户端"""
    
    def __init__(self, api_url: str = "http://localhost:7860"):
        self.api_url = api_url.rstrip('/')
        self.session = requests.Session()
        self.session.timeout = 300
    
    def check_health(self) -> bool:
        """检查WebUI服务器健康状态"""
        try:
            response = self.session.get(f"{self.api_url}/sdapi/v1/options")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
    
    def get_models(self) -> List[str]:
        """获取可用的模型列表"""
        try:
            response = self.session.get(f"{self.api_url}/sdapi/v1/sd-models")
            if response.status_code == 200:
                models = response.json()
                return [model['title'] for model in models]
            return []
        except Exception as e:
            logger.error(f"Failed to get models: {e}")
            return []
    
    def get_samplers(self) -> List[str]:
        """获取可用的采样器列表"""
        try:
            response = self.session.get(f"{self.api_url}/sdapi/v1/samplers")
            if response.status_code == 200:
                samplers = response.json()
                return [sampler['name'] for sampler in samplers]
            return []
        except Exception as e:
            logger.error(f"Failed to get samplers: {e}")
            return []
    
    def txt2img(
        self,
        prompt: str,
        negative_prompt: str = "",
        width: int = 512,
        height: int = 512,
        steps: int = 20,
        cfg_scale: float = 7.0,
        seed: int = -1,
        sampler_name: str = "DPM++ 2M Karras",
        batch_size: int = 1,
        n_iter: int = 1,
        restore_faces: bool = False,
        tiling: bool = False,
        enable_hr: bool = False,
        hr_scale: float = 2.0,
        hr_upscaler: str = "Latent",
        hr_second_pass_steps: int = 0,
        denoising_strength: float = 0.7,
        styles: Optional[List[str]] = None,
        override_settings: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """文本生成图像
        
        Args:
            prompt: 正面提示词
            negative_prompt: 负面提示词
            width: 图像宽度
            height: 图像高度
            steps: 推理步数
            cfg_scale: CFG引导系数
            seed: 随机种子
            sampler_name: 采样器名称
            batch_size: 批次大小
            n_iter: 迭代次数
            restore_faces: 是否修复面部
            tiling: 是否平铺
            enable_hr: 是否启用高分辨率修复
            hr_scale: 高分辨率缩放比例
            hr_upscaler: 高分辨率放大器
            hr_second_pass_steps: 高分辨率第二次通过步数
            denoising_strength: 去噪强度
            styles: 样式列表
            override_settings: 覆盖设置
        
        Returns:
            包含生成结果的字典
        """
        payload = {
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
            "tiling": tiling,
            "enable_hr": enable_hr,
            "hr_scale": hr_scale,
            "hr_upscaler": hr_upscaler,
            "hr_second_pass_steps": hr_second_pass_steps,
            "denoising_strength": denoising_strength,
            "styles": styles or [],
            "override_settings": override_settings or {}
        }
        
        logger.info(f"Sending txt2img request with prompt: {prompt[:100]}...")
        
        try:
            response = self.session.post(
                f"{self.api_url}/sdapi/v1/txt2img",
                json=payload
            )
            
            if response.status_code != 200:
                raise Exception(f"API returned status {response.status_code}: {response.text}")
            
            result = response.json()
            
            if "images" not in result or not result["images"]:
                raise Exception("No images returned from API")
            
            return result
            
        except requests.exceptions.ConnectionError:
            raise Exception(f"Could not connect to WebUI at {self.api_url}. Make sure it's running.")
        except requests.exceptions.Timeout:
            raise Exception("Request timed out. Try reducing image size or steps.")
        except Exception as e:
            raise Exception(f"txt2img failed: {str(e)}")
    
    def img2img(
        self,
        init_images: List[str],
        prompt: str,
        negative_prompt: str = "",
        width: int = 512,
        height: int = 512,
        steps: int = 20,
        cfg_scale: float = 7.0,
        seed: int = -1,
        sampler_name: str = "DPM++ 2M Karras",
        denoising_strength: float = 0.75,
        resize_mode: int = 0,
        mask: Optional[str] = None,
        mask_blur: int = 4,
        inpainting_fill: int = 1,
        inpaint_full_res: bool = True,
        inpaint_full_res_padding: int = 0,
        inpainting_mask_invert: int = 0
    ) -> Dict[str, Any]:
        """图像生成图像
        
        Args:
            init_images: 初始图像的base64编码列表
            prompt: 正面提示词
            negative_prompt: 负面提示词
            width: 图像宽度
            height: 图像高度
            steps: 推理步数
            cfg_scale: CFG引导系数
            seed: 随机种子
            sampler_name: 采样器名称
            denoising_strength: 去噪强度
            resize_mode: 调整大小模式
            mask: 遮罩图像的base64编码
            mask_blur: 遮罩模糊
            inpainting_fill: 修复填充模式
            inpaint_full_res: 是否全分辨率修复
            inpaint_full_res_padding: 全分辨率修复填充
            inpainting_mask_invert: 是否反转修复遮罩
        
        Returns:
            包含生成结果的字典
        """
        payload = {
            "init_images": init_images,
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "width": width,
            "height": height,
            "steps": steps,
            "cfg_scale": cfg_scale,
            "seed": seed,
            "sampler_name": sampler_name,
            "denoising_strength": denoising_strength,
            "resize_mode": resize_mode,
            "mask": mask,
            "mask_blur": mask_blur,
            "inpainting_fill": inpainting_fill,
            "inpaint_full_res": inpaint_full_res,
            "inpaint_full_res_padding": inpaint_full_res_padding,
            "inpainting_mask_invert": inpainting_mask_invert
        }
        
        logger.info(f"Sending img2img request with prompt: {prompt[:100]}...")
        
        try:
            response = self.session.post(
                f"{self.api_url}/sdapi/v1/img2img",
                json=payload
            )
            
            if response.status_code != 200:
                raise Exception(f"API returned status {response.status_code}: {response.text}")
            
            result = response.json()
            
            if "images" not in result or not result["images"]:
                raise Exception("No images returned from API")
            
            return result
            
        except requests.exceptions.ConnectionError:
            raise Exception(f"Could not connect to WebUI at {self.api_url}. Make sure it's running.")
        except requests.exceptions.Timeout:
            raise Exception("Request timed out. Try reducing image size or steps.")
        except Exception as e:
            raise Exception(f"img2img failed: {str(e)}")
    
    def save_images(self, images: List[str], output_dir: Optional[str] = None) -> List[str]:
        """保存base64编码的图像到文件
        
        Args:
            images: base64编码的图像列表
            output_dir: 输出目录，如果为None则使用临时目录
        
        Returns:
            保存的图像文件路径列表
        """
        if output_dir is None:
            output_dir = tempfile.mkdtemp()
        
        os.makedirs(output_dir, exist_ok=True)
        
        saved_paths = []
        timestamp = int(time.time())
        
        for i, image_b64 in enumerate(images):
            try:
                image_data = base64.b64decode(image_b64)
                filename = f"generated_{timestamp}_{i:03d}.png"
                filepath = os.path.join(output_dir, filename)
                
                with open(filepath, "wb") as f:
                    f.write(image_data)
                
                saved_paths.append(filepath)
                logger.info(f"Image saved to: {filepath}")
                
            except Exception as e:
                logger.error(f"Failed to save image {i}: {e}")
        
        return saved_paths
    
    def get_progress(self) -> Dict[str, Any]:
        """获取当前生成进度"""
        try:
            response = self.session.get(f"{self.api_url}/sdapi/v1/progress")
            if response.status_code == 200:
                return response.json()
            return {}
        except Exception as e:
            logger.error(f"Failed to get progress: {e}")
            return {}
    
    def interrupt(self) -> bool:
        """中断当前生成任务"""
        try:
            response = self.session.post(f"{self.api_url}/sdapi/v1/interrupt")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Failed to interrupt: {e}")
            return False


def create_enhanced_webui_client(api_url: str = "http://localhost:7860") -> AutomaticWebUIClient:
    """创建增强版WebUI客户端"""
    return AutomaticWebUIClient(api_url)


def generate_image_with_webui(
    prompt: str,
    negative_prompt: str = "",
    width: int = 512,
    height: int = 512,
    steps: int = 20,
    cfg_scale: float = 7.0,
    seed: int = -1,
    sampler_name: str = "DPM++ 2M Karras",
    api_url: str = "http://localhost:7860",
    output_dir: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """使用AUTOMATIC1111 WebUI生成图像的便捷函数
    
    Args:
        prompt: 正面提示词
        negative_prompt: 负面提示词
        width: 图像宽度
        height: 图像高度
        steps: 推理步数
        cfg_scale: CFG引导系数
        seed: 随机种子
        sampler_name: 采样器名称
        api_url: WebUI API地址
        output_dir: 输出目录
        **kwargs: 其他参数
    
    Returns:
        包含生成结果和保存路径的字典
    """
    client = AutomaticWebUIClient(api_url)
    
    # 检查服务器状态
    if not client.check_health():
        raise Exception(f"WebUI server at {api_url} is not responding. Please start it first.")
    
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
        **kwargs
    )
    
    # 保存图像
    saved_paths = client.save_images(result["images"], output_dir)
    
    return {
        "success": True,
        "images": result["images"],
        "saved_paths": saved_paths,
        "parameters": result.get("parameters", {}),
        "info": result.get("info", "")
    }


if __name__ == "__main__":
    # 测试代码
    try:
        result = generate_image_with_webui(
            prompt="a beautiful landscape with mountains and lakes",
            negative_prompt="blurry, low quality",
            width=512,
            height=512,
            steps=20
        )
        print(f"Generated {len(result['saved_paths'])} images:")
        for path in result['saved_paths']:
            print(f"  - {path}")
    except Exception as e:
        print(f"Error: {e}")