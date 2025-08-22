#!/usr/bin/env python3
"""
Stable Diffusion Optimization Presets

This module provides predefined optimization presets for Stable Diffusion image generation.
"""

from typing import Dict, Any, List
import json

# Predefined optimization presets
PRESETS = {
    "quality": {
        "name": "High Quality",
        "description": "Optimized for maximum image quality",
        "steps": 30,
        "cfg_scale": 8.0,
        "sampler_name": "DPM++ 2M Karras",
        "width": 768,
        "height": 768,
        "enable_hr": True,
        "hr_scale": 1.5,
        "denoising_strength": 0.7
    },
    "speed": {
        "name": "Fast Generation",
        "description": "Optimized for speed with acceptable quality",
        "steps": 15,
        "cfg_scale": 6.0,
        "sampler_name": "Euler a",
        "width": 512,
        "height": 512,
        "enable_hr": False,
        "hr_scale": 1.0,
        "denoising_strength": 0.5
    },
    "balanced": {
        "name": "Balanced",
        "description": "Good balance between quality and speed",
        "steps": 20,
        "cfg_scale": 7.0,
        "sampler_name": "DPM++ 2M Karras",
        "width": 640,
        "height": 640,
        "enable_hr": False,
        "hr_scale": 1.2,
        "denoising_strength": 0.6
    },
    "portrait": {
        "name": "Portrait Optimized",
        "description": "Optimized for portrait and character generation",
        "steps": 25,
        "cfg_scale": 7.5,
        "sampler_name": "DPM++ SDE Karras",
        "width": 512,
        "height": 768,
        "enable_hr": True,
        "hr_scale": 1.3,
        "denoising_strength": 0.65
    },
    "landscape": {
        "name": "Landscape Optimized",
        "description": "Optimized for landscape and scenery generation",
        "steps": 28,
        "cfg_scale": 8.5,
        "sampler_name": "DPM++ 2M Karras",
        "width": 768,
        "height": 512,
        "enable_hr": True,
        "hr_scale": 1.4,
        "denoising_strength": 0.7
    },
    "artistic": {
        "name": "Artistic Style",
        "description": "Optimized for artistic and creative outputs",
        "steps": 35,
        "cfg_scale": 9.0,
        "sampler_name": "DPM++ 2M SDE Karras",
        "width": 768,
        "height": 768,
        "enable_hr": True,
        "hr_scale": 1.6,
        "denoising_strength": 0.75
    }
}

def get_preset(preset_name: str) -> Dict[str, Any]:
    """
    Get a specific optimization preset by name.
    
    Args:
        preset_name: Name of the preset to retrieve
        
    Returns:
        Dictionary containing preset parameters
        
    Raises:
        KeyError: If preset_name is not found
    """
    if preset_name not in PRESETS:
        raise KeyError(f"Preset '{preset_name}' not found. Available presets: {list(PRESETS.keys())}")
    
    return PRESETS[preset_name].copy()

def list_presets() -> List[str]:
    """
    Get a list of all available preset names.
    
    Returns:
        List of preset names
    """
    return list(PRESETS.keys())

def print_preset_info(preset_name: str = None) -> str:
    """
    Print information about a specific preset or all presets.
    
    Args:
        preset_name: Name of the preset to print info for. If None, prints all presets.
        
    Returns:
        Formatted string with preset information
    """
    if preset_name:
        if preset_name not in PRESETS:
            return f"Preset '{preset_name}' not found. Available presets: {list(PRESETS.keys())}"
        
        preset = PRESETS[preset_name]
        info = f"Preset: {preset_name}\n"
        info += f"Name: {preset['name']}\n"
        info += f"Description: {preset['description']}\n"
        info += "Parameters:\n"
        for key, value in preset.items():
            if key not in ['name', 'description']:
                info += f"  {key}: {value}\n"
        return info
    else:
        info = "Available Optimization Presets:\n\n"
        for name, preset in PRESETS.items():
            info += f"{name}: {preset['name']}\n"
            info += f"  {preset['description']}\n\n"
        return info

def get_preset_for_goal(goal: str, hardware: str = "medium") -> Dict[str, Any]:
    """
    Get the best preset for a specific goal and hardware configuration.
    
    Args:
        goal: Generation goal ("quality", "speed", "balanced", etc.)
        hardware: Hardware profile ("low", "medium", "high")
        
    Returns:
        Dictionary containing optimized preset parameters
    """
    # Map goals to base presets
    goal_mapping = {
        "quality": "quality",
        "speed": "speed",
        "balanced": "balanced",
        "portrait": "portrait",
        "landscape": "landscape",
        "artistic": "artistic"
    }
    
    base_preset = goal_mapping.get(goal, "balanced")
    preset = get_preset(base_preset)
    
    # Adjust based on hardware
    if hardware == "low":
        preset["steps"] = max(10, preset["steps"] - 10)
        preset["width"] = min(512, preset["width"])
        preset["height"] = min(512, preset["height"])
        preset["enable_hr"] = False
    elif hardware == "high":
        preset["steps"] = min(50, preset["steps"] + 10)
        preset["width"] = min(1024, preset["width"] + 128)
        preset["height"] = min(1024, preset["height"] + 128)
        if not preset["enable_hr"]:
            preset["enable_hr"] = True
            preset["hr_scale"] = 1.3
    
    return preset

def validate_preset(preset: Dict[str, Any]) -> bool:
    """
    Validate that a preset contains all required parameters.
    
    Args:
        preset: Preset dictionary to validate
        
    Returns:
        True if valid, False otherwise
    """
    required_keys = [
        "steps", "cfg_scale", "sampler_name", "width", "height",
        "enable_hr", "hr_scale", "denoising_strength"
    ]
    
    return all(key in preset for key in required_keys)

def merge_presets(base_preset: str, overrides: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge a base preset with custom overrides.
    
    Args:
        base_preset: Name of the base preset
        overrides: Dictionary of parameters to override
        
    Returns:
        Merged preset dictionary
    """
    preset = get_preset(base_preset)
    preset.update(overrides)
    return preset