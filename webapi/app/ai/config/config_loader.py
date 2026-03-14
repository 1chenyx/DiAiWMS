import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any
from loguru import logger


class AIConfigLoader:
    """
    AI配置加载器
    
    负责加载和管理AI相关的配置文件
    """
    
    def __init__(self):
        self._config_dir = Path(__file__).parent
        self._providers_config = None
        self._tools_config = None
        self._rules_config = None
        self._load_configs()
    
    def _load_configs(self):
        """加载所有配置文件"""
        try:
            self._load_providers_config()
            self._load_tools_config()
            self._load_rules_config()
            logger.info("AI配置文件加载成功")
        except Exception as e:
            logger.error(f"AI配置文件加载失败: {e}")
    
    def _load_providers_config(self):
        """加载LLM服务商配置"""
        config_path = self._config_dir / "llm_providers.yaml"
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                self._providers_config = yaml.safe_load(f)
        else:
            self._providers_config = {"providers": {}}
            logger.warning(f"LLM服务商配置文件不存在: {config_path}")
    
    def _load_tools_config(self):
        """加载工具配置"""
        config_path = self._config_dir / "ai_tools.yaml"
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                self._tools_config = yaml.safe_load(f)
        else:
            self._tools_config = {"tools": [], "categories": []}
            logger.warning(f"工具配置文件不存在: {config_path}")
    
    def _load_rules_config(self):
        """加载规则配置"""
        config_path = self._config_dir / "ai_rules.yaml"
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                self._rules_config = yaml.safe_load(f)
        else:
            self._rules_config = {"rules": [], "categories": []}
            logger.warning(f"规则配置文件不存在: {config_path}")
    
    def get_providers(self) -> Dict[str, Any]:
        """
        获取所有LLM服务商
        
        Returns:
            服务商字典
        """
        return self._providers_config.get("providers", {})
    
    def get_provider(self, provider_code: str) -> Optional[Dict[str, Any]]:
        """
        获取指定的LLM服务商
        
        Args:
            provider_code: 服务商代码
            
        Returns:
            服务商信息
        """
        providers = self.get_providers()
        return providers.get(provider_code)
    
    def get_provider_models(self, provider_code: str) -> List[Dict[str, Any]]:
        """
        获取指定服务商的所有模型
        
        Args:
            provider_code: 服务商代码
            
        Returns:
            模型列表
        """
        provider = self.get_provider(provider_code)
        if provider:
            return provider.get("models", [])
        return []
    
    def get_model(self, provider_code: str, model_code: str) -> Optional[Dict[str, Any]]:
        """
        获取指定的模型信息
        
        Args:
            provider_code: 服务商代码
            model_code: 模型代码
            
        Returns:
            模型信息
        """
        models = self.get_provider_models(provider_code)
        for model in models:
            if model.get("code") == model_code:
                return model
        return None
    
    def get_providers_with_models(self) -> List[Dict[str, Any]]:
        """
        获取所有服务商及其模型
        
        Returns:
            服务商列表，每个服务商包含模型列表
        """
        providers = self.get_providers()
        result = []
        for provider_code, provider_data in providers.items():
            provider_info = {
                "code": provider_data.get("code"),
                "name": provider_data.get("name"),
                "description": provider_data.get("description"),
                "api_base": provider_data.get("api_base"),
                "models": provider_data.get("models", [])
            }
            result.append(provider_info)
        return result
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """
        获取所有工具
        
        Returns:
            工具列表
        """
        return self._tools_config.get("tools", [])
    
    def get_tool(self, tool_code: str) -> Optional[Dict[str, Any]]:
        """
        获取指定的工具
        
        Args:
            tool_code: 工具代码
            
        Returns:
            工具信息
        """
        tools = self.get_tools()
        for tool in tools:
            if tool.get("code") == tool_code:
                return tool
        return None
    
    def get_tools_by_category(self, category_code: str) -> List[Dict[str, Any]]:
        """
        获取指定分类的工具
        
        Args:
            category_code: 分类代码
            
        Returns:
            工具列表
        """
        tools = self.get_tools()
        return [tool for tool in tools if tool.get("category") == category_code]
    
    def get_tool_categories(self) -> List[Dict[str, Any]]:
        """
        获取所有工具分类
        
        Returns:
            分类列表
        """
        return self._tools_config.get("categories", [])
    
    def get_rules(self) -> List[Dict[str, Any]]:
        """
        获取所有系统规则
        
        Returns:
            规则列表
        """
        return self._rules_config.get("rules", [])
    
    def get_rule(self, rule_code: str) -> Optional[Dict[str, Any]]:
        """
        获取指定的规则
        
        Args:
            rule_code: 规则代码
            
        Returns:
            规则信息
        """
        rules = self.get_rules()
        for rule in rules:
            if rule.get("code") == rule_code:
                return rule
        return None
    
    def get_rules_by_category(self, category_code: str) -> List[Dict[str, Any]]:
        """
        获取指定分类的规则
        
        Args:
            category_code: 分类代码
            
        Returns:
            规则列表
        """
        rules = self.get_rules()
        return [rule for rule in rules if rule.get("category") == category_code]
    
    def get_active_rules(self) -> List[Dict[str, Any]]:
        """
        获取所有激活的规则
        
        Returns:
            激活的规则列表
        """
        rules = self.get_rules()
        return [rule for rule in rules if rule.get("is_active", False)]
    
    def get_rule_categories(self) -> List[Dict[str, Any]]:
        """
        获取所有规则分类
        
        Returns:
            分类列表
        """
        return self._rules_config.get("categories", [])


_ai_config_loader = None


def get_ai_config_loader() -> AIConfigLoader:
    """
    获取AI配置加载器单例
    
    Returns:
        AIConfigLoader实例
    """
    global _ai_config_loader
    if _ai_config_loader is None:
        _ai_config_loader = AIConfigLoader()
    return _ai_config_loader
