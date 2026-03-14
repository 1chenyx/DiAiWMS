from typing import Optional, List
from pydantic import BaseModel, Field


class AIProviderInfo(BaseModel):
    """AI服务商信息"""
    code: str = Field(default="", description="服务商代码")
    name: str = Field(default="", description="服务商名称")
    description: str = Field(default="", description="服务商描述")
    api_base: str = Field(default="", description="API基础URL")


class AIModelInfo(BaseModel):
    """AI模型信息"""
    code: str = Field(default="", description="模型代码")
    name: str = Field(default="", description="模型名称")
    type: str = Field(default="", description="模型类型")
    max_tokens: int = Field(default=0, description="最大token数")
    description: str = Field(default="", description="模型描述")


class AIProviderWithModels(BaseModel):
    """AI服务商及其模型信息"""
    code: str = Field(default="", description="服务商代码")
    name: str = Field(default="", description="服务商名称")
    description: str = Field(default="", description="服务商描述")
    api_base: str = Field(default="", description="API基础URL")
    models: List[AIModelInfo] = Field(default_factory=list, description="模型列表")


class TenantAIConfigViewModel(BaseModel):
    """租户AI配置视图模型"""
    id: int = Field(default=0, description="主键ID")
    tenant_id: str = Field(default="", description="租户ID")
    provider_code: str = Field(default="", description="服务商代码")
    provider_name: str = Field(default="", description="服务商名称")
    model_code: str = Field(default="", description="模型代码")
    model_name: str = Field(default="", description="模型名称")
    api_key: str = Field(default="", description="API密钥")
    api_endpoint: str = Field(default="", description="API端点")
    is_default: bool = Field(default=False, description="是否默认配置")
    temperature: str = Field(default="0.7", description="温度参数")
    max_tokens: int = Field(default=2000, description="最大token数")
    is_valid: bool = Field(default=True, description="是否有效")
    creator: str = Field(default="", description="创建人")
    create_time: int = Field(default=0, description="创建时间")
    last_update_time: int = Field(default=0, description="最后更新时间")


class TenantAIConfigCreateViewModel(BaseModel):
    """租户AI配置创建视图模型"""
    provider_code: str = Field(..., description="服务商代码")
    model_code: str = Field(..., description="模型代码")
    api_key: str = Field(..., description="API密钥")
    api_endpoint: str = Field(default="", description="API端点")
    is_default: bool = Field(default=False, description="是否默认配置")
    temperature: str = Field(default="0.7", description="温度参数")
    max_tokens: int = Field(default=2000, description="最大token数")


class TenantAIConfigUpdateViewModel(BaseModel):
    """租户AI配置更新视图模型"""
    id: int = Field(..., description="主键ID")
    api_key: Optional[str] = Field(None, description="API密钥")
    api_endpoint: Optional[str] = Field(None, description="API端点")
    is_default: Optional[bool] = Field(None, description="是否默认配置")
    temperature: Optional[str] = Field(None, description="温度参数")
    max_tokens: Optional[int] = Field(None, description="最大token数")


class AIToolInfo(BaseModel):
    """AI工具信息"""
    code: str = Field(default="", description="工具代码")
    name: str = Field(default="", description="工具名称")
    category: str = Field(default="", description="工具分类")
    description: str = Field(default="", description="工具描述")
    is_active: bool = Field(default=True, description="是否激活")
    is_system: bool = Field(default=True, description="是否系统工具")
    config_schema: dict = Field(default_factory=dict, description="配置模式")


class AIToolCategoryInfo(BaseModel):
    """AI工具分类信息"""
    code: str = Field(default="", description="分类代码")
    name: str = Field(default="", description="分类名称")
    description: str = Field(default="", description="分类描述")
    icon: str = Field(default="", description="图标")
    color: str = Field(default="", description="颜色")


class TenantAIToolViewModel(BaseModel):
    """租户AI工具配置视图模型"""
    id: int = Field(default=0, description="主键ID")
    tenant_id: str = Field(default="", description="租户ID")
    tool_code: str = Field(default="", description="工具代码")
    tool_name: str = Field(default="", description="工具名称")
    tool_category: str = Field(default="", description="工具分类")
    is_active: bool = Field(default=True, description="是否激活")
    config: str = Field(default="{}", description="工具配置(JSON)")
    description: str = Field(default="", description="工具描述")
    is_valid: bool = Field(default=True, description="是否有效")
    creator: str = Field(default="", description="创建人")
    create_time: int = Field(default=0, description="创建时间")
    last_update_time: int = Field(default=0, description="最后更新时间")


class TenantAIToolCreateViewModel(BaseModel):
    """租户AI工具配置创建视图模型"""
    tool_code: str = Field(..., description="工具代码")
    tool_name: str = Field(..., description="工具名称")
    tool_category: str = Field(..., description="工具分类")
    is_active: bool = Field(default=True, description="是否激活")
    config: str = Field(default="{}", description="工具配置(JSON)")
    description: str = Field(default="", description="工具描述")


class TenantAIToolUpdateViewModel(BaseModel):
    """租户AI工具配置更新视图模型"""
    id: int = Field(..., description="主键ID")
    is_active: Optional[bool] = Field(None, description="是否激活")
    config: Optional[str] = Field(None, description="工具配置(JSON)")
    description: Optional[str] = Field(None, description="工具描述")


class TenantAISkillViewModel(BaseModel):
    """租户AI技能配置视图模型"""
    id: int = Field(default=0, description="主键ID")
    tenant_id: str = Field(default="", description="租户ID")
    skill_name: str = Field(default="", description="技能名称")
    skill_type: str = Field(default="", description="技能类型")
    description: str = Field(default="", description="技能描述")
    config: str = Field(default="{}", description="技能配置(JSON)")
    is_active: bool = Field(default=True, description="是否激活")
    is_valid: bool = Field(default=True, description="是否有效")
    creator: str = Field(default="", description="创建人")
    create_time: int = Field(default=0, description="创建时间")
    last_update_time: int = Field(default=0, description="最后更新时间")


class TenantAISkillCreateViewModel(BaseModel):
    """租户AI技能配置创建视图模型"""
    skill_name: str = Field(..., description="技能名称")
    skill_type: str = Field(..., description="技能类型")
    description: str = Field(default="", description="技能描述")
    config: str = Field(default="{}", description="技能配置(JSON)")
    is_active: bool = Field(default=True, description="是否激活")


class TenantAISkillUpdateViewModel(BaseModel):
    """租户AI技能配置更新视图模型"""
    id: int = Field(..., description="主键ID")
    skill_name: Optional[str] = Field(None, description="技能名称")
    skill_type: Optional[str] = Field(None, description="技能类型")
    description: Optional[str] = Field(None, description="技能描述")
    config: Optional[str] = Field(None, description="技能配置(JSON)")
    is_active: Optional[bool] = Field(None, description="是否激活")


class AIRuleInfo(BaseModel):
    """AI规则信息"""
    code: str = Field(default="", description="规则代码")
    name: str = Field(default="", description="规则名称")
    category: str = Field(default="", description="规则类别")
    priority: int = Field(default=0, description="优先级")
    content: str = Field(default="", description="规则内容")
    description: str = Field(default="", description="规则描述")
    is_active: bool = Field(default=True, description="是否激活")
    is_system: bool = Field(default=True, description="是否系统规则")


class AIRuleCategoryInfo(BaseModel):
    """AI规则分类信息"""
    code: str = Field(default="", description="分类代码")
    name: str = Field(default="", description="分类名称")
    description: str = Field(default="", description="分类描述")
    priority_range: List[int] = Field(default_factory=list, description="优先级范围")
    color: str = Field(default="", description="颜色")


class TenantAIRuleViewModel(BaseModel):
    """租户AI规则配置视图模型"""
    id: int = Field(default=0, description="主键ID")
    tenant_id: str = Field(default="", description="租户ID")
    rule_name: str = Field(default="", description="规则名称")
    rule_category: str = Field(default="", description="规则类别")
    priority: int = Field(default=0, description="优先级")
    content: str = Field(default="", description="规则内容")
    description: str = Field(default="", description="规则描述")
    is_active: bool = Field(default=True, description="是否激活")
    is_system: bool = Field(default=False, description="是否系统规则")
    is_valid: bool = Field(default=True, description="是否有效")
    creator: str = Field(default="", description="创建人")
    create_time: int = Field(default=0, description="创建时间")
    last_update_time: int = Field(default=0, description="最后更新时间")


class TenantAIRuleCreateViewModel(BaseModel):
    """租户AI规则配置创建视图模型"""
    rule_name: str = Field(..., description="规则名称")
    rule_category: str = Field(..., description="规则类别")
    priority: int = Field(default=0, description="优先级")
    content: str = Field(..., description="规则内容")
    description: str = Field(default="", description="规则描述")
    is_active: bool = Field(default=True, description="是否激活")


class TenantAIRuleUpdateViewModel(BaseModel):
    """租户AI规则配置更新视图模型"""
    id: int = Field(..., description="主键ID")
    rule_name: Optional[str] = Field(None, description="规则名称")
    rule_category: Optional[str] = Field(None, description="规则类别")
    priority: Optional[int] = Field(None, description="优先级")
    content: Optional[str] = Field(None, description="规则内容")
    description: Optional[str] = Field(None, description="规则描述")
    is_active: Optional[bool] = Field(None, description="是否激活")


class SkillGenerateRequest(BaseModel):
    """技能生成请求"""
    skill_description: str = Field(..., description="技能描述")
    skill_type: str = Field(default="custom", description="技能类型")
    context: str = Field(default="", description="上下文信息")
