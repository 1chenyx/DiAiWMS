from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
import json


class BaseAIProvider(ABC):
    """
    AI提供商抽象基类
    
    定义AI提供商的通用接口
    """
    
    def __init__(self, api_key: str, api_endpoint: Optional[str] = None):
        """
        初始化AI提供商
        
        Args:
            api_key: API密钥
            api_endpoint: API端点URL
        """
        self.api_key = api_key
        self.api_endpoint = api_endpoint
    
    @abstractmethod
    async def chat(
        self,
        messages: list,
        model: str,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        聊天接口
        
        Args:
            messages: 消息列表
            model: 模型名称
            temperature: 温度参数
            top_p: top_p参数
            max_tokens: 最大token数
            **kwargs: 其他参数
            
        Returns:
            响应结果
        """
        pass
    
    @abstractmethod
    async def embedding(
        self,
        text: str,
        model: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        文本嵌入接口
        
        Args:
            text: 文本内容
            model: 模型名称
            **kwargs: 其他参数
            
        Returns:
            响应结果
        """
        pass


class OpenAIProvider(BaseAIProvider):
    """
    OpenAI提供商实现
    """
    
    def __init__(self, api_key: str, api_endpoint: Optional[str] = None):
        """
        初始化OpenAI提供商
        
        Args:
            api_key: API密钥
            api_endpoint: API端点URL
        """
        super().__init__(api_key, api_endpoint)
        self.client = None
    
    async def _get_client(self):
        """
        获取OpenAI客户端
        
        Returns:
            OpenAI客户端
        """
        if self.client is None:
            try:
                from openai import AsyncOpenAI
                client_kwargs = {'api_key': self.api_key}
                if self.api_endpoint:
                    client_kwargs['base_url'] = self.api_endpoint
                self.client = AsyncOpenAI(**client_kwargs)
            except ImportError:
                raise ImportError("请安装openai库: pip install openai")
        return self.client
    
    async def chat(
        self,
        messages: list,
        model: str,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        聊天接口
        
        Args:
            messages: 消息列表
            model: 模型名称
            temperature: 温度参数
            top_p: top_p参数
            max_tokens: 最大token数
            **kwargs: 其他参数
            
        Returns:
            响应结果
        """
        client = await self._get_client()
        
        chat_kwargs = {
            'model': model,
            'messages': messages
        }
        
        if temperature is not None:
            chat_kwargs['temperature'] = temperature
        if top_p is not None:
            chat_kwargs['top_p'] = top_p
        if max_tokens is not None:
            chat_kwargs['max_tokens'] = max_tokens
        
        chat_kwargs.update(kwargs)
        
        try:
            response = await client.chat.completions.create(**chat_kwargs)
            
            result = {
                'success': True,
                'content': response.choices[0].message.content,
                'model': response.model,
                'usage': {
                    'prompt_tokens': response.usage.prompt_tokens,
                    'completion_tokens': response.usage.completion_tokens,
                    'total_tokens': response.usage.total_tokens
                }
            }
            
            return result
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def embedding(
        self,
        text: str,
        model: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        文本嵌入接口
        
        Args:
            text: 文本内容
            model: 模型名称
            **kwargs: 其他参数
            
        Returns:
            响应结果
        """
        client = await self._get_client()
        
        try:
            response = await client.embeddings.create(
                model=model,
                input=text
            )
            
            result = {
                'success': True,
                'embedding': response.data[0].embedding,
                'model': response.model,
                'usage': {
                    'prompt_tokens': response.usage.prompt_tokens,
                    'total_tokens': response.usage.total_tokens
                }
            }
            
            return result
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }


class AnthropicProvider(BaseAIProvider):
    """
    Anthropic提供商实现
    """
    
    def __init__(self, api_key: str, api_endpoint: Optional[str] = None):
        """
        初始化Anthropic提供商
        
        Args:
            api_key: API密钥
            api_endpoint: API端点URL
        """
        super().__init__(api_key, api_endpoint)
        self.client = None
    
    async def _get_client(self):
        """
        获取Anthropic客户端
        
        Returns:
            Anthropic客户端
        """
        if self.client is None:
            try:
                from anthropic import AsyncAnthropic
                client_kwargs = {'api_key': self.api_key}
                if self.api_endpoint:
                    client_kwargs['base_url'] = self.api_endpoint
                self.client = AsyncAnthropic(**client_kwargs)
            except ImportError:
                raise ImportError("请安装anthropic库: pip install anthropic")
        return self.client
    
    async def chat(
        self,
        messages: list,
        model: str,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        聊天接口
        
        Args:
            messages: 消息列表
            model: 模型名称
            temperature: 温度参数
            top_p: top_p参数
            max_tokens: 最大token数
            **kwargs: 其他参数
            
        Returns:
            响应结果
        """
        client = await self._get_client()
        
        system_message = None
        user_messages = []
        
        for msg in messages:
            if msg.get('role') == 'system':
                system_message = msg.get('content')
            else:
                user_messages.append(msg)
        
        chat_kwargs = {
            'model': model,
            'messages': user_messages,
            'max_tokens': max_tokens or 4096
        }
        
        if system_message:
            chat_kwargs['system'] = system_message
        if temperature is not None:
            chat_kwargs['temperature'] = temperature
        if top_p is not None:
            chat_kwargs['top_p'] = top_p
        
        chat_kwargs.update(kwargs)
        
        try:
            response = await client.messages.create(**chat_kwargs)
            
            result = {
                'success': True,
                'content': response.content[0].text,
                'model': response.model,
                'usage': {
                    'prompt_tokens': response.usage.input_tokens,
                    'completion_tokens': response.usage.output_tokens,
                    'total_tokens': response.usage.input_tokens + response.usage.output_tokens
                }
            }
            
            return result
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def embedding(
        self,
        text: str,
        model: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        文本嵌入接口
        
        Args:
            text: 文本内容
            model: 模型名称
            **kwargs: 其他参数
            
        Returns:
            响应结果
        """
        return {
            'success': False,
            'error': 'Anthropic暂不支持embedding接口'
        }


class AIProviderFactory:
    """
    AI提供商工厂
    
    根据提供商代码创建对应的提供商实例
    """
    
    _providers = {
        'openai': OpenAIProvider,
        'azure': OpenAIProvider,
        'anthropic': AnthropicProvider
    }
    
    @classmethod
    def create_provider(
        cls,
        provider_code: str,
        api_key: str,
        api_endpoint: Optional[str] = None
    ) -> BaseAIProvider:
        """
        创建AI提供商实例
        
        Args:
            provider_code: 提供商代码
            api_key: API密钥
            api_endpoint: API端点URL
            
        Returns:
            AI提供商实例
        """
        provider_class = cls._providers.get(provider_code)
        if provider_class is None:
            raise ValueError(f"不支持的提供商: {provider_code}")
        
        return provider_class(api_key, api_endpoint)
    
    @classmethod
    def register_provider(cls, provider_code: str, provider_class: type):
        """
        注册新的AI提供商
        
        Args:
            provider_code: 提供商代码
            provider_class: 提供商类
        """
        cls._providers[provider_code] = provider_class
