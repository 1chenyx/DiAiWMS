"""
多租户系统 - 数据模型定义
定义租户配置、工具定义、技能定义等核心数据模型
"""
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime
from enum import Enum
import json


class LLMProviderType(str, Enum):
    """LLM提供者类型"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    AZURE = "azure"
    HUGGINGFACE = "huggingface"
    OLLAMA = "ollama"
    CUSTOM = "custom"


class LLMConfig(BaseModel):
    """LLM配置"""
    provider: