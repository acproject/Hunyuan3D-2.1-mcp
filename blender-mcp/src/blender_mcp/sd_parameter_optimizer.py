#!/usr/bin/env python3
"""
Stable Diffusion Parameter Optimizer

This module provides intelligent parameter optimization for Stable Diffusion generation
based on various goals, hardware profiles, and image types.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
import json
import logging

logger = logging.getLogger(__name__)

class OptimizationGoal(Enum):
    """Optimization goals for parameter tuning."""
    QUALITY = "quality"
    SPEED = "speed"
    BALANCED = "balanced"
    MEMORY = "memory"
    ARTISTIC = "artistic"

class HardwareProfile(Enum):
    """Hardware performance profiles."""
    LOW = "low"        # Low-end hardware (4GB VRAM or less)
    MEDIUM = "medium"  # Mid-range hardware (6-8GB VRAM)
    HIGH = "high"      # High-end hardware (10GB+ VRAM)
    ULTRA = "ultra"    # Enthusiast hardware (16GB+ VRAM)

@dataclass
class OptimizationContext:
    """Context information for optimization decisions."""
    goal: OptimizationGoal
    hardware: HardwareProfile
    image_type: str = "general"  # general, portrait, landscape, artistic
    time_budget: int = 60  # seconds
    quality_preference: float = 0.7  # 0.0 to 1.0
    batch_size: int = 1
    target_resolution: Optional[tuple] = None

class SDParameterOptimizer:
    """Intelligent parameter optimizer for Stable Diffusion."""
    
    def __init__(self):
        self.base_parameters = {
            "steps": 20,
            "cfg_scale": 7.0,
            "sampler_name": "DPM++ 2M Karras",
            "width": 512,
            "height": 512,
            "enable_hr": False,
            "hr_scale": 1.5,
            "denoising_strength": 0.7,
            "batch_size": 1,
            "n_iter": 1
        }
        
        # Sampler performance characteristics
        self.sampler_profiles = {
            "Euler a": {"speed": 1.0, "quality": 0.7, "memory": 1.0},
            "Euler": {"speed": 0.9, "quality": 0.75, "memory": 1.0},
            "LMS": {"speed": 0.8, "quality": 0.8, "memory": 1.0},
            "Heun": {"speed": 0.5, "quality": 0.85, "memory": 1.0},
            "DPM2": {"speed": 0.6, "quality": 0.85, "memory": 1.0},
            "DPM2 a": {"speed": 0.6, "quality": 0.87, "memory": 1.0},
            "DPM++ 2S a": {"speed": 0.7, "quality": 0.88, "memory": 1.0},
            "DPM++ 2M": {"speed": 0.8, "quality": 0.9, "memory": 1.0},
            "DPM++ 2M Karras": {"speed": 0.8, "quality": 0.92, "memory": 1.0},
            "DPM++ SDE": {"speed": 0.6, "quality": 0.9, "memory": 1.0},
            "DPM++ SDE Karras": {"speed": 0.6, "quality": 0.93, "memory": 1.0},
            "DPM++ 2M SDE": {"speed": 0.5, "quality": 0.95, "memory": 0.9},
            "DPM++ 2M SDE Karras": {"speed": 0.5, "quality": 0.96, "memory": 0.9},
            "DDIM": {"speed": 0.9, "quality": 0.8, "memory": 1.0},
            "PLMS": {"speed": 0.85, "quality": 0.82, "memory": 1.0}
        }
    
    def optimize(self, context: OptimizationContext) -> Dict[str, Any]:
        """Optimize parameters based on the given context."""
        params = self.base_parameters.copy()
        
        # Apply goal-based optimizations
        params = self._apply_goal_optimization(params, context)
        
        # Apply hardware-based optimizations
        params = self._apply_hardware_optimization(params, context)
        
        # Apply image type optimizations
        params = self._apply_image_type_optimization(params, context)
        
        # Apply time budget constraints
        params = self._apply_time_constraints(params, context)
        
        # Validate and adjust parameters
        params = self._validate_parameters(params, context)
        
        logger.info(f"Optimized parameters for {context.goal.value} goal on {context.hardware.value} hardware")
        return params
    
    def _apply_goal_optimization(self, params: Dict[str, Any], context: OptimizationContext) -> Dict[str, Any]:
        """Apply optimizations based on the primary goal."""
        if context.goal == OptimizationGoal.QUALITY:
            params["steps"] = 30
            params["cfg_scale"] = 8.0
            params["sampler_name"] = "DPM++ 2M SDE Karras"
            params["enable_hr"] = True
            params["hr_scale"] = 1.5
            
        elif context.goal == OptimizationGoal.SPEED:
            params["steps"] = 15
            params["cfg_scale"] = 6.0
            params["sampler_name"] = "Euler a"
            params["enable_hr"] = False
            
        elif context.goal == OptimizationGoal.BALANCED:
            params["steps"] = 20
            params["cfg_scale"] = 7.0
            params["sampler_name"] = "DPM++ 2M Karras"
            params["enable_hr"] = context.hardware != HardwareProfile.LOW
            
        elif context.goal == OptimizationGoal.MEMORY:
            params["steps"] = 18
            params["cfg_scale"] = 6.5
            params["sampler_name"] = "Euler a"
            params["enable_hr"] = False
            params["batch_size"] = 1
            
        elif context.goal == OptimizationGoal.ARTISTIC:
            params["steps"] = 35
            params["cfg_scale"] = 9.0
            params["sampler_name"] = "DPM++ SDE Karras"
            params["enable_hr"] = True
            params["hr_scale"] = 1.6
        
        return params
    
    def _apply_hardware_optimization(self, params: Dict[str, Any], context: OptimizationContext) -> Dict[str, Any]:
        """Apply optimizations based on hardware capabilities."""
        if context.hardware == HardwareProfile.LOW:
            params["width"] = min(512, params["width"])
            params["height"] = min(512, params["height"])
            params["enable_hr"] = False
            params["batch_size"] = 1
            params["steps"] = max(10, params["steps"] - 5)
            
        elif context.hardware == HardwareProfile.MEDIUM:
            params["width"] = min(768, params["width"])
            params["height"] = min(768, params["height"])
            if params["enable_hr"]:
                params["hr_scale"] = min(1.5, params["hr_scale"])
                
        elif context.hardware == HardwareProfile.HIGH:
            params["width"] = min(1024, params.get("width", 512))
            params["height"] = min(1024, params.get("height", 512))
            if not params["enable_hr"] and context.goal != OptimizationGoal.SPEED:
                params["enable_hr"] = True
                params["hr_scale"] = 1.5
                
        elif context.hardware == HardwareProfile.ULTRA:
            params["width"] = min(1536, params.get("width", 512))
            params["height"] = min(1536, params.get("height", 512))
            params["enable_hr"] = True
            params["hr_scale"] = min(2.0, params["hr_scale"] + 0.2)
            params["steps"] = min(50, params["steps"] + 5)
        
        return params
    
    def _apply_image_type_optimization(self, params: Dict[str, Any], context: OptimizationContext) -> Dict[str, Any]:
        """Apply optimizations based on image type."""
        if context.image_type == "portrait":
            params["width"] = min(params["width"], 512)
            params["height"] = max(params["height"], 768)
            params["cfg_scale"] = min(8.0, params["cfg_scale"] + 0.5)
            
        elif context.image_type == "landscape":
            params["width"] = max(params["width"], 768)
            params["height"] = min(params["height"], 512)
            params["cfg_scale"] = min(9.0, params["cfg_scale"] + 1.0)
            
        elif context.image_type == "artistic":
            params["cfg_scale"] = min(10.0, params["cfg_scale"] + 1.5)
            params["steps"] = min(40, params["steps"] + 5)
            if "SDE" not in params["sampler_name"]:
                params["sampler_name"] = "DPM++ SDE Karras"
        
        return params
    
    def _apply_time_constraints(self, params: Dict[str, Any], context: OptimizationContext) -> Dict[str, Any]:
        """Apply time budget constraints."""
        if context.time_budget < 30:  # Very tight time budget
            params["steps"] = min(15, params["steps"])
            params["sampler_name"] = "Euler a"
            params["enable_hr"] = False
            
        elif context.time_budget < 60:  # Moderate time budget
            params["steps"] = min(20, params["steps"])
            if params["enable_hr"]:
                params["hr_scale"] = min(1.3, params["hr_scale"])
                
        # For longer time budgets, allow current settings
        return params
    
    def _validate_parameters(self, params: Dict[str, Any], context: OptimizationContext) -> Dict[str, Any]:
        """Validate and adjust parameters for consistency."""
        # Ensure minimum values
        params["steps"] = max(5, params["steps"])
        params["cfg_scale"] = max(1.0, min(20.0, params["cfg_scale"]))
        params["width"] = max(64, params["width"])
        params["height"] = max(64, params["height"])
        
        # Ensure dimensions are multiples of 8
        params["width"] = (params["width"] // 8) * 8
        params["height"] = (params["height"] // 8) * 8
        
        # Validate sampler
        if params["sampler_name"] not in self.sampler_profiles:
            params["sampler_name"] = "DPM++ 2M Karras"
        
        # Apply target resolution if specified
        if context.target_resolution:
            params["width"], params["height"] = context.target_resolution
        
        return params
    
    def get_sampler_recommendation(self, context: OptimizationContext) -> str:
        """Get the best sampler for the given context."""
        goal_weights = {
            OptimizationGoal.QUALITY: {"speed": 0.2, "quality": 0.8, "memory": 0.0},
            OptimizationGoal.SPEED: {"speed": 0.8, "quality": 0.2, "memory": 0.0},
            OptimizationGoal.BALANCED: {"speed": 0.4, "quality": 0.6, "memory": 0.0},
            OptimizationGoal.MEMORY: {"speed": 0.3, "quality": 0.2, "memory": 0.5},
            OptimizationGoal.ARTISTIC: {"speed": 0.1, "quality": 0.9, "memory": 0.0}
        }
        
        weights = goal_weights[context.goal]
        best_sampler = None
        best_score = -1
        
        for sampler, profile in self.sampler_profiles.items():
            score = (
                profile["speed"] * weights["speed"] +
                profile["quality"] * weights["quality"] +
                profile["memory"] * weights["memory"]
            )
            
            if score > best_score:
                best_score = score
                best_sampler = sampler
        
        return best_sampler
    
    def estimate_generation_time(self, params: Dict[str, Any], context: OptimizationContext) -> float:
        """Estimate generation time in seconds."""
        base_time = 2.0  # Base time per step
        
        # Hardware multipliers
        hardware_multipliers = {
            HardwareProfile.LOW: 3.0,
            HardwareProfile.MEDIUM: 1.5,
            HardwareProfile.HIGH: 1.0,
            HardwareProfile.ULTRA: 0.7
        }
        
        # Sampler speed multiplier
        sampler_speed = self.sampler_profiles.get(params["sampler_name"], {"speed": 1.0})["speed"]
        
        # Resolution multiplier
        pixels = params["width"] * params["height"]
        resolution_multiplier = pixels / (512 * 512)
        
        # High-res multiplier
        hr_multiplier = 1.0
        if params.get("enable_hr", False):
            hr_multiplier = 1.0 + (params.get("hr_scale", 1.5) - 1.0) * 0.8
        
        estimated_time = (
            base_time * params["steps"] * 
            hardware_multipliers[context.hardware] * 
            (1.0 / sampler_speed) * 
            resolution_multiplier * 
            hr_multiplier * 
            params.get("batch_size", 1) * 
            params.get("n_iter", 1)
        )
        
        return estimated_time

def quick_optimize(prompt: str, goal: str = "balanced", hardware: str = "medium") -> Dict[str, Any]:
    """Quick optimization function for simple use cases."""
    try:
        goal_enum = OptimizationGoal(goal)
    except ValueError:
        goal_enum = OptimizationGoal.BALANCED
    
    try:
        hardware_enum = HardwareProfile(hardware)
    except ValueError:
        hardware_enum = HardwareProfile.MEDIUM
    
    # Analyze prompt for image type
    image_type = "general"
    if any(word in prompt.lower() for word in ["portrait", "face", "person", "character"]):
        image_type = "portrait"
    elif any(word in prompt.lower() for word in ["landscape", "scenery", "nature", "outdoor"]):
        image_type = "landscape"
    elif any(word in prompt.lower() for word in ["art", "painting", "artistic", "style"]):
        image_type = "artistic"
    
    context = OptimizationContext(
        goal=goal_enum,
        hardware=hardware_enum,
        image_type=image_type
    )
    
    optimizer = SDParameterOptimizer()
    return optimizer.optimize(context)