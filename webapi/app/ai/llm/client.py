"""
LLM客户端实现
"""
import httpx
import json
import uuid
import time
from typing import Optional, List, Dict, Any, AsyncGenerator
from loguru import logger

from app.ai.llm.base import (
    BaseLLMClient,
    ChatMessage,
    ToolDefinition,
    ChatCompletionResponse
)


class LLMClient(BaseLLMClient):
    """
    LLM客户端
    
    支持OpenAI兼容API的LLM客户端
    """
    
    DEFAULT_TIMEOUT = 60.0
    
    PROVIDER_CONFIGS = {
        "openai": {
            "base_url": "https://api.openai.com/v1",
            "api_type": "openai"
        },
        "zhipu": {
            "base_url": "https://open.bigmodel.cn/api/paas/v4",
            "api_type": "zhipu"
        },
        "deepseek": {
            "base_url": "https://api.deepseek.com/v1",
            "api_type": "openai"
        },
        "moonshot": {
            "base_url": "https://api.moonshot.cn/v1",
            "api_type": "openai"
        },
        "qwen": {
            "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
            "api_type": "openai"
        },
        "ollama": {
            "base_url": "http://localhost:11434/v1",
            "api_type": "openai"
        }
    }
    
    def __init__(
        self,
        provider_code: str,
        api_key: str,
        base_url: Optional[str] = None
    ):
        """
        初始化LLM客户端
        
        Args:
            provider_code: 服务商代码
            api_key: API密钥
            base_url: API基础URL（可选）
        """
        self.provider_code = provider_code
        self.api_key = api_key
        
        provider_config = self.PROVIDER_CONFIGS.get(provider_code, {})
        self.base_url = base_url or provider_config.get("base_url", "")
        self.api_type = provider_config.get("api_type", "openai")
        
        if not self.base_url:
            raise ValueError(f"未知的LLM服务商: {provider_code}，请提供base_url")
    
    def _get_headers(self) -> Dict[str, str]:
        """
        获取请求头
        
        Returns:
            请求头字典
        """
        if self.api_type == "zhipu":
            return {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
        else:
            return {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
    
    def _build_request_body(
        self,
        messages: List[ChatMessage],
        model: str,
        temperature: float,
        max_tokens: int,
        tools: Optional[List[ToolDefinition]],
        tool_choice: Optional[str],
        stream: bool
    ) -> Dict[str, Any]:
        """
        构建请求体
        
        Args:
            messages: 消息列表
            model: 模型代码
            temperature: 温度参数
            max_tokens: 最大token数
            tools: 工具列表
            tool_choice: 工具选择策略
            stream: 是否流式
            
        Returns:
            请求体字典
        """
        body = {
            "model": model,
            "messages": [msg.model_dump(exclude_none=True) for msg in messages],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream
        }
        
        if tools:
            body["tools"] = [tool.model_dump() for tool in tools]
            body["tool_choice"] = tool_choice
        
        return body
    
    async def chat_completion(
        self,
        messages: List[ChatMessage],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        tools: Optional[List[ToolDefinition]] = None,
        tool_choice: Optional[str] = "auto"
    ) -> ChatCompletionResponse:
        """
        聊天完成
        
        Args:
            messages: 消息列表
            model: 模型代码
            temperature: 温度参数
            max_tokens: 最大token数
            tools: 工具列表
            tool_choice: 工具选择策略
            
        Returns:
            聊天完成响应
        """
        url = f"{self.base_url}/chat/completions"
        headers = self._get_headers()
        body = self._build_request_body(
            messages, model, temperature, max_tokens,
            tools, tool_choice, stream=False
        )
        
        try:
            async with httpx.AsyncClient(timeout=self.DEFAULT_TIMEOUT) as client:
                response = await client.post(url, headers=headers, json=body)
                response.raise_for_status()
                data = response.json()
                
                return ChatCompletionResponse(
                    id=data.get("id", str(uuid.uuid4())),
                    model=data.get("model", model),
                    choices=data.get("choices", []),
                    usage=data.get("usage", {}),
                    created=data.get("created")
                )
                
        except httpx.HTTPStatusError as e:
            error_detail = ""
            try:
                error_detail = e.response.text
            except:
                pass
            logger.error(f"LLM API请求失败: {e}, 详情: {error_detail}")
            raise Exception(f"LLM API请求失败: {e.response.status_code} - {error_detail}")
        except Exception as e:
            logger.error(f"LLM调用异常: {e}")
            raise
    
    async def chat_completion_stream(
        self,
        messages: List[ChatMessage],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        tools: Optional[List[ToolDefinition]] = None,
        tool_choice: Optional[str] = "auto"
    ) -> AsyncGenerator[str, None]:
        """
        流式聊天完成
        
        Args:
            messages: 消息列表
            model: 模型代码
            temperature: 温度参数
            max_tokens: 最大token数
            tools: 工具列表
            tool_choice: 工具选择策略
            
        Yields:
            流式响应块
        """
        url = f"{self.base_url}/chat/completions"
        headers = self._get_headers()
        body = self._build_request_body(
            messages, model, temperature, max_tokens,
            tools, tool_choice, stream=True
        )
        
        try:
            async with httpx.AsyncClient(timeout=self.DEFAULT_TIMEOUT) as client:
                async with client.stream("POST", url, headers=headers, json=body) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data = line[6:]
                            if data == "[DONE]":
                                break
                            try:
                                chunk = json.loads(data)
                                yield chunk
                            except json.JSONDecodeError:
                                continue
                                
        except httpx.HTTPStatusError as e:
            error_detail = ""
            try:
                error_detail = e.response.text
            except:
                pass
            logger.error(f"LLM流式API请求失败: {e}, 详情: {error_detail}")
            raise Exception(f"LLM流式API请求失败: {e.response.status_code}")
        except Exception as e:
            logger.error(f"LLM流式调用异常: {e}")
            raise


def create_llm_client(
    provider_code: str,
    api_key: str,
    base_url: Optional[str] = None
) -> LLMClient:
    """
    创建LLM客户端
    
    Args:
        provider_code: 服务商代码
        api_key: API密钥
        base_url: API基础URL
        
    Returns:
        LLM客户端实例
    """
    return LLMClient(provider_code, api_key, base_url)
