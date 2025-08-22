#!/usr/bin/env python3
"""
Stable Diffusion 参数优化器

这个模块提供智能参数优化功能，根据用户需求、硬件配置和生成目标
自动推荐最佳的 Stable Diffusion 参数组合。

主要功能:
- 智能参数推荐
- 硬件性能优化
- 质量与速度平衡
- 批量生成优化
- 实时参数调整建议
"""

import json
import math
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from sd_optimization_presets import get_preset, PRESETS, SDPreset

class OptimizationGoal(Enum):
    """优化目标枚举"""
    SPEED = "speed"          # 优先速度
    QUALITY = "quality"      # 优先质量
    BALANCED = "balanced"    # 平衡模式
    MEMORY = "memory"        # 内存优化
    BATCH = "batch"          # 批量优化
    CREATIVE = "creative"    # 创意探索

class HardwareProfile(Enum):
    """硬件配置枚举"""
    LOW_END = "low_end"      # 低端配置 (<4GB VRAM)
    MID_RANGE = "mid_range"  # 中端配置 (4-8GB VRAM)
    HIGH_END = "high_end"    # 高端配置 (8-12GB VRAM)
    ENTHUSIAST = "enthusiast" # 发烧级配置 (>12GB VRAM)

@dataclass
class OptimizationContext:
    """优化上下文信息"""
    goal: OptimizationGoal
    hardware_profile: HardwareProfile
    gpu_memory_gb: float
    target_resolution: Tuple[int, int] = (512, 512)
    time_constraint: Optional[int] = None  # 秒
    quality_threshold: float = 0.7  # 0-1
    batch_requirement: int = 1
    use_case: str = "general"
    model_type: str = "sd15"  # sd15, sdxl, etc.
    
@dataclass
class OptimizationResult:
    """优化结果"""
    recommended_params: Dict[str, Any]
    confidence_score: float
    estimated_time: float
    memory_usage: float
    quality_score: float
    alternative_configs: List[Dict[str, Any]]
    optimization_notes: List[str]
    warnings: List[str]

class SDParameterOptimizer:
    """Stable Diffusion 参数优化器"""
    
    def __init__(self):
        self.performance_cache = {}
        self.optimization_history = []
        
        # 硬件配置映射
        self.hardware_configs = {
            HardwareProfile.LOW_END: {
                "max_resolution": (512, 512),
                "max_batch_size": 1,
                "recommended_steps": (8, 20),
                "enable_hr": False,
                "memory_limit": 4.0
            },
            HardwareProfile.MID_RANGE: {
                "max_resolution": (768, 768),
                "max_batch_size": 2,
                "recommended_steps": (15, 30),
                "enable_hr": True,
                "memory_limit": 8.0
            },
            HardwareProfile.HIGH_END: {
                "max_resolution": (1024, 1024),
                "max_batch_size": 4,
                "recommended_steps": (20, 50),
                "enable_hr": True,
                "memory_limit": 12.0
            },
            HardwareProfile.ENTHUSIAST: {
                "max_resolution": (1536, 1536),
                "max_batch_size": 8,
                "recommended_steps": (25, 80),
                "enable_hr": True,
                "memory_limit": 24.0
            }
        }
        
        # 采样器性能特征
        self.sampler_profiles = {
            "DPM++ 2M Karras": {"speed": 0.9, "quality": 0.8, "stability": 0.9},
            "DPM++ SDE Karras": {"speed": 0.6, "quality": 0.95, "stability": 0.8},
            "Euler a": {"speed": 0.95, "quality": 0.7, "stability": 0.6},
            "Euler": {"speed": 0.9, "quality": 0.75, "stability": 0.8},
            "DDIM": {"speed": 0.7, "quality": 0.85, "stability": 0.95},
            "PLMS": {"speed": 0.8, "quality": 0.8, "stability": 0.85},
            "LMS Karras": {"speed": 0.85, "quality": 0.75, "stability": 0.8},
            "DPM++ 2S a Karras": {"speed": 0.5, "quality": 0.9, "stability": 0.85},
            "Heun": {"speed": 0.4, "quality": 0.85, "stability": 0.9}
        }
    
    def optimize_parameters(self, context: OptimizationContext) -> OptimizationResult:
        """
        根据优化上下文推荐最佳参数
        
        Args:
            context: 优化上下文
            
        Returns:
            优化结果
        """
        # 获取硬件限制
        hw_config = self.hardware_configs[context.hardware_profile]
        
        # 选择基础预设
        base_preset = self._select_base_preset(context)
        
        # 应用优化策略
        optimized_params = self._apply_optimization_strategy(base_preset, context, hw_config)
        
        # 计算性能指标
        performance_metrics = self._calculate_performance_metrics(optimized_params, context)
        
        # 生成替代配置
        alternatives = self._generate_alternatives(optimized_params, context, hw_config)
        
        # 生成优化建议和警告
        notes, warnings = self._generate_recommendations(optimized_params, context, performance_metrics)
        
        result = OptimizationResult(
            recommended_params=optimized_params,
            confidence_score=performance_metrics["confidence"],
            estimated_time=performance_metrics["estimated_time"],
            memory_usage=performance_metrics["memory_usage"],
            quality_score=performance_metrics["quality_score"],
            alternative_configs=alternatives,
            optimization_notes=notes,
            warnings=warnings
        )
        
        # 记录优化历史
        self.optimization_history.append({
            "timestamp": time.time(),
            "context": asdict(context),
            "result": asdict(result)
        })
        
        return result
    
    def _select_base_preset(self, context: OptimizationContext) -> Dict[str, Any]:
        """
        选择最适合的基础预设
        """
        goal_preset_mapping = {
            OptimizationGoal.SPEED: "quick_preview",
            OptimizationGoal.QUALITY: "high_quality",
            OptimizationGoal.BALANCED: "standard",
            OptimizationGoal.MEMORY: "quick_preview",
            OptimizationGoal.BATCH: "batch_generation",
            OptimizationGoal.CREATIVE: "creative_exploration"
        }
        
        # 根据用例调整
        if context.use_case == "portrait":
            preset_name = "portrait"
        elif context.use_case == "landscape":
            preset_name = "landscape"
        elif context.use_case == "3d_modeling":
            preset_name = "for_3d_model"
        else:
            preset_name = goal_preset_mapping.get(context.goal, "standard")
        
        return get_preset(preset_name) or get_preset("standard")
    
    def _apply_optimization_strategy(self, base_params: Dict[str, Any], 
                                   context: OptimizationContext, 
                                   hw_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        应用具体的优化策略
        """
        params = base_params.copy()
        
        # 硬件限制优化
        params = self._apply_hardware_constraints(params, context, hw_config)
        
        # 目标导向优化
        if context.goal == OptimizationGoal.SPEED:
            params = self._optimize_for_speed(params, context)
        elif context.goal == OptimizationGoal.QUALITY:
            params = self._optimize_for_quality(params, context)
        elif context.goal == OptimizationGoal.MEMORY:
            params = self._optimize_for_memory(params, context)
        elif context.goal == OptimizationGoal.BATCH:
            params = self._optimize_for_batch(params, context)
        elif context.goal == OptimizationGoal.CREATIVE:
            params = self._optimize_for_creativity(params, context)
        else:  # BALANCED
            params = self._optimize_balanced(params, context)
        
        # 时间约束优化
        if context.time_constraint:
            params = self._apply_time_constraints(params, context)
        
        return params
    
    def _apply_hardware_constraints(self, params: Dict[str, Any], 
                                  context: OptimizationContext, 
                                  hw_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        应用硬件约束
        """
        # 分辨率限制
        max_w, max_h = hw_config["max_resolution"]
        target_w, target_h = context.target_resolution
        
        if target_w > max_w or target_h > max_h:
            # 按比例缩放到硬件限制内
            scale = min(max_w / target_w, max_h / target_h)
            params["width"] = int(target_w * scale // 64) * 64  # 确保是64的倍数
            params["height"] = int(target_h * scale // 64) * 64
        else:
            params["width"] = target_w
            params["height"] = target_h
        
        # 批次大小限制
        params["batch_size"] = min(params.get("batch_size", 1), hw_config["max_batch_size"])
        
        # 高分辨率修复限制
        if not hw_config["enable_hr"]:
            params["enable_hr"] = False
        
        # 步数限制
        min_steps, max_steps = hw_config["recommended_steps"]
        params["steps"] = max(min_steps, min(params.get("steps", 20), max_steps))
        
        return params
    
    def _optimize_for_speed(self, params: Dict[str, Any], context: OptimizationContext) -> Dict[str, Any]:
        """
        速度优化
        """
        # 选择最快的采样器
        fast_samplers = ["DPM++ 2M Karras", "Euler a", "LMS Karras"]
        params["sampler_name"] = fast_samplers[0]
        
        # 减少步数
        params["steps"] = min(params.get("steps", 20), 15)
        
        # 禁用高分辨率修复
        params["enable_hr"] = False
        
        # 禁用面部修复
        params["restore_faces"] = False
        
        # 降低CFG Scale
        params["cfg_scale"] = min(params.get("cfg_scale", 7.0), 6.0)
        
        return params
    
    def _optimize_for_quality(self, params: Dict[str, Any], context: OptimizationContext) -> Dict[str, Any]:
        """
        质量优化
        """
        # 选择高质量采样器
        quality_samplers = ["DPM++ SDE Karras", "DPM++ 2S a Karras", "DDIM"]
        params["sampler_name"] = quality_samplers[0]
        
        # 增加步数
        params["steps"] = max(params.get("steps", 20), 25)
        
        # 启用高分辨率修复
        if context.hardware_profile != HardwareProfile.LOW_END:
            params["enable_hr"] = True
            params["hr_scale"] = 1.5
        
        # 启用面部修复
        params["restore_faces"] = True
        
        # 优化CFG Scale
        params["cfg_scale"] = max(params.get("cfg_scale", 7.0), 8.0)
        
        return params
    
    def _optimize_for_memory(self, params: Dict[str, Any], context: OptimizationContext) -> Dict[str, Any]:
        """
        内存优化
        """
        # 最小批次大小
        params["batch_size"] = 1
        params["n_iter"] = 1
        
        # 禁用高分辨率修复
        params["enable_hr"] = False
        
        # 降低分辨率
        params["width"] = min(params.get("width", 512), 512)
        params["height"] = min(params.get("height", 512), 512)
        
        # 选择内存友好的采样器
        params["sampler_name"] = "DPM++ 2M Karras"
        
        return params
    
    def _optimize_for_batch(self, params: Dict[str, Any], context: OptimizationContext) -> Dict[str, Any]:
        """
        批量生成优化
        """
        # 平衡批次大小和质量
        max_batch = self.hardware_configs[context.hardware_profile]["max_batch_size"]
        params["batch_size"] = min(context.batch_requirement, max_batch)
        
        # 适中的步数
        params["steps"] = 15
        
        # 选择稳定的采样器
        params["sampler_name"] = "DPM++ 2M Karras"
        
        # 禁用高分辨率修复以节省时间
        params["enable_hr"] = False
        
        return params
    
    def _optimize_for_creativity(self, params: Dict[str, Any], context: OptimizationContext) -> Dict[str, Any]:
        """
        创意优化
        """
        # 选择创意采样器
        creative_samplers = ["Euler a", "Euler", "Heun"]
        params["sampler_name"] = creative_samplers[0]
        
        # 降低CFG Scale以增加创意性
        params["cfg_scale"] = min(params.get("cfg_scale", 7.0), 6.0)
        
        # 适中的步数
        params["steps"] = 20
        
        # 增加批次以获得更多变体
        max_batch = self.hardware_configs[context.hardware_profile]["max_batch_size"]
        params["batch_size"] = min(2, max_batch)
        
        return params
    
    def _optimize_balanced(self, params: Dict[str, Any], context: OptimizationContext) -> Dict[str, Any]:
        """
        平衡优化
        """
        # 选择平衡的采样器
        params["sampler_name"] = "DPM++ 2M Karras"
        
        # 平衡的步数
        params["steps"] = 20
        
        # 平衡的CFG Scale
        params["cfg_scale"] = 7.0
        
        # 根据硬件决定是否启用高分辨率修复
        if context.hardware_profile in [HardwareProfile.HIGH_END, HardwareProfile.ENTHUSIAST]:
            params["enable_hr"] = True
            params["hr_scale"] = 1.3
        
        return params
    
    def _apply_time_constraints(self, params: Dict[str, Any], context: OptimizationContext) -> Dict[str, Any]:
        """
        应用时间约束
        """
        estimated_time = self._estimate_generation_time(params, context)
        
        if estimated_time > context.time_constraint:
            # 需要加速
            reduction_factor = context.time_constraint / estimated_time
            
            # 按优先级减少参数
            if reduction_factor < 0.5:
                # 大幅减少
                params["steps"] = max(8, int(params["steps"] * 0.5))
                params["enable_hr"] = False
                params["batch_size"] = 1
            elif reduction_factor < 0.8:
                # 适度减少
                params["steps"] = max(10, int(params["steps"] * 0.7))
                if params.get("enable_hr"):
                    params["hr_scale"] = min(params.get("hr_scale", 1.5), 1.3)
        
        return params
    
    def _calculate_performance_metrics(self, params: Dict[str, Any], 
                                     context: OptimizationContext) -> Dict[str, float]:
        """
        计算性能指标
        """
        # 估算生成时间
        estimated_time = self._estimate_generation_time(params, context)
        
        # 估算内存使用
        memory_usage = self._estimate_memory_usage(params, context)
        
        # 估算质量分数
        quality_score = self._estimate_quality_score(params, context)
        
        # 计算置信度
        confidence = self._calculate_confidence(params, context, estimated_time, memory_usage, quality_score)
        
        return {
            "estimated_time": estimated_time,
            "memory_usage": memory_usage,
            "quality_score": quality_score,
            "confidence": confidence
        }
    
    def _estimate_generation_time(self, params: Dict[str, Any], context: OptimizationContext) -> float:
        """
        估算生成时间（秒）
        """
        # 基础时间计算
        base_time = 2.0  # 基础时间
        
        # 分辨率影响
        pixels = params.get("width", 512) * params.get("height", 512)
        resolution_factor = pixels / (512 * 512)
        
        # 步数影响
        steps_factor = params.get("steps", 20) / 20
        
        # 批次影响
        batch_factor = params.get("batch_size", 1) * params.get("n_iter", 1)
        
        # 采样器影响
        sampler_speed = self.sampler_profiles.get(params.get("sampler_name", "DPM++ 2M Karras"), {}).get("speed", 0.8)
        sampler_factor = 1.0 / sampler_speed
        
        # 高分辨率修复影响
        hr_factor = 1.5 if params.get("enable_hr", False) else 1.0
        
        # 硬件影响
        hardware_multiplier = {
            HardwareProfile.LOW_END: 2.0,
            HardwareProfile.MID_RANGE: 1.0,
            HardwareProfile.HIGH_END: 0.6,
            HardwareProfile.ENTHUSIAST: 0.3
        }.get(context.hardware_profile, 1.0)
        
        total_time = (base_time * resolution_factor * steps_factor * 
                     batch_factor * sampler_factor * hr_factor * hardware_multiplier)
        
        return total_time
    
    def _estimate_memory_usage(self, params: Dict[str, Any], context: OptimizationContext) -> float:
        """
        估算内存使用（GB）
        """
        # 基础内存使用
        base_memory = 2.0
        
        # 分辨率影响
        pixels = params.get("width", 512) * params.get("height", 512)
        resolution_factor = pixels / (512 * 512)
        
        # 批次影响
        batch_factor = params.get("batch_size", 1)
        
        # 高分辨率修复影响
        hr_factor = 1.3 if params.get("enable_hr", False) else 1.0
        
        total_memory = base_memory * resolution_factor * batch_factor * hr_factor
        
        return total_memory
    
    def _estimate_quality_score(self, params: Dict[str, Any], context: OptimizationContext) -> float:
        """
        估算质量分数（0-1）
        """
        score = 0.5  # 基础分数
        
        # 步数影响
        steps = params.get("steps", 20)
        if steps >= 25:
            score += 0.2
        elif steps >= 15:
            score += 0.1
        elif steps < 10:
            score -= 0.1
        
        # 采样器影响
        sampler_quality = self.sampler_profiles.get(params.get("sampler_name", "DPM++ 2M Karras"), {}).get("quality", 0.8)
        score += (sampler_quality - 0.8) * 0.3
        
        # CFG Scale影响
        cfg = params.get("cfg_scale", 7.0)
        if 6.0 <= cfg <= 10.0:
            score += 0.1
        elif cfg > 15.0 or cfg < 3.0:
            score -= 0.1
        
        # 高分辨率修复影响
        if params.get("enable_hr", False):
            score += 0.15
        
        # 面部修复影响
        if params.get("restore_faces", False):
            score += 0.05
        
        return max(0.0, min(1.0, score))
    
    def _calculate_confidence(self, params: Dict[str, Any], context: OptimizationContext,
                            estimated_time: float, memory_usage: float, quality_score: float) -> float:
        """
        计算推荐置信度
        """
        confidence = 0.8  # 基础置信度
        
        # 硬件匹配度
        hw_limit = self.hardware_configs[context.hardware_profile]["memory_limit"]
        if memory_usage <= hw_limit * 0.8:
            confidence += 0.1
        elif memory_usage > hw_limit:
            confidence -= 0.3
        
        # 时间约束匹配度
        if context.time_constraint:
            if estimated_time <= context.time_constraint:
                confidence += 0.1
            else:
                confidence -= 0.2
        
        # 质量阈值匹配度
        if quality_score >= context.quality_threshold:
            confidence += 0.1
        else:
            confidence -= 0.1
        
        return max(0.0, min(1.0, confidence))
    
    def _generate_alternatives(self, base_params: Dict[str, Any], 
                             context: OptimizationContext, 
                             hw_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        生成替代配置
        """
        alternatives = []
        
        # 速度优化版本
        if context.goal != OptimizationGoal.SPEED:
            speed_params = base_params.copy()
            speed_params = self._optimize_for_speed(speed_params, context)
            speed_params["_variant_name"] = "速度优化版本"
            alternatives.append(speed_params)
        
        # 质量优化版本
        if context.goal != OptimizationGoal.QUALITY:
            quality_params = base_params.copy()
            quality_params = self._optimize_for_quality(quality_params, context)
            quality_params["_variant_name"] = "质量优化版本"
            alternatives.append(quality_params)
        
        # 内存优化版本
        if context.goal != OptimizationGoal.MEMORY:
            memory_params = base_params.copy()
            memory_params = self._optimize_for_memory(memory_params, context)
            memory_params["_variant_name"] = "内存优化版本"
            alternatives.append(memory_params)
        
        return alternatives[:3]  # 最多返回3个替代方案
    
    def _generate_recommendations(self, params: Dict[str, Any], 
                                context: OptimizationContext,
                                metrics: Dict[str, float]) -> Tuple[List[str], List[str]]:
        """
        生成优化建议和警告
        """
        notes = []
        warnings = []
        
        # 性能建议
        if metrics["estimated_time"] > 60:
            notes.append("生成时间较长，建议降低分辨率或步数以提高速度")
        
        if metrics["memory_usage"] > context.gpu_memory_gb * 0.9:
            warnings.append("内存使用接近上限，可能导致生成失败")
            notes.append("建议降低批次大小或分辨率")
        
        if metrics["quality_score"] < context.quality_threshold:
            notes.append("当前设置可能无法达到期望的质量水平")
            notes.append("建议增加步数或启用高分辨率修复")
        
        # 参数建议
        if params.get("cfg_scale", 7.0) > 12:
            warnings.append("CFG Scale过高可能导致过度饱和")
        
        if params.get("steps", 20) < 10:
            warnings.append("步数过少可能影响图像质量")
        
        # 硬件建议
        if context.hardware_profile == HardwareProfile.LOW_END:
            notes.append("当前硬件配置较低，建议使用快速预设")
        
        return notes, warnings
    
    def get_optimization_suggestions(self, current_params: Dict[str, Any], 
                                   performance_feedback: Dict[str, float]) -> List[str]:
        """
        根据性能反馈提供优化建议
        
        Args:
            current_params: 当前参数
            performance_feedback: 性能反馈 {"generation_time": float, "memory_used": float, "quality_rating": float}
            
        Returns:
            优化建议列表
        """
        suggestions = []
        
        actual_time = performance_feedback.get("generation_time", 0)
        actual_memory = performance_feedback.get("memory_used", 0)
        quality_rating = performance_feedback.get("quality_rating", 0.5)
        
        # 时间优化建议
        if actual_time > 120:  # 超过2分钟
            suggestions.append("生成时间过长，建议：")
            suggestions.append("- 减少步数到15-20")
            suggestions.append("- 使用更快的采样器如 'DPM++ 2M Karras'")
            suggestions.append("- 降低分辨率")
            if current_params.get("enable_hr"):
                suggestions.append("- 禁用高分辨率修复")
        
        # 内存优化建议
        if actual_memory > 6.0:  # 超过6GB
            suggestions.append("内存使用过高，建议：")
            suggestions.append("- 减少批次大小")
            suggestions.append("- 降低分辨率")
            suggestions.append("- 禁用高分辨率修复")
        
        # 质量优化建议
        if quality_rating < 0.6:
            suggestions.append("质量不满意，建议：")
            suggestions.append("- 增加步数到25-30")
            suggestions.append("- 使用高质量采样器如 'DPM++ SDE Karras'")
            suggestions.append("- 启用面部修复")
            suggestions.append("- 调整CFG Scale到7-9")
        
        return suggestions
    
    def save_optimization_profile(self, name: str, context: OptimizationContext, 
                                result: OptimizationResult, filename: str = "optimization_profiles.json"):
        """
        保存优化配置文件
        """
        profile = {
            "name": name,
            "context": asdict(context),
            "recommended_params": result.recommended_params,
            "performance_metrics": {
                "estimated_time": result.estimated_time,
                "memory_usage": result.memory_usage,
                "quality_score": result.quality_score,
                "confidence_score": result.confidence_score
            },
            "timestamp": time.time()
        }
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                profiles = json.load(f)
        except FileNotFoundError:
            profiles = {}
        
        profiles[name] = profile
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(profiles, f, ensure_ascii=False, indent=2)
        
        print(f"优化配置 '{name}' 已保存到 {filename}")
    
    def load_optimization_profile(self, name: str, filename: str = "optimization_profiles.json") -> Optional[Dict[str, Any]]:
        """
        加载优化配置文件
        """
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                profiles = json.load(f)
            return profiles.get(name)
        except FileNotFoundError:
            print(f"配置文件 {filename} 不存在")
            return None

# 便捷函数
def quick_optimize(goal: str = "balanced", gpu_memory: float = 8.0, 
                  resolution: Tuple[int, int] = (512, 512), 
                  use_case: str = "general") -> Dict[str, Any]:
    """
    快速优化参数
    
    Args:
        goal: 优化目标 (speed, quality, balanced, memory, batch, creative)
        gpu_memory: GPU内存大小(GB)
        resolution: 目标分辨率
        use_case: 使用场景
        
    Returns:
        优化后的参数
    """
    # 确定硬件配置
    if gpu_memory < 4:
        hw_profile = HardwareProfile.LOW_END
    elif gpu_memory < 8:
        hw_profile = HardwareProfile.MID_RANGE
    elif gpu_memory < 12:
        hw_profile = HardwareProfile.HIGH_END
    else:
        hw_profile = HardwareProfile.ENTHUSIAST
    
    # 创建优化上下文
    context = OptimizationContext(
        goal=OptimizationGoal(goal),
        hardware_profile=hw_profile,
        gpu_memory_gb=gpu_memory,
        target_resolution=resolution,
        use_case=use_case
    )
    
    # 执行优化
    optimizer = SDParameterOptimizer()
    result = optimizer.optimize_parameters(context)
    
    return result.recommended_params

if __name__ == "__main__":
    # 演示用法
    print("🔧 Stable Diffusion 参数优化器")
    print("=" * 50)
    
    # 创建优化器
    optimizer = SDParameterOptimizer()
    
    # 示例1：高质量优化
    print("\n📈 示例1：高质量优化")
    context1 = OptimizationContext(
        goal=OptimizationGoal.QUALITY,
        hardware_profile=HardwareProfile.HIGH_END,
        gpu_memory_gb=10.0,
        target_resolution=(768, 768),
        use_case="portrait"
    )
    
    result1 = optimizer.optimize_parameters(context1)
    print(f"推荐参数: {result1.recommended_params['width']}x{result1.recommended_params['height']}")
    print(f"采样器: {result1.recommended_params['sampler_name']}")
    print(f"步数: {result1.recommended_params['steps']}")
    print(f"预估时间: {result1.estimated_time:.1f}秒")
    print(f"质量分数: {result1.quality_score:.2f}")
    print(f"置信度: {result1.confidence_score:.2f}")
    
    # 示例2：速度优化
    print("\n⚡ 示例2：速度优化")
    context2 = OptimizationContext(
        goal=OptimizationGoal.SPEED,
        hardware_profile=HardwareProfile.MID_RANGE,
        gpu_memory_gb=6.0,
        target_resolution=(512, 512),
        time_constraint=30  # 30秒内完成
    )
    
    result2 = optimizer.optimize_parameters(context2)
    print(f"推荐参数: {result2.recommended_params['width']}x{result2.recommended_params['height']}")
    print(f"采样器: {result2.recommended_params['sampler_name']}")
    print(f"步数: {result2.recommended_params['steps']}")
    print(f"预估时间: {result2.estimated_time:.1f}秒")
    
    # 示例3：快速优化函数
    print("\n🚀 示例3：快速优化")
    quick_params = quick_optimize(goal="balanced", gpu_memory=8.0, resolution=(768, 768))
    print(f"快速优化结果: {quick_params['width']}x{quick_params['height']}, {quick_params['steps']}步")
    
    print("\n✅ 优化演示完成！")