import yaml
from typing import Dict, List, Any
from pathlib import Path


class AIConfigLoader:
    """
    AI配置加载器
    
    从YAML文件加载全局AI提供商和模型配置
    """
    
    def __init__(self, config_path: str = None):
        """
        初始化配置加载器
        
        Args:
            config_path: 配置文件路径，默认为app/ai/providers.yaml
        """
        if config_path is None:
            config_path = str(Path(__file__).parent / "providers.yaml")
        
        self.config_path = config_path
        self._config = None
        self._providers = None
        self._models = None
    
    def load_config(self) -> Dict[str, Any]:
        """
        加载配置文件
        
        Returns:
            配置字典
        """
        if self._config is None:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self._config = yaml.safe_load(f)
        return self._config
    
    def get_providers(self) -> Dict[str, Dict[str, Any]]:
        """
        获取所有提供商
        
        Returns:
            提供商字典，key为provider_code
        """
        if self._providers is None:
            config = self.load_config()
            self._providers = {}
            for provider_code, provider_data in config.get('providers', {}).items():
                self._providers[provider_code] = {
                    'code': provider_code,
                    'name': provider_data.get('name', ''),
                    'description': provider_data.get('description', '')
                }
        return self._providers
    
    def get_provider(self, provider_code: str) -> Dict[str, Any]:
        """
        获取指定提供商
        
        Args:
            provider_code: 提供商代码
            
        Returns:
            提供商信息
        """
        providers = self.get_providers()
        return providers.get(provider_code)
    
    def get_models(self) -> Dict[str, Dict[str, Any]]:
        """
        获取所有模型
        
        Returns:
            模型字典，key为provider_code:model_code
        """
        if self._models is None:
            config = self.load_config()
            self._models = {}
            for provider_code, provider_data in config.get('providers', {}).items():
                for model_data in provider_data.get('models', []):
                    model_code = model_data.get('code', '')
                    key = f"{provider_code}:{model_code}"
                    self._models[key] = {
                        'provider_code': provider_code,
                        'code': model_code,
                        'name': model_data.get('name', ''),
                        'type': model_data.get('type', ''),
                        'max_tokens': model_data.get('max_tokens', 0),
                        'description': model_data.get('description', '')
                    }
        return self._models
    
    def get_provider_models(self, provider_code: str) -> List[Dict[str, Any]]:
        """
        获取指定提供商的所有模型
        
        Args:
            provider_code: 提供商代码
            
        Returns:
            模型列表
        """
        config = self.load_config()
        provider_data = config.get('providers', {}).get(provider_code, {})
        models = []
        for model_data in provider_data.get('models', []):
            models.append({
                'provider_code': provider_code,
                'code': model_data.get('code', ''),
                'name': model_data.get('name', ''),
                'type': model_data.get('type', ''),
                'max_tokens': model_data.get('max_tokens', 0),
                'description': model_data.get('description', '')
            })
        return models
    
    def get_model(self, provider_code: str, model_code: str) -> Dict[str, Any]:
        """
        获取指定模型
        
        Args:
            provider_code: 提供商代码
            model_code: 模型代码
            
        Returns:
            模型信息
        """
        models = self.get_models()
        key = f"{provider_code}:{model_code}"
        return models.get(key)
    
    def get_providers_with_models(self) -> List[Dict[str, Any]]:
        """
        获取所有提供商及其模型
        
        Returns:
            提供商列表，每个提供商包含模型列表
        """
        config = self.load_config()
        result = []
        for provider_code, provider_data in config.get('providers', {}).items():
            models = []
            for model_data in provider_data.get('models', []):
                models.append({
                    'code': model_data.get('code', ''),
                    'name': model_data.get('name', ''),
                    'type': model_data.get('type', ''),
                    'max_tokens': model_data.get('max_tokens', 0),
                    'description': model_data.get('description', '')
                })
            
            result.append({
                'code': provider_code,
                'name': provider_data.get('name', ''),
                'description': provider_data.get('description', ''),
                'models': models
            })
        return result


_global_config_loader = None


def get_ai_config_loader() -> AIConfigLoader:
    """
    获取全局AI配置加载器实例
    
    Returns:
        AI配置加载器实例
    """
    global _global_config_loader
    if _global_config_loader is None:
        _global_config_loader = AIConfigLoader()
    return _global_config_loader
