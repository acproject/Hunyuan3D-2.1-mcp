# 文本到3D场景完整工作流程指南

本指南介绍如何使用 Blender MCP 项目的完整工作流程管理系统，从文本描述创建完整的3D场景。

## 功能概述

工作流程管理器提供了一个统一的接口，整合了以下功能：
- 智能图像生成（AUTOMATIC1111 WebUI）
- 3D模型创建（Hyper3D、HunYuan3D）
- 场景组装和优化
- 参数自动优化
- 后处理和增强

## 工作流程阶段

### 1. 初始化阶段 (INITIALIZATION)
- 解析用户输入
- 选择生成策略
- 配置参数

### 2. 图像生成阶段 (IMAGE_GENERATION)
- 根据文本描述生成概念图像
- 应用优化参数
- 质量检查和增强

### 3. 3D模型创建阶段 (MODEL_GENERATION)
- 基于图像或文本生成3D模型
- 纹理和材质处理
- 几何优化

### 4. 场景组装阶段 (SCENE_ASSEMBLY)
- 将模型导入Blender场景
- 设置灯光和相机
- 应用环境贴图

### 5. 优化阶段 (OPTIMIZATION)
- 性能优化
- 质量提升
- 资源管理

### 6. 最终化阶段 (FINALIZATION)
- 最终渲染设置
- 导出配置
- 结果验证

## 生成方法

### IMAGE_FIRST（图像优先）
1. 首先生成高质量概念图像
2. 基于图像创建3D模型
3. 适用于需要精确视觉效果的场景

### MODEL_FIRST（模型优先）
1. 直接从文本生成3D模型
2. 后续生成纹理和材质
3. 适用于几何形状明确的对象

### HYBRID（混合模式）
1. 同时进行图像和模型生成
2. 交叉验证和优化
3. 平衡质量和效率

## 预设配置

### fast（快速模式）
- **描述**: 快速原型制作，优先速度
- **生成方法**: MODEL_FIRST
- **图像质量**: low
- **模型质量**: medium
- **场景复杂度**: simple
- **预计时间**: 5分钟

### balanced（平衡模式）
- **描述**: 质量和速度的平衡
- **生成方法**: HYBRID
- **图像质量**: medium
- **模型质量**: medium
- **场景复杂度**: medium
- **预计时间**: 15分钟

### quality（高质量模式）
- **描述**: 高质量输出，适合最终作品
- **生成方法**: IMAGE_FIRST
- **图像质量**: high
- **模型质量**: high
- **场景复杂度**: complex
- **预计时间**: 30分钟

### creative（创意模式）
- **描述**: 创意探索，多样化输出
- **生成方法**: HYBRID
- **图像质量**: high
- **模型质量**: medium
- **场景复杂度**: complex
- **预计时间**: 25分钟

## MCP工具函数

### execute_text_to_3d_workflow
执行完整的文本到3D场景创建工作流程。

```python
# 基本用法
result = execute_text_to_3d_workflow(
    description="一个现代风格的客厅，有沙发、茶几和落地灯",
    preset="balanced"
)

# 使用自定义配置
custom_config = {
    "generation_method": "image_first",
    "image_quality": "high",
    "enable_optimization": True
}
result = execute_text_to_3d_workflow(
    description="科幻风格的太空站内部",
    preset="quality",
    custom_config=json.dumps(custom_config)
)
```

### get_workflow_presets
获取所有可用的工作流程预设配置。

```python
presets = get_workflow_presets()
print(json.loads(presets)["presets"])
```

### create_custom_workflow
创建自定义工作流程配置。

```python
custom_workflow = create_custom_workflow(
    name="my_custom_workflow",
    description="专用于建筑可视化的工作流程",
    generation_method="image_first",
    image_quality="ultra",
    model_quality="high",
    scene_complexity="complex",
    enable_optimization=True,
    enable_post_processing=True
)
```

### get_workflow_status
获取工作流程执行状态和系统集成信息。

```python
status = get_workflow_status()
print(json.loads(status)["status"])
```

## 使用示例

### 示例1：创建简单场景
```python
# 快速创建一个简单的室内场景
result = execute_text_to_3d_workflow(
    description="一个温馨的卧室，有床、衣柜和窗户",
    preset="fast"
)

if json.loads(result)["success"]:
    print("场景创建成功！")
else:
    print(f"创建失败: {json.loads(result)['error']}")
```

### 示例2：高质量艺术作品
```python
# 创建高质量的艺术场景
result = execute_text_to_3d_workflow(
    description="梦幻森林中的精灵小屋，周围有发光的蘑菇和萤火虫",
    preset="quality"
)

workflow_result = json.loads(result)
if workflow_result["success"]:
    print(f"使用预设: {workflow_result['preset_used']}")
    print(f"工作流程结果: {workflow_result['workflow_result']}")
```

### 示例3：自定义配置
```python
# 使用自定义配置创建建筑场景
custom_config = {
    "generation_method": "image_first",
    "image_quality": "ultra",
    "model_quality": "high",
    "scene_complexity": "complex",
    "enable_optimization": True,
    "enable_post_processing": True,
    "image_generation_params": {
        "steps": 50,
        "cfg_scale": 8.0,
        "enable_hr": True
    },
    "model_generation_params": {
        "face_count": 60000,
        "texture_resolution": "2k"
    }
}

result = execute_text_to_3d_workflow(
    description="现代摩天大楼的大堂，有大理石地面和玻璃幕墙",
    custom_config=json.dumps(custom_config)
)
```

## 最佳实践

### 1. 描述编写技巧
- **具体明确**: 提供详细的视觉描述
- **风格指定**: 明确艺术风格（现代、古典、科幻等）
- **材质描述**: 包含材质和纹理信息
- **光照环境**: 描述光照条件和氛围

**好的描述示例**:
```
"一个现代风格的开放式厨房，白色大理石台面，不锈钢电器，
暖色调的木质橱柜，大窗户提供自然光照，简约而温馨的氛围"
```

### 2. 预设选择指南
- **原型阶段**: 使用 `fast` 预设快速验证概念
- **开发阶段**: 使用 `balanced` 预设平衡质量和效率
- **最终作品**: 使用 `quality` 预设获得最佳效果
- **创意探索**: 使用 `creative` 预设尝试不同可能性

### 3. 性能优化建议
- 根据硬件配置选择合适的质量设置
- 复杂场景分阶段创建
- 利用批量生成功能提高效率
- 定期清理临时文件

### 4. 故障排除

#### 常见问题
1. **工作流程管理器不可用**
   - 检查 `workflow_manager.py` 是否正确安装
   - 验证依赖项是否完整

2. **图像生成失败**
   - 确认 AUTOMATIC1111 WebUI 正在运行
   - 检查 API 连接设置
   - 验证模型是否加载

3. **3D模型生成失败**
   - 检查 Hyper3D/HunYuan3D 服务状态
   - 验证输入图像质量
   - 确认网络连接稳定

4. **场景组装问题**
   - 确认 Blender 连接正常
   - 检查模型文件完整性
   - 验证场景复杂度设置

## 高级功能

### 1. 批量处理
```python
# 批量创建多个场景变体
descriptions = [
    "现代客厅 - 简约风格",
    "现代客厅 - 豪华风格",
    "现代客厅 - 工业风格"
]

for desc in descriptions:
    result = execute_text_to_3d_workflow(
        description=desc,
        preset="balanced"
    )
    # 处理结果...
```

### 2. 参数优化集成
```python
# 结合参数优化功能
optimized_params = quick_sd_optimize(
    prompt="现代办公室内部设计",
    goal="quality",
    hardware="high"
)

custom_config = {
    "image_generation_params": json.loads(optimized_params)
}

result = execute_text_to_3d_workflow(
    description="现代办公室，开放式布局，自然光照",
    custom_config=json.dumps(custom_config)
)
```

### 3. 工作流程监控
```python
# 监控工作流程状态
status = get_workflow_status()
status_data = json.loads(status)

if status_data["success"]:
    integration_status = status_data["status"]["integration_status"]
    print(f"WebUI 可用: {integration_status['webui_available']}")
    print(f"优化工具可用: {integration_status['optimization_available']}")
    print(f"PolyHaven 可用: {integration_status['polyhaven_available']}")
```

## 文件结构

```
blender-mcp/
├── src/blender_mcp/
│   ├── workflow_manager.py          # 工作流程管理器
│   ├── sd_optimization_presets.py   # SD参数预设
│   ├── sd_parameter_optimizer.py    # 参数优化器
│   ├── enhanced_webui_tools.py      # 增强WebUI工具
│   └── server.py                    # MCP服务器
├── WORKFLOW_GUIDE.md                # 本指南
├── WEBUI_INTEGRATION_GUIDE.md       # WebUI集成指南
└── README.md                        # 项目说明
```

## 总结

工作流程管理系统为文本到3D场景创建提供了完整的解决方案，通过智能的参数优化和多阶段处理，能够高效地创建高质量的3D内容。合理使用预设配置和自定义参数，可以满足从快速原型到精品制作的各种需求。

通过本指南的学习，您应该能够：
- 理解工作流程的各个阶段
- 选择合适的生成方法和预设
- 编写有效的场景描述
- 使用MCP工具函数执行工作流程
- 处理常见问题和优化性能

开始您的3D创作之旅吧！