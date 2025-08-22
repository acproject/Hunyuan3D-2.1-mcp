#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import base64
from PIL import Image
import torch

# 添加路径
sys.path.insert(0, './hy3dshape')
sys.path.insert(0, './hy3dpaint')

def direct_generate_3d():
    """直接调用Hunyuan3D生成函数"""
    
    # 图片路径
    image_path = os.path.join(os.path.expanduser('~'), 'Desktop', 'yellow_kitten.png')
    
    if not os.path.exists(image_path):
        print(f'❌ 图片文件不存在: {image_path}')
        return None
    
    print(f'✅ 找到图片: {image_path}')
    
    try:
        # 应用兼容性修复
        try:
            from torchvision_fix import apply_fix
            apply_fix()
            print('✅ 应用了torchvision兼容性修复')
        except ImportError:
            print('⚠️ 未找到torchvision_fix模块')
        except Exception as e:
            print(f'⚠️ 应用torchvision修复失败: {e}')
        
        # 导入必要的模块
        from hy3dshape.pipelines import Hunyuan3DDiTFlowMatchingPipeline
        print('✅ 成功导入Hunyuan3DDiTFlowMatchingPipeline')
        
        # 初始化管道
        print('正在初始化Hunyuan3D管道...')
        pipeline = Hunyuan3DDiTFlowMatchingPipeline.from_pretrained(
            'tencent/Hunyuan3D-2.1',
            device='cuda',
            dtype=torch.float16
        )
        print('✅ 管道初始化成功')
        
        # 加载图片
        image = Image.open(image_path).convert('RGB')
        print(f'✅ 图片加载成功，尺寸: {image.size}')
        
        # 生成3D模型
        print('开始生成3D模型...')
        result = pipeline(
            image=image,
            num_inference_steps=20,
            guidance_scale=7.5,
            seed=1234,
            octree_resolution=256
        )
        
        # 保存结果
        desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')
        output_path = os.path.join(desktop_path, 'yellow_kitten_3d_direct.glb')
        
        # 假设result包含mesh数据
        if hasattr(result, 'mesh') and result.mesh is not None:
            result.mesh.export(output_path)
            print(f'✅ 3D模型已保存到: {output_path}')
            return output_path
        else:
            print('❌ 生成结果中没有找到mesh数据')
            return None
            
    except ImportError as e:
        print(f'❌ 导入模块失败: {str(e)}')
        print('可能需要安装相关依赖或模型文件')
        return None
    except Exception as e:
        print(f'❌ 生成3D模型时出错: {str(e)}')
        return None

if __name__ == '__main__':
    direct_generate_3d()