from fastapi import APIRouter
from app.schemas.ai_config import (
    AIProviderInfo,
    AIModelInfo,
    AIProviderWithModels
)
from app.ai.config_loader import get_ai_config_loader
from app.api.responses import success_response, error_response


router = APIRouter(prefix="/ai/config", tags=["AI配置"])


@router.get("/providers")
async def get_providers():
    """
    获取所有AI提供商
    
    Returns:
        提供商列表
    """
    config_loader = get_ai_config_loader()
    providers = config_loader.get_providers()
    
    provider_list = []
    for provider_code, provider_data in providers.items():
        provider_list.append(AIProviderInfo(
            code=provider_data['code'],
            name=provider_data['name'],
            description=provider_data['description']
        ))
    
    return success_response(provider_list)


@router.get("/providers/{provider_code}")
async def get_provider(provider_code: str):
    """
    获取指定AI提供商
    
    Args:
        provider_code: 提供商代码
        
    Returns:
        提供商信息
    """
    config_loader = get_ai_config_loader()
    provider = config_loader.get_provider(provider_code)
    
    if provider is None:
        return error_response("提供商不存在")
    
    return success_response(AIProviderInfo(
        code=provider['code'],
        name=provider['name'],
        description=provider['description']
    ))


@router.get("/providers/{provider_code}/models")
async def get_provider_models(provider_code: str):
    """
    获取指定AI提供商的所有模型
    
    Args:
        provider_code: 提供商代码
        
    Returns:
        模型列表
    """
    config_loader = get_ai_config_loader()
    models = config_loader.get_provider_models(provider_code)
    
    model_list = []
    for model_data in models:
        model_list.append(AIModelInfo(
            code=model_data['code'],
            name=model_data['name'],
            type=model_data['type'],
            max_tokens=model_data['max_tokens'],
            description=model_data['description']
        ))
    
    return success_response(model_list)


@router.get("/providers-with-models")
async def get_providers_with_models():
    """
    获取所有AI提供商及其模型
    
    Returns:
        提供商列表，每个提供商包含模型列表
    """
    config_loader = get_ai_config_loader()
    providers = config_loader.get_providers_with_models()
    
    provider_list = []
    for provider_data in providers:
        models = []
        for model_data in provider_data['models']:
            models.append(AIModelInfo(
                code=model_data['code'],
                name=model_data['name'],
                type=model_data['type'],
                max_tokens=model_data['max_tokens'],
                description=model_data['description']
            ))
        
        provider_list.append(AIProviderWithModels(
            code=provider_data['code'],
            name=provider_data['name'],
            description=provider_data['description'],
            models=models
        ))
    
    return success_response(provider_list)
