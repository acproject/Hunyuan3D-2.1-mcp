#!/usr/bin/env python3
"""
Simple test script for AUTOMATIC1111 WebUI integration

This script tests basic WebUI connectivity and the existing integration in server.py
"""

import sys
import os
import requests
import json
import time
from pathlib import Path

def test_webui_connectivity(api_url="http://localhost:7860"):
    """
    Test basic connectivity to AUTOMATIC1111 WebUI API
    """
    print("\n🔍 Testing WebUI connectivity...")
    
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

def test_webui_models(api_url="http://localhost:7860"):
    """
    Test getting available models from WebUI
    """
    print("\n📋 Testing model availability...")
    
    try:
        response = requests.get(f"{api_url}/sdapi/v1/sd-models", timeout=10)
        if response.status_code == 200:
            models = response.json()
            print(f"✅ Found {len(models)} available models")
            if models:
                print(f"   Current model: {models[0].get('title', 'Unknown')}")
            return True
        else:
            print(f"❌ Failed to get models: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error getting models: {e}")
        return False

def test_webui_samplers(api_url="http://localhost:7860"):
    """
    Test getting available samplers from WebUI
    """
    print("\n🎛️ Testing sampler availability...")
    
    try:
        response = requests.get(f"{api_url}/sdapi/v1/samplers", timeout=10)
        if response.status_code == 200:
            samplers = response.json()
            print(f"✅ Found {len(samplers)} available samplers")
            if samplers:
                sampler_names = [s.get('name', 'Unknown') for s in samplers[:3]]
                print(f"   Available: {', '.join(sampler_names)}...")
            return True
        else:
            print(f"❌ Failed to get samplers: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error getting samplers: {e}")
        return False

def test_basic_txt2img(api_url="http://localhost:7860"):
    """
    Test basic text-to-image generation using direct API call
    """
    print("\n🎨 Testing basic text-to-image generation...")
    
    try:
        payload = {
            "prompt": "a beautiful sunset over mountains, digital art, high quality",
            "negative_prompt": "blurry, low quality, distorted",
            "width": 512,
            "height": 512,
            "steps": 10,  # Use fewer steps for faster testing
            "cfg_scale": 7.0,
            "sampler_name": "DPM++ 2M Karras",
            "batch_size": 1,
            "n_iter": 1,
            "seed": -1
        }
        
        print("   Sending generation request...")
        response = requests.post(f"{api_url}/sdapi/v1/txt2img", json=payload, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            if 'images' in result and result['images']:
                print("✅ Text-to-image generation successful")
                print(f"   Generated {len(result['images'])} image(s)")
                
                # Save the first image for verification
                import base64
                from PIL import Image
                import io
                
                image_data = base64.b64decode(result['images'][0])
                image = Image.open(io.BytesIO(image_data))
                
                # Create output directory if it doesn't exist
                output_dir = Path("test_outputs")
                output_dir.mkdir(exist_ok=True)
                
                output_path = output_dir / "test_image.png"
                image.save(output_path)
                print(f"   Image saved to: {output_path}")
                
                return True
            else:
                print("❌ No images in response")
                return False
        else:
            print(f"❌ Generation failed with status: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Text-to-image test failed: {e}")
        return False

def test_existing_integration():
    """
    Test if the existing server.py integration can be imported
    """
    print("\n🔧 Testing existing integration...")
    
    try:
        # Add the src directory to the path
        src_path = os.path.join(os.path.dirname(__file__), 'src')
        if src_path not in sys.path:
            sys.path.insert(0, src_path)
        
        # Try to import the server module
        from blender_mcp import server
        print("✅ Successfully imported blender_mcp.server")
        
        # Check if generate_stable_diffusion_image function exists
        if hasattr(server, 'generate_stable_diffusion_image'):
            print("✅ generate_stable_diffusion_image function found")
        else:
            print("❌ generate_stable_diffusion_image function not found")
            return False
        
        # Check if enhanced tools are available
        if hasattr(server, 'ENHANCED_WEBUI_AVAILABLE'):
            enhanced_available = getattr(server, 'ENHANCED_WEBUI_AVAILABLE', False)
            if enhanced_available:
                print("✅ Enhanced WebUI tools are available")
            else:
                print("⚠️ Enhanced WebUI tools are not available (this is expected if modules are missing)")
        
        return True
        
    except ImportError as e:
        print(f"❌ Failed to import server module: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing existing integration: {e}")
        return False

def check_enhanced_files():
    """
    Check if the enhanced integration files exist
    """
    print("\n📁 Checking enhanced integration files...")
    
    files_to_check = [
        "enhanced_webui_integration.py",
        "enhanced_webui_tools.py",
        "src/blender_mcp/server.py"
    ]
    
    all_exist = True
    
    for file_path in files_to_check:
        full_path = Path(file_path)
        if full_path.exists():
            print(f"✅ {file_path} exists")
        else:
            print(f"❌ {file_path} not found")
            all_exist = False
    
    return all_exist

def main():
    """
    Run all tests
    """
    print("🧪 Simple AUTOMATIC1111 WebUI Integration Test")
    print("=" * 50)
    
    api_url = "http://localhost:7860"
    
    # Track test results
    tests = [
        ("Enhanced Files Check", check_enhanced_files),
        ("Existing Integration", test_existing_integration),
        ("WebUI Connectivity", lambda: test_webui_connectivity(api_url)),
        ("Model Availability", lambda: test_webui_models(api_url)),
        ("Sampler Availability", lambda: test_webui_samplers(api_url)),
        ("Basic Text-to-Image", lambda: test_basic_txt2img(api_url))
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
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
    
    if passed >= 4:  # At least basic functionality works
        print("🎉 Basic integration is working! You can use AUTOMATIC1111 WebUI with this project.")
    elif passed >= 2:  # Files exist and can be imported
        print("⚠️ Integration files are ready, but WebUI may not be running.")
        print("   Start AUTOMATIC1111 WebUI with --api flag to enable full functionality.")
    else:
        print("❌ Integration setup needs attention. Check the troubleshooting tips below.")
    
    # Provide setup instructions
    print("\n🔧 Setup Instructions:")
    print("1. Install AUTOMATIC1111 WebUI: https://github.com/AUTOMATIC1111/stable-diffusion-webui")
    print("2. Start WebUI with API enabled: ./webui.sh --api (Linux/Mac) or webui.bat --api (Windows)")
    print("3. Ensure WebUI is accessible at http://localhost:7860")
    print("4. Install required Python packages: pip install requests pillow")
    print("5. Run this test again to verify functionality")

if __name__ == "__main__":
    main()