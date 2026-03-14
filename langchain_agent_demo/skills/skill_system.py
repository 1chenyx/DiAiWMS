"""
LangChain Agent Demo - 技能系统
提供可配置的技能管理、技能执行和技能组合功能
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Callable
from pathlib import Path
import importlib.util
import inspect
from pydantic import BaseModel, Field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class SkillType(str, Enum):
    """技能类型枚举"""
    REASONING = "reasoning"  # 推理技能
    PLANNING = "planning"  # 规划技能
    ANALYSIS = "analysis"  # 分析技能
    CREATIVITY = "creativity"  # 创造性技能
    KNOWLEDGE = "knowledge"  # 知识技能
    COMMUNICATION = "communication"  # 交流技能
    CUSTOM = "custom"  # 自定义技能


class SkillMetadata(BaseModel):
    """技能元数据"""
    name: str = Field(..., description="技能名称")
    type: SkillType = Field(default=SkillType.CUSTOM, description="技能类型")
    version: str = Field(default="1.0.0", description="技能版本")
    description: str = Field(..., description="技能描述")
    author: str = Field(default="", description="技能作者")
    enabled: bool = Field(default=True, description="是否启用")
    priority: int = Field(default=0, description="优先级（数值越大优先级越高）")
    dependencies: List[str] = Field(default_factory=list, description="依赖的其他技能")
    config: Dict[str, Any] = Field(default_factory=dict, description="技能配置")
    tags: List[str] = Field(default_factory=list, description="技能标签")


class SkillResult(BaseModel):
    """技能执行结果"""
    success: bool = Field(..., description="是否成功")
    output: Any = Field(default=None, description="输出结果")
    error: Optional[str] = Field(default=None, description="错误信息")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")
    execution_time: float = Field(default=0.0, description="执行时间（秒）")


class BaseSkill(ABC):
    """技能基类 - 定义技能的统一接口"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        初始化技能
        
        Args:
            config: 技能配置
        """
        self.config = config or {}
        self.metadata = self._get_metadata()
    
    @abstractmethod
    def _get_metadata(self) -> SkillMetadata:
        """
        获取技能元数据
        
        Returns:
            SkillMetadata: 技能元数据
        """
        pass
    
    @abstractmethod
    async def execute(
        self,
        input_data: Any,
        context: Dict[str, Any] = None
    ) -> SkillResult:
        """
        执行技能
        
        Args:
            input_data: 输入数据
            context: 执行上下文
        
        Returns:
            SkillResult: 执行结果
        """
        pass
    
    def execute_sync(
        self,
        input_data: Any,
        context: Dict[str, Any] = None
    ) -> SkillResult:
        """
        同步执行技能
        
        Args:
            input_data: 输入数据
            context: 执行上下文
        
        Returns:
            SkillResult: 执行结果
        """
        import asyncio
        return asyncio.run(self.execute(input_data, context))
    
    def is_enabled(self) -> bool:
        """检查技能是否启用"""
        return self.metadata.enabled
    
    def enable(self) -> None:
        """启用技能"""
        self.metadata.enabled = True
    
    def disable(self) -> None:
        """禁用技能"""
        self.metadata.enabled = False
    
    def get_priority(self) -> int:
        """获取技能优先级"""
        return self.metadata.priority
    
    def get_dependencies(self) -> List[str]:
        """获取技能依赖"""
        return self.metadata.dependencies


class ReasoningSkill(BaseSkill):
    """推理技能 - 提供深度推理能力"""
    
    def _get_metadata(self) -> SkillMetadata:
        return SkillMetadata(
            name="reasoning",
            type=SkillType.REASONING,
            description="深度推理技能，支持链式思考",
            version="1.0.0",
            priority=10,
            config=self.config
        )
    
    async def execute(
        self,
        input_data: str,
        context: Dict[str, Any] = None
    ) -> SkillResult:
        """
        执行推理
        
        Args:
            input_data: 输入问题
            context: 执行上下文
        
        Returns:
            SkillResult: 推理结果
        """
        import time
        start_time = time.time()
        
        try:
            # 获取配置
            enable_chain_of_thought = self.config.get('enable_chain_of_thought', True)
            
            if enable_chain_of_thought:
                # 链式思考推理
                reasoning_steps = self._chain_of_thought(input_data)
                output = {
                    'reasoning': reasoning_steps,
                    'conclusion': reasoning_steps[-1] if reasoning_steps else ""
                }
            else:
                # 直接推理
                output = self._direct_reasoning(input_data)
            
            execution_time = time.time() - start_time
            
            return SkillResult(
                success=True,
                output=output,
                execution_time=execution_time,
                metadata={'method': 'chain_of_thought' if enable_chain_of_thought else 'direct'}
            )
        
        except Exception as e:
            execution_time = time.time() - start_time
            return SkillResult(
                success=False,
                error=str(e),
                execution_time=execution_time
            )
    
    def _chain_of_thought(self, question: str) -> List[str]:
        """
        链式思考推理
        
        Args:
            question: 问题
        
        Returns:
            List[str]: 推理步骤列表
        """
        # 这里是简化的链式思考实现
        # 在实际应用中，这里会调用LLM进行推理
        steps = [
            f"分析问题: {question}",
            "识别关键信息",
            "制定推理计划",
            "逐步推理",
            "得出结论"
        ]
        return steps
    
    def _direct_reasoning(self, question: str) -> str:
        """
        直接推理
        
        Args:
            question: 问题
        
        Returns:
            str: 推理结果
        """
        # 简化的直接推理实现
        return f"对问题 '{question}' 的推理结果"


class PlanningSkill(BaseSkill):
    """规划技能 - 提供任务规划能力"""
    
    def _get_metadata(self) -> SkillMetadata:
        return SkillMetadata(
            name="planning",
            type=SkillType.PLANNING,
            description="任务规划技能，将复杂任务分解为可执行的步骤",
            version="1.0.0",
            priority=8,
            config=self.config
        )
    
    async def execute(
        self,
        input_data: str,
        context: Dict[str, Any] = None
    ) -> SkillResult:
        """
        执行规划
        
        Args:
            input_data: 任务描述
            context: 执行上下文
        
        Returns:
            SkillResult: 规划结果
        """
        import time
        start_time = time.time()
        
        try:
            # 获取配置
            max_steps = self.config.get('max_steps', 5)
            
            # 分解任务
            plan = self._decompose_task(input_data, max_steps)
            
            execution_time = time.time() - start_time
            
            return SkillResult(
                success=True,
                output=plan,
                execution_time=execution_time,
                metadata={'total_steps': len(plan)}
            )
        
        except Exception as e:
            execution_time = time.time() - start_time
            return SkillResult(
                success=False,
                error=str(e),
                execution_time=execution_time
            )
    
    def _decompose_task(self, task: str, max_steps: int) -> List[Dict[str, Any]]:
        """
        分解任务为步骤
        
        Args:
            task: 任务描述
            max_steps: 最大步骤数
        
        Returns:
            List[Dict[str, Any]]: 步骤列表
        """
        # 简化的任务分解实现
        steps = [
            {
                'step': 1,
                'action': '分析任务',
                'description': f"理解任务 '{task}' 的目标和要求"
            },
            {
                'step': 2,
                'action': '收集信息',
                'description': '获取完成任务所需的信息和资源'
            },
            {
                'step': 3,
                'action': '制定方案',
                'description': '设计完成任务的具体方案'
            },
            {
                'step': 4,
                'action': '执行方案',
                'description': '按照方案执行具体操作'
            },
            {
                'step': 5,
                'action': '验证结果',
                'description': '检查任务完成情况'
            }
        ]
        
        return steps[:max_steps]


class AnalysisSkill(BaseSkill):
    """分析技能 - 提供数据分析能力"""
    
    def _get_metadata(self) -> SkillMetadata:
        return SkillMetadata(
            name="analysis",
            type=SkillType.ANALYSIS,
            description="数据分析技能，支持数据统计、可视化和洞察发现",
            version="1.0.0",
            priority=6,
            config=self.config
        )
    
    async def execute(
        self,
        input_data: Any,
        context: Dict[str, Any] = None
    ) -> SkillResult:
        """
        执行分析
        
        Args:
            input_data: 输入数据
            context: 执行上下文
        
        Returns:
            SkillResult: 分析结果
        """
        import time
        start_time = time.time()
        
        try:
            # 获取配置
            enable_visualization = self.config.get('enable_visualization', False)
            
            # 执行分析
            analysis_result = self._analyze_data(input_data)
            
            output = {
                'analysis': analysis_result,
                'visualization': None
            }
            
            if enable_visualization:
                output['visualization'] = self._create_visualization(input_data)
            
            execution_time = time.time() - start_time
            
            return SkillResult(
                success=True,
                output=output,
                execution_time=execution_time
            )
        
        except Exception as e:
            execution_time = time.time() - start_time
            return SkillResult(
                success=False,
                error=str(e),
                execution_time=execution_time
            )
    
    def _analyze_data(self, data: Any) -> Dict[str, Any]:
        """
        分析数据
        
        Args:
            data: 输入数据
        
        Returns:
            Dict[str, Any]: 分析结果
        """
        # 简化的数据分析实现
        return {
            'summary': '数据分析摘要',
            'insights': ['洞察1', '洞察2', '洞察3'],
            'statistics': {}
        }
    
    def _create_visualization(self, data: Any) -> Dict[str, Any]:
        """
        创建可视化
        
        Args:
            data: 输入数据
        
        Returns:
            Dict[str, Any]: 可视化配置
        """
        # 简化的可视化实现
        return {
            'type': 'chart',
            'config': {}
        }


class CreativitySkill(BaseSkill):
    """创造性技能 - 提供创造性思维能力"""
    
    def _get_metadata(self) -> SkillMetadata:
        return SkillMetadata(
            name="creativity",
            type=SkillType.CREATIVITY,
            description="创造性思维技能，支持创意生成和问题创新解决",
            version="1.0.0",
            priority=4,
            config=self.config
        )
    
    async def execute(
        self,
        input_data: str,
        context: Dict[str, Any] = None
    ) -> SkillResult:
        """
        执行创造性思维
        
        Args:
            input_data: 创意主题
            context: 执行上下文
        
        Returns:
            SkillResult: 创意结果
        """
        import time
        start_time = time.time()
        
        try:
            # 获取配置
            temperature_boost = self.config.get('temperature_boost', 0.2)
            
            # 生成创意
            ideas = self._generate_ideas(input_data, temperature_boost)
            
            execution_time = time.time() - start_time
            
            return SkillResult(
                success=True,
                output={
                    'ideas': ideas,
                    'temperature_boost': temperature_boost
                },
                execution_time=execution_time
            )
        
        except Exception as e:
            execution_time = time.time() - start_time
            return SkillResult(
                success=False,
                error=str(e),
                execution_time=execution_time
            )
    
    def _generate_ideas(self, topic: str, temperature: float) -> List[str]:
        """
        生成创意
        
        Args:
            topic: 创意主题
            temperature: 温度参数
        
        Returns:
            List[str]: 创意列表
        """
        # 简化的创意生成实现
        return [
            f"关于 '{topic}' 的创意1",
            f"关于 '{topic}' 的创意2",
            f"关于 '{topic}' 的创意3"
        ]


class SkillRegistry:
    """技能注册表 - 管理所有已注册的技能"""
    
    def __init__(self):
        """初始化技能注册表"""
        self._skills: Dict[str, BaseSkill] = {}
        self._skill_types: Dict[SkillType, List[str]] = {}
    
    def register(self, skill: BaseSkill) -> None:
        """
        注册技能
        
        Args:
            skill: 技能实例
        """
        name = skill.metadata.name
        self._skills[name] = skill
        
        # 按类型索引
        skill_type = skill.metadata.type
        if skill_type not in self._skill_types:
            self._skill_types[skill_type] = []
        self._skill_types[skill_type].append(name)
        
        logger.info(f"技能已注册: {name} v{skill.metadata.version}")
    
    def unregister(self, skill_name: str) -> bool:
        """
        注销技能
        
        Args:
            skill_name: 技能名称
        
        Returns:
            bool: 是否成功注销
        """
        if skill_name in self._skills:
            skill = self._skills[skill_name]
            skill_type = skill.metadata.type
            self._skill_types[skill_type].remove(skill_name)
            del self._skills[skill_name]
            logger.info(f"技能已注销: {skill_name}")
            return True
        return False
    
    def get_skill(self, skill_name: str) -> Optional[BaseSkill]:
        """
        获取技能
        
        Args:
            skill_name: 技能名称
        
        Returns:
            Optional[BaseSkill]: 技能实例
        """
        return self._skills.get(skill_name)
    
    def list_skills(
        self,
        skill_type: Optional[SkillType] = None,
        enabled_only: bool = True
    ) -> List[str]:
        """
        列出技能
        
        Args:
            skill_type: 技能类型（可选）
            enabled_only: 是否只列出已启用的技能
        
        Returns:
            List[str]: 技能名称列表
        """
        if skill_type:
            skill_names = self._skill_types.get(skill_type, [])
        else:
            skill_names = list(self._skills.keys())
        
        if enabled_only:
            return [
                name for name in skill_names
                if self._skills[name].is_enabled()
            ]
        
        return skill_names
    
    def get_skills_by_type(self, skill_type: SkillType) -> List[BaseSkill]:
        """
        按类型获取技能
        
        Args:
            skill_type: 技能类型
        
        Returns:
            List[BaseSkill]: 技能实例列表
        """
        skill_names = self._skill_types.get(skill_type, [])
        skills = []
        
        for name in skill_names:
            skill = self.get_skill(name)
            if skill and skill.is_enabled():
                skills.append(skill)
        
        return skills
    
    def get_all_enabled_skills(self) -> List[BaseSkill]:
        """
        获取所有已启用的技能
        
        Returns:
            List[BaseSkill]: 技能实例列表
        """
        return [
            skill for skill in self._skills.values()
            if skill.is_enabled()
        ]
    
    def enable_skill(self, skill_name: str) -> bool:
        """
        启用技能
        
        Args:
            skill_name: 技能名称
        
        Returns:
            bool: 是否成功启用
        """
        skill = self._skills.get(skill_name)
        if skill:
            skill.enable()
            logger.info(f"技能已启用: {skill_name}")
            return True
        return False
    
    def disable_skill(self, skill_name: str) -> bool:
        """
        禁用技能
        
        Args:
            skill_name: 技能名称
        
        Returns:
            bool: 是否成功禁用
        """
        skill = self._skills.get(skill_name)
        if skill:
            skill.disable()
            logger.info(f"技能已禁用: {skill_name}")
            return True
        return False
    
    def get_skills_sorted_by_priority(self) -> List[BaseSkill]:
        """
        按优先级排序获取技能
        
        Returns:
            List[BaseSkill]: 排序后的技能列表
        """
        enabled_skills = self.get_all_enabled_skills()
        return sorted(enabled_skills, key=lambda s: s.get_priority(), reverse=True)


class SkillManager:
    """技能管理器 - 提供技能管理的统一接口"""
    
    def __init__(self):
        """初始化技能管理器"""
        self.registry = SkillRegistry()
        self._initialize_default_skills()
    
    def _initialize_default_skills(self) -> None:
        """初始化默认技能"""
        default_skills = [
            ReasoningSkill(),
            PlanningSkill(),
            AnalysisSkill(),
            CreativitySkill()
        ]
        
        for skill in default_skills:
            self.registry.register(skill)
    
    def register_skill(self, skill: BaseSkill) -> None:
        """
        注册技能
        
        Args:
            skill: 技能实例
        """
        self.registry.register(skill)
    
    def get_skill(self, skill_name: str) -> Optional[BaseSkill]:
        """
        获取技能
        
        Args:
            skill_name: 技能名称
        
        Returns:
            Optional[BaseSkill]: 技能实例
        """
        return self.registry.get_skill(skill_name)
    
    async def execute_skill(
        self,
        skill_name: str,
        input_data: Any,
        context: Dict[str, Any] = None
    ) -> SkillResult:
        """
        执行技能
        
        Args:
            skill_name: 技能名称
            input_data: 输入数据
            context: 执行上下文
        
        Returns:
            SkillResult: 执行结果
        """
        skill = self.get_skill(skill_name)
        if not skill:
            return SkillResult(
                success=False,
                error=f"技能不存在: {skill_name}"
            )
        
        if not skill.is_enabled():
            return SkillResult(
                success=False,
                error=f"技能未启用: {skill_name}"
            )
        
        return await skill.execute(input_data, context)
    
    def execute_skill_sync(
        self,
        skill_name: str,
        input_data: Any,
        context: Dict[str, Any] = None
    ) -> SkillResult:
        """
        同步执行技能
        
        Args:
            skill_name: 技能名称
            input_data: 输入数据
            context: 执行上下文
        
        Returns:
            SkillResult: 执行结果
        """
        import asyncio
        return asyncio.run(self.execute_skill(skill_name, input_data, context))
    
    async def execute_skills_chain(
        self,
        skill_names: List[str],
        input_data: Any,
        context: Dict[str, Any] = None
    ) -> List[SkillResult]:
        """
        按顺序执行技能链
        
        Args:
            skill_names: 技能名称列表
            input_data: 输入数据
            context: 执行上下文
        
        Returns:
            List[SkillResult]: 执行结果列表
        """
        results = []
        current_input = input_data
        
        for skill_name in skill_names:
            result = await self.execute_skill(skill_name, current_input, context)
            results.append(result)
            
            if result.success:
                current_input = result.output
            else:
                break
        
        return results
    
    def list_skills(self, **kwargs) -> List[str]:
        """
        列出技能
        
        Args:
            **kwargs: 过滤参数
        
        Returns:
            List[str]: 技能名称列表
        """
        return self.registry.list_skills(**kwargs)
    
    def enable_skill(self, skill_name: str) -> bool:
        """
        启用技能
        
        Args:
            skill_name: 技能名称
        
        Returns:
            bool: 是否成功
        """
        return self.registry.enable_skill(skill_name)
    
    def disable_skill(self, skill_name: str) -> bool:
        """
        禁用技能
        
        Args:
            skill_name: 技能名称
        
        Returns:
            bool: 是否成功
        """
        return self.registry.disable_skill(skill_name)
