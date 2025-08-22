#!/usr/bin/env python3
"""
Stable Diffusion 优化参数预设配置

本文件包含针对不同用途和质量要求的 Stable Diffusion 参数预设，
帮助用户快速选择最适合的生成参数。

使用方法:
    from sd_optimization_presets import get_preset, list_presets
    
    # 获取预设参数
    params = get_preset('high_quality')
    
    # 列出所有可用预设
    presets = list_presets()
"""

import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

@dataclass
class SDPreset:
    """
    Stable Diffusion 参数预设数据类
    """
    name: str
    description: str
    width: int
    height: int
    steps: int
    cfg_scale: float
    sampler_name: str
    negative_prompt: str
    batch_size: int = 1
    n_iter: int = 1
    restore_faces: bool = False
    enable_hr: bool = False
    hr_scale: float = 1.5
    denoising_strength: float = 0.7  # for img2img
    use_case: str = "general"
    quality_level: str = "medium"
    estimated_time: str = "medium"
    recommended_for: List[str] = None
    
    def __post_init__(self):
        if self.recommended_for is None:
            self.recommended_for = []

# 预设配置定义
PRESETS = {
    # 快速预览预设
    "quick_preview": SDPreset(
        name="快速预览",
        description="快速生成低质量预览图，适合测试提示词和构图",
        width=512,
        height=512,
        steps=10,
        cfg_scale=6.0,
        sampler_name="DPM++ 2M Karras",
        negative_prompt="blurry, low quality, distorted",
        batch_size=1,
        n_iter=1,
        restore_faces=False,
        enable_hr=False,
        use_case="testing",
        quality_level="low",
        estimated_time="fast",
        recommended_for=["提示词测试", "快速迭代", "构图验证"]
    ),
    
    # 标准质量预设
    "standard": SDPreset(
        name="标准质量",
        description="平衡质量和速度的标准设置，适合大多数用途",
        width=512,
        height=512,
        steps=20,
        cfg_scale=7.0,
        sampler_name="DPM++ 2M Karras",
        negative_prompt="blurry, low quality, distorted, deformed, ugly",
        batch_size=1,
        n_iter=1,
        restore_faces=False,
        enable_hr=False,
        use_case="general",
        quality_level="medium",
        estimated_time="medium",
        recommended_for=["日常使用", "概念设计", "插图创作"]
    ),
    
    # 高质量预设
    "high_quality": SDPreset(
        name="高质量",
        description="高质量图像生成，适合最终作品和专业用途",
        width=768,
        height=768,
        steps=30,
        cfg_scale=8.0,
        sampler_name="DPM++ SDE Karras",
        negative_prompt="blurry, low quality, distorted, deformed, ugly, bad anatomy, extra limbs, poorly drawn",
        batch_size=1,
        n_iter=1,
        restore_faces=True,
        enable_hr=True,
        hr_scale=1.5,
        use_case="professional",
        quality_level="high",
        estimated_time="slow",
        recommended_for=["最终作品", "专业设计", "高分辨率需求"]
    ),
    
    # 超高质量预设
    "ultra_quality": SDPreset(
        name="超高质量",
        description="最高质量设置，适合展示和印刷用途",
        width=1024,
        height=1024,
        steps=50,
        cfg_scale=9.0,
        sampler_name="DPM++ SDE Karras",
        negative_prompt="blurry, low quality, distorted, deformed, ugly, bad anatomy, extra limbs, poorly drawn, bad hands, bad face, mutation, mutated",
        batch_size=1,
        n_iter=1,
        restore_faces=True,
        enable_hr=True,
        hr_scale=2.0,
        use_case="showcase",
        quality_level="ultra",
        estimated_time="very_slow",
        recommended_for=["展示作品", "印刷用途", "艺术创作"]
    ),
    
    # 人像专用预设
    "portrait": SDPreset(
        name="人像专用",
        description="专门优化的人像生成设置，强化面部细节",
        width=512,
        height=768,
        steps=25,
        cfg_scale=7.5,
        sampler_name="DPM++ 2M Karras",
        negative_prompt="blurry, low quality, distorted, deformed, ugly, bad anatomy, bad face, bad eyes, bad hands, extra limbs, mutation",
        batch_size=1,
        n_iter=1,
        restore_faces=True,
        enable_hr=True,
        hr_scale=1.3,
        use_case="portrait",
        quality_level="high",
        estimated_time="medium",
        recommended_for=["人像摄影", "角色设计", "头像创作"]
    ),
    
    # 风景专用预设
    "landscape": SDPreset(
        name="风景专用",
        description="专门优化的风景生成设置，适合宽幅构图",
        width=768,
        height=512,
        steps=25,
        cfg_scale=7.0,
        sampler_name="DPM++ 2M Karras",
        negative_prompt="blurry, low quality, distorted, people, person, human, character",
        batch_size=1,
        n_iter=1,
        restore_faces=False,
        enable_hr=True,
        hr_scale=1.5,
        use_case="landscape",
        quality_level="high",
        estimated_time="medium",
        recommended_for=["风景摄影", "环境设计", "背景创作"]
    ),
    
    # 3D模型专用预设
    "for_3d_model": SDPreset(
        name="3D模型专用",
        description="专门为3D模型生成优化的设置，强调清晰轮廓和细节",
        width=768,
        height=768,
        steps=30,
        cfg_scale=8.5,
        sampler_name="DPM++ SDE Karras",
        negative_prompt="blurry, low quality, distorted, deformed, ugly, bad anatomy, extra limbs, poorly drawn, complex background, cluttered",
        batch_size=1,
        n_iter=1,
        restore_faces=False,
        enable_hr=True,
        hr_scale=1.5,
        use_case="3d_modeling",
        quality_level="high",
        estimated_time="medium",
        recommended_for=["3D建模参考", "纹理生成", "模型设计"]
    ),
    
    # 批量生成预设
    "batch_generation": SDPreset(
        name="批量生成",
        description="优化的批量生成设置，平衡质量和效率",
        width=512,
        height=512,
        steps=15,
        cfg_scale=7.0,
        sampler_name="DPM++ 2M Karras",
        negative_prompt="blurry, low quality, distorted, deformed",
        batch_size=4,
        n_iter=2,
        restore_faces=False,
        enable_hr=False,
        use_case="batch",
        quality_level="medium",
        estimated_time="medium",
        recommended_for=["批量创作", "变体生成", "素材收集"]
    ),
    
    # 图像增强预设
    "image_enhancement": SDPreset(
        name="图像增强",
        description="专门用于img2img的图像增强设置",
        width=768,
        height=768,
        steps=20,
        cfg_scale=7.0,
        sampler_name="DPM++ 2M Karras",
        negative_prompt="blurry, low quality, distorted, deformed, ugly, artifacts",
        batch_size=1,
        n_iter=1,
        restore_faces=True,
        enable_hr=False,
        denoising_strength=0.5,
        use_case="enhancement",
        quality_level="high",
        estimated_time="medium",
        recommended_for=["图像修复", "风格转换", "质量提升"]
    ),
    
    # 创意探索预设
    "creative_exploration": SDPreset(
        name="创意探索",
        description="鼓励创意和多样性的设置，适合艺术探索",
        width=512,
        height=512,
        steps=25,
        cfg_scale=6.0,
        sampler_name="Euler a",
        negative_prompt="low quality, blurry",
        batch_size=2,
        n_iter=2,
        restore_faces=False,
        enable_hr=False,
        use_case="creative",
        quality_level="medium",
        estimated_time="medium",
        recommended_for=["艺术探索", "创意实验", "风格研究"]
    )
}

# 采样器推荐配置
SAMPLER_RECOMMENDATIONS = {
    "speed_focused": [
        "DPM++ 2M Karras",
        "DPM++ 2M",
        "LMS Karras"
    ],
    "quality_focused": [
        "DPM++ SDE Karras",
        "DPM++ 2S a Karras",
        "DDIM"
    ],
    "creative_focused": [
        "Euler a",
        "Euler",
        "Heun"
    ],
    "stable_focused": [
        "DPM++ 2M Karras",
        "DDIM",
        "PLMS"
    ]
}

# CFG Scale 推荐范围
CFG_RECOMMENDATIONS = {
    "creative": (4.0, 8.0),
    "balanced": (6.0, 10.0),
    "strict": (8.0, 15.0),
    "experimental": (1.0, 20.0)
}

# Steps 推荐范围
STEPS_RECOMMENDATIONS = {
    "fast": (8, 15),
    "standard": (15, 25),
    "quality": (25, 40),
    "ultra": (40, 80)
}

def get_preset(preset_name: str) -> Optional[Dict[str, Any]]:
    """
    获取指定的预设配置
    
    Args:
        preset_name: 预设名称
        
    Returns:
        预设配置字典，如果不存在则返回None
    """
    if preset_name in PRESETS:
        return asdict(PRESETS[preset_name])
    return None

def list_presets() -> List[str]:
    """
    列出所有可用的预设名称
    
    Returns:
        预设名称列表
    """
    return list(PRESETS.keys())

def get_presets_by_use_case(use_case: str) -> List[Dict[str, Any]]:
    """
    根据用途获取相关预设
    
    Args:
        use_case: 用途类型
        
    Returns:
        相关预设配置列表
    """
    return [asdict(preset) for preset in PRESETS.values() if preset.use_case == use_case]

def get_presets_by_quality(quality_level: str) -> List[Dict[str, Any]]:
    """
    根据质量等级获取相关预设
    
    Args:
        quality_level: 质量等级 (low, medium, high, ultra)
        
    Returns:
        相关预设配置列表
    """
    return [asdict(preset) for preset in PRESETS.values() if preset.quality_level == quality_level]

def get_sampler_recommendations(focus: str) -> List[str]:
    """
    获取采样器推荐
    
    Args:
        focus: 关注点 (speed_focused, quality_focused, creative_focused, stable_focused)
        
    Returns:
        推荐的采样器列表
    """
    return SAMPLER_RECOMMENDATIONS.get(focus, SAMPLER_RECOMMENDATIONS["speed_focused"])

def get_cfg_recommendation(style: str) -> tuple:
    """
    获取CFG Scale推荐范围
    
    Args:
        style: 风格类型 (creative, balanced, strict, experimental)
        
    Returns:
        CFG Scale推荐范围 (min, max)
    """
    return CFG_RECOMMENDATIONS.get(style, CFG_RECOMMENDATIONS["balanced"])

def get_steps_recommendation(quality: str) -> tuple:
    """
    获取Steps推荐范围
    
    Args:
        quality: 质量要求 (fast, standard, quality, ultra)
        
    Returns:
        Steps推荐范围 (min, max)
    """
    return STEPS_RECOMMENDATIONS.get(quality, STEPS_RECOMMENDATIONS["standard"])

def optimize_preset_for_hardware(preset_name: str, gpu_memory_gb: float) -> Dict[str, Any]:
    """
    根据硬件配置优化预设参数
    
    Args:
        preset_name: 预设名称
        gpu_memory_gb: GPU内存大小(GB)
        
    Returns:
        优化后的预设配置
    """
    preset = get_preset(preset_name)
    if not preset:
        return None
    
    # 根据GPU内存调整参数
    if gpu_memory_gb < 4:
        # 低端GPU优化
        preset["width"] = min(preset["width"], 512)
        preset["height"] = min(preset["height"], 512)
        preset["batch_size"] = 1
        preset["enable_hr"] = False
        preset["steps"] = min(preset["steps"], 20)
    elif gpu_memory_gb < 8:
        # 中端GPU优化
        preset["width"] = min(preset["width"], 768)
        preset["height"] = min(preset["height"], 768)
        preset["batch_size"] = min(preset["batch_size"], 2)
        if preset["enable_hr"]:
            preset["hr_scale"] = min(preset["hr_scale"], 1.5)
    elif gpu_memory_gb >= 12:
        # 高端GPU可以使用更高设置
        if preset["quality_level"] in ["medium", "high"]:
            preset["width"] = min(preset["width"] * 1.2, 1024)
            preset["height"] = min(preset["height"] * 1.2, 1024)
    
    return preset

def create_custom_preset(name: str, base_preset: str = "standard", **kwargs) -> Dict[str, Any]:
    """
    创建自定义预设
    
    Args:
        name: 自定义预设名称
        base_preset: 基础预设名称
        **kwargs: 要覆盖的参数
        
    Returns:
        自定义预设配置
    """
    base = get_preset(base_preset)
    if not base:
        base = get_preset("standard")
    
    # 更新参数
    base.update(kwargs)
    base["name"] = name
    base["description"] = f"基于 {base_preset} 的自定义预设"
    
    return base

def export_presets_to_json(filename: str = "sd_presets.json"):
    """
    导出所有预设到JSON文件
    
    Args:
        filename: 输出文件名
    """
    presets_dict = {name: asdict(preset) for name, preset in PRESETS.items()}
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(presets_dict, f, ensure_ascii=False, indent=2)
    
    print(f"预设已导出到 {filename}")

def load_presets_from_json(filename: str) -> Dict[str, SDPreset]:
    """
    从JSON文件加载预设
    
    Args:
        filename: JSON文件名
        
    Returns:
        加载的预设字典
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            presets_dict = json.load(f)
        
        loaded_presets = {}
        for name, preset_data in presets_dict.items():
            loaded_presets[name] = SDPreset(**preset_data)
        
        return loaded_presets
    except FileNotFoundError:
        print(f"文件 {filename} 不存在")
        return {}
    except Exception as e:
        print(f"加载预设失败: {e}")
        return {}

def print_preset_info(preset_name: str):
    """
    打印预设详细信息
    
    Args:
        preset_name: 预设名称
    """
    preset = PRESETS.get(preset_name)
    if not preset:
        print(f"预设 '{preset_name}' 不存在")
        return
    
    print(f"\n📋 预设信息: {preset.name}")
    print(f"📝 描述: {preset.description}")
    print(f"🎯 用途: {preset.use_case}")
    print(f"⭐ 质量等级: {preset.quality_level}")
    print(f"⏱️ 预估时间: {preset.estimated_time}")
    print(f"📐 尺寸: {preset.width}x{preset.height}")
    print(f"🔄 步数: {preset.steps}")
    print(f"🎛️ CFG Scale: {preset.cfg_scale}")
    print(f"🔧 采样器: {preset.sampler_name}")
    print(f"🚫 负面提示: {preset.negative_prompt}")
    print(f"📦 批次设置: {preset.batch_size}x{preset.n_iter}")
    print(f"👤 面部修复: {'是' if preset.restore_faces else '否'}")
    print(f"🔍 高分辨率: {'是' if preset.enable_hr else '否'}")
    if preset.enable_hr:
        print(f"📈 放大倍数: {preset.hr_scale}x")
    print(f"💡 推荐用于: {', '.join(preset.recommended_for)}")

def print_all_presets_summary():
    """
    打印所有预设的摘要信息
    """
    print("\n🎨 Stable Diffusion 预设配置摘要")
    print("=" * 60)
    
    for name, preset in PRESETS.items():
        print(f"\n📌 {preset.name} ({name})")
        print(f"   📝 {preset.description}")
        print(f"   📐 {preset.width}x{preset.height} | 🔄 {preset.steps}步 | ⭐ {preset.quality_level}")
        print(f"   💡 推荐: {', '.join(preset.recommended_for[:2])}{'...' if len(preset.recommended_for) > 2 else ''}")

if __name__ == "__main__":
    # 演示用法
    print("🎨 Stable Diffusion 优化预设配置")
    print("=" * 50)
    
    # 显示所有预设摘要
    print_all_presets_summary()
    
    # 显示特定预设详情
    print("\n" + "=" * 50)
    print_preset_info("high_quality")
    
    # 演示硬件优化
    print("\n" + "=" * 50)
    print("\n🔧 硬件优化示例 (4GB GPU):")
    optimized = optimize_preset_for_hardware("high_quality", 4.0)
    print(f"原始尺寸: 768x768 -> 优化后: {optimized['width']}x{optimized['height']}")
    print(f"原始HR: {PRESETS['high_quality'].enable_hr} -> 优化后: {optimized['enable_hr']}")
    
    # 导出预设
    print("\n📤 导出预设到 JSON 文件...")
    export_presets_to_json()