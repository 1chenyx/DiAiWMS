from fastapi import APIRouter
from app.schemas.ai_config import (
    AIProviderInfo,
    AIModelInfo,
    AIProviderWithModels,
    AIToolInfo,
    AIToolCategoryInfo,
    AIRuleInfo,
    AIRuleCategoryInfo
)
from app.ai.config.config_loader import get_ai_config_loader
from app.api.responses import success_response, error_response


_tag = "公共接口-AI系统配置"
router = APIRouter(prefix="/ai/system")


@router.get("/providers")
async def get_providers():
    """
    获取所有AI服务商
    
    Returns:
        服务商列表
    """
    config_loader = get_ai_config_loader()
    providers = config_loader.get_providers()
    
    provider_list = []
    for provider_code, provider_data in providers.items():
        provider_list.append(AIProviderInfo(
            code=provider_data.get('code', ''),
            name=provider_data.get('name', ''),
            description=provider_data.get('description', ''),
            api_base=provider_data.get('api_base', '')
        ))
    
    return success_response(provider_list)


@router.get("/providers/{provider_code}")
async def get_provider(provider_code: str):
    """
    获取指定AI服务商
    
    Args:
        provider_code: 服务商代码
        
    Returns:
        服务商信息
    """
    config_loader = get_ai_config_loader()
    provider = config_loader.get_provider(provider_code)
    
    if provider is None:
        return error_response("服务商不存在")
    
    return success_response(AIProviderInfo(
        code=provider.get('code', ''),
        name=provider.get('name', ''),
        description=provider.get('description', ''),
        api_base=provider.get('api_base', '')
    ))


@router.get("/providers/{provider_code}/models")
async def get_provider_models(provider_code: str):
    """
    获取指定AI服务商的所有模型
    
    Args:
        provider_code: 服务商代码
        
    Returns:
        模型列表
    """
    config_loader = get_ai_config_loader()
    models = config_loader.get_provider_models(provider_code)
    
    model_list = []
    for model_data in models:
        model_list.append(AIModelInfo(
            code=model_data.get('code', ''),
            name=model_data.get('name', ''),
            type=model_data.get('type', ''),
            max_tokens=model_data.get('max_tokens', 0),
            description=model_data.get('description', '')
        ))
    
    return success_response(model_list)


@router.get("/providers-with-models")
async def get_providers_with_models():
    """
    获取所有AI服务商及其模型
    
    Returns:
        服务商列表，每个服务商包含模型列表
    """
    config_loader = get_ai_config_loader()
    providers = config_loader.get_providers_with_models()
    
    provider_list = []
    for provider_data in providers:
        models = []
        for model_data in provider_data.get('models', []):
            models.append(AIModelInfo(
                code=model_data.get('code', ''),
                name=model_data.get('name', ''),
                type=model_data.get('type', ''),
                max_tokens=model_data.get('max_tokens', 0),
                description=model_data.get('description', '')
            ))
        
        provider_list.append(AIProviderWithModels(
            code=provider_data.get('code', ''),
            name=provider_data.get('name', ''),
            description=provider_data.get('description', ''),
            api_base=provider_data.get('api_base', ''),
            models=models
        ))
    
    return success_response(provider_list)


@router.get("/tools")
async def get_tools():
    """
    获取所有系统工具
    
    Returns:
        工具列表
    """
    config_loader = get_ai_config_loader()
    tools = config_loader.get_tools()
    
    tool_list = []
    for tool_data in tools:
        tool_list.append(AIToolInfo(
            code=tool_data.get('code', ''),
            name=tool_data.get('name', ''),
            category=tool_data.get('category', ''),
            description=tool_data.get('description', ''),
            is_active=tool_data.get('is_active', False),
            is_system=tool_data.get('is_system', True),
            config_schema=tool_data.get('config_schema', {})
        ))
    
    return success_response(tool_list)


@router.get("/tools/categories")
async def get_tool_categories():
    """
    获取所有工具分类
    
    Returns:
        分类列表
    """
    config_loader = get_ai_config_loader()
    categories = config_loader.get_tool_categories()
    
    category_list = []
    for cat_data in categories:
        category_list.append(AIToolCategoryInfo(
            code=cat_data.get('code', ''),
            name=cat_data.get('name', ''),
            description=cat_data.get('description', ''),
            icon=cat_data.get('icon', ''),
            color=cat_data.get('color', '')
        ))
    
    return success_response(category_list)


@router.get("/tools/{tool_code}")
async def get_tool(tool_code: str):
    """
    获取指定工具
    
    Args:
        tool_code: 工具代码
        
    Returns:
        工具信息
    """
    config_loader = get_ai_config_loader()
    tool = config_loader.get_tool(tool_code)
    
    if tool is None:
        return error_response("工具不存在")
    
    return success_response(AIToolInfo(
        code=tool.get('code', ''),
        name=tool.get('name', ''),
        category=tool.get('category', ''),
        description=tool.get('description', ''),
        is_active=tool.get('is_active', False),
        is_system=tool.get('is_system', True),
        config_schema=tool.get('config_schema', {})
    ))


@router.get("/rules")
async def get_rules():
    """
    获取所有系统规则
    
    Returns:
        规则列表
    """
    config_loader = get_ai_config_loader()
    rules = config_loader.get_rules()
    
    rule_list = []
    for rule_data in rules:
        rule_list.append(AIRuleInfo(
            code=rule_data.get('code', ''),
            name=rule_data.get('name', ''),
            category=rule_data.get('category', ''),
            priority=rule_data.get('priority', 0),
            content=rule_data.get('content', ''),
            description=rule_data.get('description', ''),
            is_active=rule_data.get('is_active', False),
            is_system=rule_data.get('is_system', True)
        ))
    
    return success_response(rule_list)


@router.get("/rules/categories")
async def get_rule_categories():
    """
    获取所有规则分类
    
    Returns:
        分类列表
    """
    config_loader = get_ai_config_loader()
    categories = config_loader.get_rule_categories()
    
    category_list = []
    for cat_data in categories:
        category_list.append(AIRuleCategoryInfo(
            code=cat_data.get('code', ''),
            name=cat_data.get('name', ''),
            description=cat_data.get('description', ''),
            priority_range=cat_data.get('priority_range', []),
            color=cat_data.get('color', '')
        ))
    
    return success_response(category_list)


@router.get("/rules/{rule_code}")
async def get_rule(rule_code: str):
    """
    获取指定规则
    
    Args:
        rule_code: 规则代码
        
    Returns:
        规则信息
    """
    config_loader = get_ai_config_loader()
    rule = config_loader.get_rule(rule_code)
    
    if rule is None:
        return error_response("规则不存在")
    
    return success_response(AIRuleInfo(
        code=rule.get('code', ''),
        name=rule.get('name', ''),
        category=rule.get('category', ''),
        priority=rule.get('priority', 0),
        content=rule.get('content', ''),
        description=rule.get('description', ''),
        is_active=rule.get('is_active', False),
        is_system=rule.get('is_system', True)
    ))
