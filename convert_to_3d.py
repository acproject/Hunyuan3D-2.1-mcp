#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import base64
import os
import json
from datetime import datetime

def convert_image_to_3d():
    """使用Hunyuan3D服务将黄色小猫图片转换为3D模型"""
    
    # 图片路径
    image_path = os.path.join(os.path.expanduser('~'), 'Desktop', 'yellow_kitten.png')
    
    if not os.path.exists(image_path):
        print(f'❌ 图片文件不存在: {image_path}')
        return None
    
    # 读取并编码图片
    try:
        with open(image_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode()
    except Exception as e:
        print(f'❌ 读取图片失败: {str(e)}')
        return None
    
    # 直接使用8080端口（用户说已经启动了服务）
    api_url = 'http://localhost:8080'
    print(f'使用 Hunyuan3D 服务: {api_url}')
    
    # 检查服务是否可用（跳过健康检查，直接尝试生成）
    print('直接尝试生成3D模型（跳过健康检查）...')
    
    # 准备生成请求
    request_data = {
        "image": image_data,
        "remove_background": True,
        "texture": True,
        "seed": 1234,
        "octree_resolution": 256,
        "num_inference_steps": 5,
        "guidance_scale": 5.0,
        "num_chunks": 8000,
        "face_count": 40000,
        "type": "glb"
    }
    
    print('开始生成3D模型...')
    
    try:
        # 发送生成请求
        response = requests.post(f'{api_url}/generate', json=request_data, timeout=300)
        
        if response.status_code == 200:
            # 保存3D模型到桌面
            desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')
            model_path = os.path.join(desktop_path, 'yellow_kitten_3d.glb')
            
            with open(model_path, 'wb') as f:
                f.write(response.content)
            
            print(f'✅ 成功生成3D模型: {model_path}')
            print(f'模型参数:')
            print(f'  • 移除背景: {request_data["remove_background"]}')
            print(f'  • 生成纹理: {request_data["texture"]}')
            print(f'  • 分辨率: {request_data["octree_resolution"]}')
            print(f'  • 推理步数: {request_data["num_inference_steps"]}')
            
            return model_path
        else:
            print(f'❌ 3D生成失败: {response.status_code}')
            try:
                error_detail = response.json()
                print(f'错误详情: {json.dumps(error_detail, indent=2, ensure_ascii=False)}')
            except:
                print(f'错误响应: {response.text}')
            return None
            
    except Exception as e:
        print(f'❌ 生成3D模型时出错: {str(e)}')
        return None

if __name__ == '__main__':
    convert_image_to_3d()