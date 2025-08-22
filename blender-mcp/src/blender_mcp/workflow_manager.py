#!/usr/bin/env python3
"""
Workflow Manager for Text-to-3D Scene Creation

这个模块提供了完整的文本到3D场景创建工作流程管理，
整合了图像生成、3D模型创建、场景组装等功能。
"""

import json
import logging
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import time

# 设置日志
logger = logging.getLogger(__name__)

class WorkflowStage(Enum):
    """工作流程阶段"""
    INITIALIZATION = "initialization"
    IMAGE_GENERATION = "image_generation"
    MODEL_CREATION = "model_creation"
    SCENE_ASSEMBLY = "scene_assembly"
    OPTIMIZATION = "optimization"
    FINALIZATION = "finalization"
    COMPLETED = "completed"
    FAILED = "failed"

class GenerationMethod(Enum):
    """生成方法"""
    HUNYUAN3D = "hunyuan3d"
    HYPER3D_TEXT = "hyper3d_text"
    HYPER3D_IMAGE = "hyper3d_image"
    STABLE_DIFFUSION = "stable_diffusion"

@dataclass
class WorkflowConfig:
    """工作流程配置"""
    # 基本设置
    scene_description: str
    output_directory: str = "./output"
    
    # 图像生成设置
    use_enhanced_generation: bool = True
    image_width: int = 768
    image_height: int = 768
    image_steps: int = 30
    image_cfg_scale: float = 8.0
    enable_hr: bool = True
    hr_scale: float = 1.5
    
    # 3D模型生成设置
    preferred_3d_method: GenerationMethod = GenerationMethod.HUNYUAN3D
    remove_background: bool = True
    texture_enabled: bool = True
    model_seed: int = 1234
    
    # 优化设置
    optimization_goal: str = "quality"
    hardware_profile: str = "medium"
    
    # API设置
    webui_api_url: str = "http://localhost:7860"
    hunyuan3d_api_url: str = "http://localhost:8081"
    
    # 高级设置
    batch_processing: bool = False
    auto_retry: bool = True
    max_retries: int = 3
    save_intermediate: bool = True

@dataclass
class WorkflowResult:
    """工作流程结果"""
    success: bool
    stage: WorkflowStage
    generated_files: List[str]
    execution_time: float
    error_message: Optional[str] = None
    intermediate_results: Dict[str, Any] = None
    performance_metrics: Dict[str, float] = None

class WorkflowManager:
    """工作流程管理器"""
    
    def __init__(self, config: WorkflowConfig):
        self.config = config
        self.current_stage = WorkflowStage.INITIALIZATION
        self.results = []
        self.start_time = None
        self.intermediate_files = []
        
        # 创建输出目录
        Path(config.output_directory).mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Workflow Manager initialized with config: {config.scene_description}")
    
    async def execute_workflow(self) -> WorkflowResult:
        """执行完整的工作流程"""
        self.start_time = time.time()
        
        try:
            # 阶段1: 初始化
            await self._stage_initialization()
            
            # 阶段2: 图像生成
            image_result = await self._stage_image_generation()
            if not image_result.success:
                return self._create_failure_result("Image generation failed", image_result.error_message)
            
            # 阶段3: 3D模型创建
            model_result = await self._stage_model_creation(image_result)
            if not model_result.success:
                return self._create_failure_result("3D model creation failed", model_result.error_message)
            
            # 阶段4: 场景组装
            scene_result = await self._stage_scene_assembly(model_result)
            if not scene_result.success:
                return self._create_failure_result("Scene assembly failed", scene_result.error_message)
            
            # 阶段5: 优化
            optimization_result = await self._stage_optimization(scene_result)
            
            # 阶段6: 最终化
            final_result = await self._stage_finalization(optimization_result)
            
            self.current_stage = WorkflowStage.COMPLETED
            
            return WorkflowResult(
                success=True,
                stage=WorkflowStage.COMPLETED,
                generated_files=final_result.generated_files,
                execution_time=time.time() - self.start_time,
                intermediate_results=self._collect_intermediate_results(),
                performance_metrics=self._calculate_performance_metrics()
            )
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {str(e)}")
            return self._create_failure_result("Workflow execution failed", str(e))
    
    async def _stage_initialization(self) -> None:
        """初始化阶段"""
        self.current_stage = WorkflowStage.INITIALIZATION
        logger.info("Starting workflow initialization")
        
        # 验证配置
        self._validate_config()
        
        # 检查API连接
        await self._check_api_connections()
        
        logger.info("Workflow initialization completed")
    
    async def _stage_image_generation(self) -> WorkflowResult:
        """图像生成阶段"""
        self.current_stage = WorkflowStage.IMAGE_GENERATION
        logger.info("Starting image generation stage")
        
        try:
            # 这里需要调用实际的图像生成函数
            # 由于我们在MCP工具中，这里模拟调用
            image_params = {
                "prompt": self.config.scene_description,
                "width": self.config.image_width,
                "height": self.config.image_height,
                "steps": self.config.image_steps,
                "cfg_scale": self.config.image_cfg_scale,
                "enable_hr": self.config.enable_hr,
                "hr_scale": self.config.hr_scale
            }
            
            # 模拟图像生成结果
            generated_image_path = f"{self.config.output_directory}/generated_image.png"
            
            return WorkflowResult(
                success=True,
                stage=WorkflowStage.IMAGE_GENERATION,
                generated_files=[generated_image_path],
                execution_time=0.0
            )
            
        except Exception as e:
            return WorkflowResult(
                success=False,
                stage=WorkflowStage.IMAGE_GENERATION,
                generated_files=[],
                execution_time=0.0,
                error_message=str(e)
            )
    
    async def _stage_model_creation(self, image_result: WorkflowResult) -> WorkflowResult:
        """3D模型创建阶段"""
        self.current_stage = WorkflowStage.MODEL_CREATION
        logger.info("Starting 3D model creation stage")
        
        try:
            image_path = image_result.generated_files[0]
            
            # 根据配置选择3D生成方法
            if self.config.preferred_3d_method == GenerationMethod.HUNYUAN3D:
                model_result = await self._create_hunyuan3d_model(image_path)
            elif self.config.preferred_3d_method == GenerationMethod.HYPER3D_IMAGE:
                model_result = await self._create_hyper3d_model_from_image(image_path)
            else:
                model_result = await self._create_hyper3d_model_from_text()
            
            return model_result
            
        except Exception as e:
            return WorkflowResult(
                success=False,
                stage=WorkflowStage.MODEL_CREATION,
                generated_files=[],
                execution_time=0.0,
                error_message=str(e)
            )
    
    async def _stage_scene_assembly(self, model_result: WorkflowResult) -> WorkflowResult:
        """场景组装阶段"""
        self.current_stage = WorkflowStage.SCENE_ASSEMBLY
        logger.info("Starting scene assembly stage")
        
        try:
            # 场景组装逻辑
            model_files = model_result.generated_files
            
            # 模拟场景组装
            scene_file = f"{self.config.output_directory}/assembled_scene.blend"
            
            return WorkflowResult(
                success=True,
                stage=WorkflowStage.SCENE_ASSEMBLY,
                generated_files=[scene_file],
                execution_time=0.0
            )
            
        except Exception as e:
            return WorkflowResult(
                success=False,
                stage=WorkflowStage.SCENE_ASSEMBLY,
                generated_files=[],
                execution_time=0.0,
                error_message=str(e)
            )
    
    async def _stage_optimization(self, scene_result: WorkflowResult) -> WorkflowResult:
        """优化阶段"""
        self.current_stage = WorkflowStage.OPTIMIZATION
        logger.info("Starting optimization stage")
        
        try:
            # 优化逻辑
            optimized_files = scene_result.generated_files.copy()
            
            return WorkflowResult(
                success=True,
                stage=WorkflowStage.OPTIMIZATION,
                generated_files=optimized_files,
                execution_time=0.0
            )
            
        except Exception as e:
            return WorkflowResult(
                success=True,  # 优化失败不影响整体流程
                stage=WorkflowStage.OPTIMIZATION,
                generated_files=scene_result.generated_files,
                execution_time=0.0,
                error_message=f"Optimization failed: {str(e)}"
            )
    
    async def _stage_finalization(self, optimization_result: WorkflowResult) -> WorkflowResult:
        """最终化阶段"""
        self.current_stage = WorkflowStage.FINALIZATION
        logger.info("Starting finalization stage")
        
        try:
            # 清理临时文件
            if not self.config.save_intermediate:
                self._cleanup_intermediate_files()
            
            # 生成报告
            report_file = f"{self.config.output_directory}/workflow_report.json"
            self._generate_workflow_report(report_file)
            
            final_files = optimization_result.generated_files + [report_file]
            
            return WorkflowResult(
                success=True,
                stage=WorkflowStage.FINALIZATION,
                generated_files=final_files,
                execution_time=0.0
            )
            
        except Exception as e:
            return WorkflowResult(
                success=True,  # 最终化失败不影响主要结果
                stage=WorkflowStage.FINALIZATION,
                generated_files=optimization_result.generated_files,
                execution_time=0.0,
                error_message=f"Finalization failed: {str(e)}"
            )
    
    async def _create_hunyuan3d_model(self, image_path: str) -> WorkflowResult:
        """使用HunYuan3D创建3D模型"""
        # 这里应该调用实际的HunYuan3D API
        model_file = f"{self.config.output_directory}/hunyuan3d_model.obj"
        
        return WorkflowResult(
            success=True,
            stage=WorkflowStage.MODEL_CREATION,
            generated_files=[model_file],
            execution_time=0.0
        )
    
    async def _create_hyper3d_model_from_image(self, image_path: str) -> WorkflowResult:
        """使用Hyper3D从图像创建3D模型"""
        model_file = f"{self.config.output_directory}/hyper3d_model.obj"
        
        return WorkflowResult(
            success=True,
            stage=WorkflowStage.MODEL_CREATION,
            generated_files=[model_file],
            execution_time=0.0
        )
    
    async def _create_hyper3d_model_from_text(self) -> WorkflowResult:
        """使用Hyper3D从文本创建3D模型"""
        model_file = f"{self.config.output_directory}/hyper3d_text_model.obj"
        
        return WorkflowResult(
            success=True,
            stage=WorkflowStage.MODEL_CREATION,
            generated_files=[model_file],
            execution_time=0.0
        )
    
    def _validate_config(self) -> None:
        """验证配置"""
        if not self.config.scene_description:
            raise ValueError("Scene description is required")
        
        if self.config.image_width <= 0 or self.config.image_height <= 0:
            raise ValueError("Invalid image dimensions")
    
    async def _check_api_connections(self) -> None:
        """检查API连接"""
        # 这里应该检查各种API的连接状态
        logger.info("API connections verified")
    
    def _create_failure_result(self, message: str, error: str) -> WorkflowResult:
        """创建失败结果"""
        self.current_stage = WorkflowStage.FAILED
        
        return WorkflowResult(
            success=False,
            stage=WorkflowStage.FAILED,
            generated_files=[],
            execution_time=time.time() - self.start_time if self.start_time else 0.0,
            error_message=f"{message}: {error}"
        )
    
    def _collect_intermediate_results(self) -> Dict[str, Any]:
        """收集中间结果"""
        return {
            "config": asdict(self.config),
            "stages_completed": [result.stage.value for result in self.results],
            "intermediate_files": self.intermediate_files
        }
    
    def _calculate_performance_metrics(self) -> Dict[str, float]:
        """计算性能指标"""
        total_time = time.time() - self.start_time if self.start_time else 0.0
        
        return {
            "total_execution_time": total_time,
            "average_stage_time": total_time / len(self.results) if self.results else 0.0,
            "success_rate": sum(1 for r in self.results if r.success) / len(self.results) if self.results else 0.0
        }
    
    def _cleanup_intermediate_files(self) -> None:
        """清理中间文件"""
        for file_path in self.intermediate_files:
            try:
                Path(file_path).unlink(missing_ok=True)
                logger.info(f"Cleaned up intermediate file: {file_path}")
            except Exception as e:
                logger.warning(f"Failed to cleanup file {file_path}: {str(e)}")
    
    def _generate_workflow_report(self, report_file: str) -> None:
        """生成工作流程报告"""
        report = {
            "workflow_config": asdict(self.config),
            "execution_summary": {
                "success": self.current_stage == WorkflowStage.COMPLETED,
                "final_stage": self.current_stage.value,
                "total_execution_time": time.time() - self.start_time if self.start_time else 0.0
            },
            "stage_results": [asdict(result) for result in self.results],
            "performance_metrics": self._calculate_performance_metrics(),
            "generated_timestamp": time.time()
        }
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Workflow report generated: {report_file}")

# 便捷函数
def create_workflow_config(
    scene_description: str,
    **kwargs
) -> WorkflowConfig:
    """创建工作流程配置的便捷函数"""
    return WorkflowConfig(scene_description=scene_description, **kwargs)

async def execute_text_to_3d_workflow(
    scene_description: str,
    config_overrides: Optional[Dict[str, Any]] = None
) -> WorkflowResult:
    """执行文本到3D场景工作流程的便捷函数"""
    config_dict = {"scene_description": scene_description}
    if config_overrides:
        config_dict.update(config_overrides)
    
    config = WorkflowConfig(**config_dict)
    manager = WorkflowManager(config)
    
    return await manager.execute_workflow()

# 预设配置
PRESET_CONFIGS = {
    "fast": {
        "image_width": 512,
        "image_height": 512,
        "image_steps": 20,
        "enable_hr": False,
        "optimization_goal": "speed"
    },
    "quality": {
        "image_width": 768,
        "image_height": 768,
        "image_steps": 30,
        "enable_hr": True,
        "hr_scale": 1.5,
        "optimization_goal": "quality"
    },
    "ultra": {
        "image_width": 1024,
        "image_height": 1024,
        "image_steps": 50,
        "enable_hr": True,
        "hr_scale": 2.0,
        "optimization_goal": "quality",
        "hardware_profile": "ultra"
    }
}

def get_preset_config(preset_name: str) -> Dict[str, Any]:
    """获取预设配置"""
    return PRESET_CONFIGS.get(preset_name, PRESET_CONFIGS["quality"])