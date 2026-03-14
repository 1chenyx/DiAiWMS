"""
LangChain Agent Demo - 配置管理模块
提供灵活的YAML配置加载和验证功能
"""
import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field, validator
from enum import Enum


class LLMProviderType(str, Enum):
    """LLM提供者类型枚举"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    AZURE = "azure"
    HUGGINGFACE = "huggingface"
    OLLAMA = "ollama"


class MemoryBackendType(str, Enum):
    """记忆存储后端类型枚举"""
    IN_MEMORY = "in_memory"
    REDIS = "redis"
    SQLITE = "sqlite"
    POSTGRESQL = "postgresql"


class AgentType(str, Enum):
    """Agent类型枚举"""
    REACT = "react"
    CONVERSATIONAL = "conversational"
    STRUCTURED_CHAT = "structured_chat"
    PLAN_AND_EXECUTE = "plan_and_execute"


class LLMConfig(BaseModel):
    """LLM配置模型"""
    provider: LLMProviderType = Field(default=LLMProviderType.OPENAI, description="LLM提供者类型")
    model_name: str = Field(default="gpt-3.5-turbo", description="模型名称")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="温度参数")
    max_tokens: int = Field(default=2000, gt=0, description="最大token数")
    api_key: Optional[str] = Field(default=None, description="API密钥")
    api_base: Optional[str] = Field(default=None, description="API基础URL")
    timeout: int = Field(default=60, gt=0, description="请求超时时间(秒)")
    max_retries: int = Field(default=3, ge=0, description="最大重试次数")
    fallback_providers: List[LLMProviderType] = Field(default_factory=list, description="备用提供者列表")
    
    @validator('temperature')
    def validate_temperature(cls, v):
        if not 0.0 <= v <= 2.0:
            raise ValueError('温度参数必须在0.0到2.0之间')
        return v


class MemoryConfig(BaseModel):
    """记忆配置模型"""
    backend: MemoryBackendType = Field(default=MemoryBackendType.IN_MEMORY, description="记忆存储后端")
    max_history: int = Field(default=10, gt=0, description="最大历史记录数")
    enable_summarization: bool = Field(default=False, description="是否启用对话摘要")
    summarization_threshold: int = Field(default=5, gt=0, description="摘要触发阈值")
    
    # Redis特定配置
    redis_host: Optional[str] = Field(default="localhost", description="Redis主机地址")
    redis_port: Optional[int] = Field(default=6379, gt=0, description="Redis端口")
    redis_db: Optional[int] = Field(default=0, ge=0, description="Redis数据库编号")
    redis_password: Optional[str] = Field(default=None, description="Redis密码")
    
    # SQLite特定配置
    sqlite_path: Optional[str] = Field(default=":memory:", description="SQLite数据库路径")
    
    # PostgreSQL特定配置
    postgres_host: Optional[str] = Field(default="localhost", description="PostgreSQL主机地址")
    postgres_port: Optional[int] = Field(default=5432, gt=0, description="PostgreSQL端口")
    postgres_database: Optional[str] = Field(default="agent_memory", description="PostgreSQL数据库名")
    postgres_user: Optional[str] = Field(default=None, description="PostgreSQL用户名")
    postgres_password: Optional[str] = Field(default=None, description="PostgreSQL密码")


class ToolConfig(BaseModel):
    """工具配置模型"""
    name: str = Field(..., description="工具名称")
    enabled: bool = Field(default=True, description="是否启用")
    config: Dict[str, Any] = Field(default_factory=dict, description="工具特定配置")


class SkillConfig(BaseModel):
    """技能配置模型"""
    name: str = Field(..., description="技能名称")
    enabled: bool = Field(default=True, description="是否启用")
    priority: int = Field(default=0, description="优先级")
    config: Dict[str, Any] = Field(default_factory=dict, description="技能特定配置")


class AgentConfig(BaseModel):
    """Agent配置模型"""
    name: str = Field(default="LangChain Agent", description="Agent名称")
    type: AgentType = Field(default=AgentType.REACT, description="Agent类型")
    verbose: bool = Field(default=True, description="是否输出详细日志")
    max_iterations: int = Field(default=10, gt=0, description="最大迭代次数")
    early_stopping_method: str = Field(default="generate", description="早期停止方法")
    handle_parsing_errors: bool = Field(default=True, description="是否处理解析错误")
    return_intermediate_steps: bool = Field(default=False, description="是否返回中间步骤")


class SystemPromptConfig(BaseModel):
    """系统提示词配置模型"""
    persona: str = Field(default="你是一个有用的AI助手", description="角色设定")
    rules: List[str] = Field(default_factory=list, description="规则列表")
    constraints: List[str] = Field(default_factory=list, description="约束列表")
    capabilities: List[str] = Field(default_factory=list, description="能力列表")
    custom_instructions: str = Field(default="", description="自定义指令")


class AgentSystemConfig(BaseModel):
    """Agent系统总配置模型"""
    llm: LLMConfig = Field(default_factory=LLMConfig, description="LLM配置")
    memory: MemoryConfig = Field(default_factory=MemoryConfig, description="记忆配置")
    agent: AgentConfig = Field(default_factory=AgentConfig, description="Agent配置")
    system_prompt: SystemPromptConfig = Field(default_factory=SystemPromptConfig, description="系统提示词配置")
    tools: List[ToolConfig] = Field(default_factory=list, description="工具配置列表")
    skills: List[SkillConfig] = Field(default_factory=list, description="技能配置列表")
    
    @classmethod
    def from_yaml(cls, yaml_path: str) -> 'AgentSystemConfig':
        """从YAML文件加载配置"""
        path = Path(yaml_path)
        if not path.exists():
            raise FileNotFoundError(f"配置文件不存在: {yaml_path}")
        
        with open(path, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
        
        return cls(**config_data)
    
    def to_yaml(self, yaml_path: str) -> None:
        """保存配置到YAML文件"""
        path = Path(yaml_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            yaml.dump(
                self.dict(),
                f,
                default_flow_style=False,
                allow_unicode=True,
                sort_keys=False
            )
    
    def get_enabled_tools(self) -> List[str]:
        """获取已启用的工具名称列表"""
        return [tool.name for tool in self.tools if tool.enabled]
    
    def get_enabled_skills(self) -> List[str]:
        """获取已启用的技能名称列表"""
        return [skill.name for skill in self.skills if skill.enabled]
    
    def get_tool_config(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """获取指定工具的配置"""
        for tool in self.tools:
            if tool.name == tool_name:
                return tool.config
        return None
    
    def get_skill_config(self, skill_name: str) -> Optional[Dict[str, Any]]:
        """获取指定技能的配置"""
        for skill in self.skills:
            if skill.name == skill_name:
                return skill.config
        return None


class ConfigManager:
    """配置管理器 - 提供配置加载、验证和环境变量替换功能"""
    
    def __init__(self, config_dir: str = "config"):
        """
        初始化配置管理器
        
        Args:
            config_dir: 配置文件目录路径
        """
        self.config_dir = Path(config_dir)
        self._config_cache: Dict[str, AgentSystemConfig] = {}
    
    def load_config(self, config_name: str = "default", environment: str = "dev") -> AgentSystemConfig:
        """
        加载配置文件
        
        Args:
            config_name: 配置文件名称（不含扩展名）
            environment: 环境名称（dev, staging, production）
        
        Returns:
            AgentSystemConfig: 配置对象
        """
        cache_key = f"{config_name}_{environment}"
        
        if cache_key in self._config_cache:
            return self._config_cache[cache_key]
        
        # 构建配置文件路径，优先级：环境特定配置 > 默认配置
        env_config_path = self.config_dir / f"{config_name}_{environment}.yaml"
        default_config_path = self.config_dir / f"{config_name}.yaml"
        
        if env_config_path.exists():
            config_path = env_config_path
        elif default_config_path.exists():
            config_path = default_config_path
        else:
            raise FileNotFoundError(
                f"配置文件不存在: {env_config_path} 或 {default_config_path}"
            )
        
        # 加载并解析配置
        config = AgentSystemConfig.from_yaml(str(config_path))
        
        # 替换环境变量
        self._replace_env_variables(config)
        
        # 缓存配置
        self._config_cache[cache_key] = config
        
        return config
    
    def _replace_env_variables(self, config: AgentSystemConfig) -> None:
        """
        替换配置中的环境变量占位符
        
        Args:
            config: 配置对象
        """
        # 替换LLM配置中的环境变量
        if config.llm.api_key and config.llm.api_key.startswith("${"):
            env_var = config.llm.api_key[2:-1]
            config.llm.api_key = os.getenv(env_var)
        
        if config.llm.api_base and config.llm.api_base.startswith("${"):
            env_var = config.llm.api_base[2:-1]
            config.llm.api_base = os.getenv(env_var)
        
        # 替换记忆配置中的环境变量
        if config.memory.redis_password and config.memory.redis_password.startswith("${"):
            env_var = config.memory.redis_password[2:-1]
            config.memory.redis_password = os.getenv(env_var)
        
        if config.memory.postgres_password and config.memory.postgres_password.startswith("${"):
            env_var = config.memory.postgres_password[2:-1]
            config.memory.postgres_password = os.getenv(env_var)
    
    def reload_config(self, config_name: str = "default", environment: str = "dev") -> AgentSystemConfig:
        """
        重新加载配置文件
        
        Args:
            config_name: 配置文件名称
            environment: 环境名称
        
        Returns:
            AgentSystemConfig: 配置对象
        """
        cache_key = f"{config_name}_{environment}"
        if cache_key in self._config_cache:
            del self._config_cache[cache_key]
        
        return self.load_config(config_name, environment)
    
    def save_config(self, config: AgentSystemConfig, config_name: str = "default") -> None:
        """
        保存配置到文件
        
        Args:
            config: 配置对象
            config_name: 配置文件名称
        """
        config_path = self.config_dir / f"{config_name}.yaml"
        config.to_yaml(str(config_path))
