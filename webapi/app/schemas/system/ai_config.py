from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class AIProviderInfo(BaseModel):
    """
    AI提供商信息
    """
    code: str = Field(..., description="提供商代码")
    name: str = Field(..., description="提供商名称")
    description: str = Field(..., description="提供商描述")


class AIModelInfo(BaseModel):
    """
    AI模型信息
    """
    code: str = Field(..., description="模型代码")
    name: str = Field(..., description="模型名称")
    type: str = Field(..., description="模型类型")
    max_tokens: int = Field(..., description="最大token数")
    description: str = Field(..., description="模型描述")


class AIProviderWithModels(BaseModel):
    """
    AI提供商及其模型信息
    """
    code: str = Field(..., description="提供商代码")
    name: str = Field(..., description="提供商名称")
    description: str = Field(..., description="提供商描述")
    models: list[AIModelInfo] = Field(..., description="模型列表")


class TenantAIConfigViewModel(BaseModel):
    """
    租户AI配置视图模型
    """
    id: int = Field(default=0, description="主键ID")
    provider_code: str = Field(default="", description="提供商代码")
    provider_name: str = Field(default="", description="提供商名称")
    model_code: str = Field(default="", description="模型代码")
    model_name: str = Field(default="", description="模型名称")
    api_key: str = Field(default="", description="API密钥")
    api_endpoint: Optional[str] = Field(default=None, description="API端点URL")
    is_default: bool = Field(default=False, description="是否为默认配置")
    tenant_id: str = Field(default="", description="租户ID")
    creator: Optional[str] = Field(default=None, description="创建人")
    create_time: int = Field(default=0, description="创建时间")
    last_update_time: int = Field(default=0, description="最后更新时间")
    is_valid: bool = Field(default=True, description="是否有效")


class TenantAIConfigCreateViewModel(BaseModel):
    """
    租户AI配置创建视图模型
    """
    provider_code: str = Field(..., description="提供商代码")
    model_code: str = Field(..., description="模型代码")
    api_key: str = Field(..., description="API密钥")
    api_endpoint: Optional[str] = Field(default=None, description="API端点URL")
    is_default: bool = Field(default=False, description="是否为默认配置")


class TenantAIConfigUpdateViewModel(BaseModel):
    """
    租户AI配置更新视图模型
    """
    api_key: Optional[str] = Field(None, description="API密钥")
    api_endpoint: Optional[str] = Field(None, description="API端点URL")
    is_default: Optional[bool] = Field(None, description="是否为默认配置")
