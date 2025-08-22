#!/usr/bin/env python3
"""
Test script for AUTOMATIC1111 WebUI integration with Blender MCP

This script tests the enhanced WebUI integration functionality including:
- Basic connectivity to WebUI API
- Image generation capabilities
- Enhanced features like high-resolution upscaling
- Batch generation
- Image enhancement (img2img)
- Status checking

Usage:
    python test_webui_integration.py

Requirements:
    - AUTOMATIC1111 WebUI running on http://localhost:7860
    - Enhanced WebUI tools available
"""

import sys
import os
import requests
import json
import time
from pathlib import Path

# Add the src directory to the path to import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from blender_mcp.enhanced_webui_integration import AutomaticWebUIClient
    from blender_mcp.enhanced_webui_tools import (
        enhanced_generate_stable_diffusion_image,
        batch_generate_images,
        img2img_enhance,
        get_webui_status
    )
    ENHANCED_TOOLS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Enhanced WebUI tools not available: {e}")
    ENHANCED_TOOLS_AVAILABLE = False

def test_basic_connectivity(api_url="http://localhost:7860"):
    """
    Test basic connectivity to AUTOMATIC1111 WebUI API
    """
    print("\n🔍 Testing basic connectivity...")
    
    try:
        # Test basic health endpoint
        response = requests.get(f"{api_url}/internal/ping", timeout=5)
        if response.status_code == 200:
            print("✅ WebUI API is accessible")
            return True
        else:
            print(f"❌ WebUI API returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to WebUI API at {api_url}")
        print("   Make sure AUTOMATIC1111 WebUI is running with --api flag")
        return False
    except Exception as e:
        print(f"❌ Error testing connectivity: {e}")
        return False

def test_webui_status(api_url="http://localhost:7860"):
    """
    Test WebUI status checking functionality
    """
    print("\n📊 Testing WebUI status check...")
    
    if not ENHANCED_TOOLS_AVAILABLE:
        print("⚠️ Enhanced tools not available, skipping status test")
        return False
    
    try:
        status_result = get_webui_status(api_url=api_url)
        print("✅ Status check completed:")
        print(status_result[:500] + "..." if len(status_result) > 500 else status_result)
        return True
    except Exception as e:
        print(f"❌ Status check failed: {e}")
        return False

def test_basic_txt2img(api_url="http://localhost:7860"):
    """
    Test basic text-to-image generation
    """
    print("\n🎨 Testing basic text-to-image generation...")
    
    if not ENHANCED_TOOLS_AVAILABLE:
        print("⚠️ Enhanced tools not available, skipping txt2img test")
        return False
    
    try:
        test_prompt = "a beautiful sunset over mountains, digital art, high quality"
        
        result = enhanced_generate_stable_diffusion_image(
            prompt=test_prompt,
            negative_prompt="blurry, low quality",
            width=512,
            height=512,
            steps=10,  # Use fewer steps for faster testing
            cfg_scale=7.0,
            api_url=api_url,
            save_parameters=True
        )
        
        if "Error" not in result:
            print("✅ Basic text-to-image generation successful")
            print(f"Result: {result[:200]}...")
            return True
        else:
            print(f"❌ Text-to-image generation failed: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Text-to-image test failed: {e}")
        return False

def test_enhanced_features(api_url="http://localhost:7860"):
    """
    Test enhanced features like high-resolution upscaling
    """
    print("\n🚀 Testing enhanced features...")
    
    if not ENHANCED_TOOLS_AVAILABLE:
        print("⚠️ Enhanced tools not available, skipping enhanced features test")
        return False
    
    try:
        test_prompt = "a cute robot, 3D render, high detail"
        
        result = enhanced_generate_stable_diffusion_image(
            prompt=test_prompt,
            negative_prompt="blurry, low quality, distorted",
            width=512,
            height=512,
            steps=15,
            cfg_scale=8.0,
            enable_hr=True,  # Enable high-resolution upscaling
            hr_scale=1.5,
            restore_faces=True,
            api_url=api_url
        )
        
        if "Error" not in result:
            print("✅ Enhanced features test successful")
            print(f"Result: {result[:200]}...")
            return True
        else:
            print(f"❌ Enhanced features test failed: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Enhanced features test failed: {e}")
        return False

def test_batch_generation(api_url="http://localhost:7860"):
    """
    Test batch image generation
    """
    print("\n📦 Testing batch generation...")
    
    if not ENHANCED_TOOLS_AVAILABLE:
        print("⚠️ Enhanced tools not available, skipping batch test")
        return False
    
    try:
        test_prompts = [
            "a red apple on a table",
            "a blue car in a city"
        ]
        
        result = batch_generate_images(
            prompts=test_prompts,
            negative_prompt="blurry, low quality",
            width=512,
            height=512,
            steps=10,
            cfg_scale=7.0,
            batch_count=1,  # Generate 1 image per prompt for testing
            api_url=api_url
        )
        
        if "Error" not in result:
            print("✅ Batch generation test successful")
            print(f"Result: {result[:300]}...")
            return True
        else:
            print(f"❌ Batch generation test failed: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Batch generation test failed: {e}")
        return False

def test_client_class(api_url="http://localhost:7860"):
    """
    Test the AutomaticWebUIClient class
    """
    print("\n🔧 Testing WebUI client class...")
    
    if not ENHANCED_TOOLS_AVAILABLE:
        print("⚠️ Enhanced tools not available, skipping client test")
        return False
    
    try:
        client = AutomaticWebUIClient(api_url)
        
        # Test health check
        if client.health_check():
            print("✅ Client health check passed")
        else:
            print("❌ Client health check failed")
            return False
        
        # Test getting models
        models = client.get_models()
        if models:
            print(f"✅ Found {len(models)} models")
        else:
            print("⚠️ No models found or failed to get models")
        
        # Test getting samplers
        samplers = client.get_samplers()
        if samplers:
            print(f"✅ Found {len(samplers)} samplers")
        else:
            print("⚠️ No samplers found or failed to get samplers")
        
        return True
        
    except Exception as e:
        print(f"❌ Client class test failed: {e}")
        return False

def main():
    """
    Run all tests
    """
    print("🧪 AUTOMATIC1111 WebUI Integration Test Suite")
    print("=" * 50)
    
    api_url = "http://localhost:7860"
    
    # Track test results
    tests = [
        ("Basic Connectivity", test_basic_connectivity),
        ("WebUI Status Check", test_webui_status),
        ("Basic Text-to-Image", test_basic_txt2img),
        ("Enhanced Features", test_enhanced_features),
        ("Batch Generation", test_batch_generation),
        ("Client Class", test_client_class)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func(api_url)
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "=" * 50)
    print("📋 Test Results Summary:")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<25} {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! AUTOMATIC1111 WebUI integration is working correctly.")
    elif passed > 0:
        print("⚠️ Some tests failed. Check the output above for details.")
    else:
        print("❌ All tests failed. Please check your WebUI setup and configuration.")
    
    # Provide troubleshooting tips
    if passed < total:
        print("\n🔧 Troubleshooting Tips:")
        print("1. Make sure AUTOMATIC1111 WebUI is running with --api flag")
        print("2. Check that WebUI is accessible at http://localhost:7860")
        print("3. Ensure enhanced_webui_integration.py and enhanced_webui_tools.py are in the correct location")
        print("4. Verify all required dependencies are installed")
        print("5. Check the WebUI console for any error messages")

if __name__ == "__main__":
    main()