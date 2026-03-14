"""
LangChain Agent Demo - LLM提供者抽象层
提供统一的LLM接口，支持多种LLM提供者（OpenAI、Anthropic、Azure、HuggingFace、Ollama等）
"""
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from langchain.llms.base import LLM
from langchain.chat_models.base import BaseChatModel
from langchain.schema import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain.callbacks.manager import CallbackManagerForLLMRun

from ..core.config import LLMConfig, LLMProviderType


class BaseLLMProvider(ABC):
    """LLM提供者基类 - 定义统一的接口"""
    
    def __init__(self, config: LLMConfig):
        """
        初始化LLM提供者
        
        Args:
            config: LLM配置对象
        """
        self.config = config
        self._llm: Optional[BaseChatModel] = None
        self._fallback_providers: List['BaseLLMProvider'] = []
    
    @abstractmethod
    def create_llm(self) -> BaseChatModel:
        """
        创建LangChain LLM实例
        
        Returns:
            BaseChatModel: LangChain聊天模型实例
        """
        pass
    
    @abstractmethod
    def get_model_name(self) -> str:
        """
        获取模型名称
        
        Returns:
            str: 模型名称
        """
        pass
    
    def get_llm(self) -> BaseChatModel:
        """
        获取LLM实例（懒加载）
        
        Returns:
            BaseChatModel: LangChain聊天模型实例
        """
        if self._llm is None:
            self._llm = self.create_llm()
        return self._llm
    
    def set_fallback_providers(self, providers: List['BaseLLMProvider']) -> None:
        """
        设置备用提供者列表
        
        Args:
            providers: 备用提供者列表
        """
        self._fallback_providers = providers
    
    async def ainvoke(
        self,
        messages: List[BaseMessage],
        run_manager: Optional[CallbackManagerForLLMRun] = None
    ) -> str:
        """
        异步调用LLM
        
        Args:
            messages: 消息列表
            run_manager: 回调管理器
        
        Returns:
            str: LLM响应
        """
        try:
            llm = self.get_llm()
            response = await llm.ainvoke(messages)
            return response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            # 尝试使用备用提供者
            if self._fallback_providers:
                for fallback in self._fallback_providers:
                    try:
                        return await fallback.ainvoke(messages, run_manager)
                    except Exception:
                        continue
            raise e
    
    def invoke(
        self,
        messages: List[BaseMessage],
        run_manager: Optional[CallbackManagerForLLMRun] = None
    ) -> str:
        """
        同步调用LLM
        
        Args:
            messages: 消息列表
            run_manager: 回调管理器
        
        Returns:
            str: LLM响应
        """
        try:
            llm = self.get_llm()
            response = llm.invoke(messages)
            return response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            # 尝试使用备用提供者
            if self._fallback_providers:
                for fallback in self._fallback_providers:
                    try:
                        return fallback.invoke(messages, run_manager)
                    except Exception:
                        continue
            raise e


class OpenAIProvider(BaseLLMProvider):
    """OpenAI LLM提供者"""
    
    def create_llm(self) -> BaseChatModel:
        """创建OpenAI聊天模型"""
        from langchain.chat_models import ChatOpenAI
        
        return ChatOpenAI(
            model=self.config.model_name,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            api_key=self.config.api_key,
            base_url=self.config.api_base,
            timeout=self.config.timeout,
            max_retries=self.config.max_retries
        )
    
    def get_model_name(self) -> str:
        """获取模型名称"""
        return self.config.model_name


class AnthropicProvider(BaseLLMProvider):
    """Anthropic LLM提供者"""
    
    def create_llm(self) -> BaseChatModel:
        """创建Anthropic聊天模型"""
        from langchain.chat_models import ChatAnthropic
        
        return ChatAnthropic(
            model=self.config.model_name,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            anthropic_api_key=self.config.api_key,
            timeout=self.config.timeout,
            max_retries=self.config.max_retries
        )
    
    def get_model_name(self) -> str:
        """获取模型名称"""
        return self.config.model_name


class AzureOpenAIProvider(BaseLLMProvider):
    """Azure OpenAI LLM提供者"""
    
    def create_llm(self) -> BaseChatModel:
        """创建Azure OpenAI聊天模型"""
        from langchain.chat_models import AzureChatOpenAI
        
        return AzureChatOpenAI(
            deployment_name=self.config.model_name,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            openai_api_key=self.config.api_key,
            openai_api_base=self.config.api_base,
            timeout=self.config.timeout,
            max_retries=self.config.max_retries
        )
    
    def get_model_name(self) -> str:
        """获取模型名称"""
        return self.config.model_name


class HuggingFaceProvider(BaseLLMProvider):
    """HuggingFace LLM提供者"""
    
    def create_llm(self) -> BaseChatModel:
        """创建HuggingFace聊天模型"""
        from langchain.llms import HuggingFacePipeline
        from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
        
        model_name = self.config.model_name
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForCausalLM.from_pretrained(model_name)
        
        pipe = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
            max_new_tokens=self.config.max_tokens,
            temperature=self.config.temperature
        )
        
        return HuggingFacePipeline(pipeline=pipe)
    
    def get_model_name(self) -> str:
        """获取模型名称"""
        return self.config.model_name


class OllamaProvider(BaseLLMProvider):
    """Ollama LLM提供者"""
    
    def create_llm(self) -> BaseChatModel:
        """创建Ollama聊天模型"""
        from langchain.chat_models import ChatOllama
        
        return ChatOllama(
            model=self.config.model_name,
            temperature=self.config.temperature,
            num_predict=self.config.max_tokens,
            base_url=self.config.api_base,
            timeout=self.config.timeout
        )
    
    def get_model_name(self) -> str:
        """获取模型名称"""
        return self.config.model_name


class LLMProviderFactory:
    """LLM提供者工厂 - 根据配置创建对应的提供者实例"""
    
    _provider_classes = {
        LLMProviderType.OPENAI: OpenAIProvider,
        LLMProviderType.ANTHROPIC: AnthropicProvider,
        LLMProviderType.AZURE: AzureOpenAIProvider,
        LLMProviderType.HUGGINGFACE: HuggingFaceProvider,
        LLMProviderType.OLLAMA: OllamaProvider
    }
    
    @classmethod
    def create_provider(cls, config: LLMConfig) -> BaseLLMProvider:
        """
        根据配置创建LLM提供者
        
        Args:
            config: LLM配置对象
        
        Returns:
            BaseLLMProvider: LLM提供者实例
        
        Raises:
            ValueError: 当提供者类型不支持时
        """
        provider_class = cls._provider_classes.get(config.provider)
        
        if provider_class is None:
            raise ValueError(f"不支持的LLM提供者类型: {config.provider}")
        
        provider = provider_class(config)
        
        # 创建备用提供者
        if config.fallback_providers:
            fallback_providers = []
            for fallback_type in config.fallback_providers:
                fallback_config = config.copy()
                fallback_config.provider = fallback_type
                fallback_config.fallback_providers = []  # 避免递归
                fallback_providers.append(cls.create_provider(fallback_config))
            provider.set_fallback_providers(fallback_providers)
        
        return provider
    
    @classmethod
    def register_provider(
        cls,
        provider_type: LLMProviderType,
        provider_class: type
    ) -> None:
        """
        注册新的LLM提供者
        
        Args:
            provider_type: 提供者类型
            provider_class: 提供者类
        """
        cls._provider_classes[provider_type] = provider_class
    
    @classmethod
    def get_supported_providers(cls) -> List[LLMProviderType]:
        """
        获取支持的提供者列表
        
        Returns:
            List[LLMProviderType]: 支持的提供者类型列表
        """
        return list(cls._provider_classes.keys())


class LLMManager:
    """LLM管理器 - 管理多个LLM提供者实例"""
    
    def __init__(self):
        """初始化LLM管理器"""
        self._providers: Dict[str, BaseLLMProvider] = {}
    
    def register_provider(self, name: str, provider: BaseLLMProvider) -> None:
        """
        注册LLM提供者
        
        Args:
            name: 提供者名称
            provider: LLM提供者实例
        """
        self._providers[name] = provider
    
    def get_provider(self, name: str) -> Optional[BaseLLMProvider]:
        """
        获取LLM提供者
        
        Args:
            name: 提供者名称
        
        Returns:
            Optional[BaseLLMProvider]: LLM提供者实例，如果不存在则返回None
        """
        return self._providers.get(name)
    
    def list_providers(self) -> List[str]:
        """
        列出所有已注册的提供者
        
        Returns:
            List[str]: 提供者名称列表
        """
        return list(self._providers.keys())
    
    def remove_provider(self, name: str) -> bool:
        """
        移除LLM提供者
        
        Args:
            name: 提供者名称
        
        Returns:
            bool: 是否成功移除
        """
        if name in self._providers:
            del self._providers[name]
            return True
        return False
