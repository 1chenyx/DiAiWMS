from typing import Optional, Dict, Any
from app.ai.config_loader import get_ai_config_loader


class AICacheManager:
    """
    AI缓存管理器
    
    管理AI配置的缓存，由于提供商和模型现在是全局配置文件，主要缓存租户AI配置
    """
    
    def __init__(self, redis_client=None):
        """
        初始化缓存管理器
        
        Args:
            redis_client: Redis客户端实例
        """
        self.redis = redis_client
        self.config_loader = get_ai_config_loader()
    
    def get_providers(self) -> Dict[str, Dict[str, Any]]:
        """
        获取所有提供商（从配置文件）
        
        Returns:
            提供商字典
        """
        return self.config_loader.get_providers()
    
    def get_provider(self, provider_code: str) -> Optional[Dict[str, Any]]:
        """
        获取指定提供商（从配置文件）
        
        Args:
            provider_code: 提供商代码
            
        Returns:
            提供商信息
        """
        return self.config_loader.get_provider(provider_code)
    
    def get_models(self) -> Dict[str, Dict[str, Any]]:
        """
        获取所有模型（从配置文件）
        
        Returns:
            模型字典
        """
        return self.config_loader.get_models()
    
    def get_model(self, provider_code: str, model_code: str) -> Optional[Dict[str, Any]]:
        """
        获取指定模型（从配置文件）
        
        Args:
            provider_code: 提供商代码
            model_code: 模型代码
            
        Returns:
            模型信息
        """
        return self.config_loader.get_model(provider_code, model_code)
    
    def get_provider_models(self, provider_code: str) -> list:
        """
        获取指定提供商的所有模型（从配置文件）
        
        Args:
            provider_code: 提供商代码
            
        Returns:
            模型列表
        """
        return self.config_loader.get_provider_models(provider_code)
    
    def get_providers_with_models(self) -> list:
        """
        获取所有提供商及其模型（从配置文件）
        
        Returns:
            提供商列表
        """
        return self.config_loader.get_providers_with_models()
    
    async def get_tenant_config(
        self,
        tenant_id: str,
        config_id: int,
        config_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        获取租户AI配置（带缓存）
        
        Args:
            tenant_id: 租户ID
            config_id: 配置ID
            config_data: 配置数据
            
        Returns:
            配置信息
        """
        cache_key = f"ai:tenant_config:{tenant_id}:{config_id}"
        
        if self.redis:
            try:
                cached = await self.redis.get(cache_key)
                if cached:
                    import json
                    return json.loads(cached)
            except Exception:
                pass
        
        provider = self.config_loader.get_provider(config_data.get('provider_code', ''))
        model = self.config_loader.get_model(
            config_data.get('provider_code', ''),
            config_data.get('model_code', '')
        )
        
        result = {
            'id': config_data.get('id'),
            'provider_code': config_data.get('provider_code'),
            'provider_name': provider.get('name', '') if provider else '',
            'model_code': config_data.get('model_code'),
            'model_name': model.get('name', '') if model else '',
            'api_key': config_data.get('api_key'),
            'api_endpoint': config_data.get('api_endpoint'),
            'is_default': config_data.get('is_default'),
            'temperature': config_data.get('temperature'),
            'top_p': config_data.get('top_p'),
            'max_tokens': config_data.get('max_tokens'),
            'config': config_data.get('config'),
            'tenant_id': config_data.get('tenant_id'),
            'creator': config_data.get('creator'),
            'create_time': config_data.get('create_time'),
            'last_update_time': config_data.get('last_update_time'),
            'is_valid': config_data.get('is_valid')
        }
        
        if self.redis:
            try:
                import json
                await self.redis.setex(
                    cache_key,
                    3600,
                    json.dumps(result, ensure_ascii=False)
                )
            except Exception:
                pass
        
        return result
    
    async def invalidate_tenant_config(self, tenant_id: str, config_id: int):
        """
        使租户AI配置缓存失效
        
        Args:
            tenant_id: 租户ID
            config_id: 配置ID
        """
        if self.redis:
            try:
                cache_key = f"ai:tenant_config:{tenant_id}:{config_id}"
                await self.redis.delete(cache_key)
            except Exception:
                pass
