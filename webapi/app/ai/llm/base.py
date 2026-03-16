"""
LLM客户端基类
"""
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class ChatMessage(BaseModel):
    """聊天消息"""
    role: str
    content: str
    name: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_call_id: Optional[str] = None


class ToolDefinition(BaseModel):
    """工具定义"""
    type: str = "function"
    function: Dict[str, Any]


class ChatCompletionRequest(BaseModel):
    """聊天完成请求"""
    messages: List[ChatMessage]
    model: str
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 2000
    tools: Optional[List[ToolDefinition]] = None
    tool_choice: Optional[str] = "auto"
    stream: bool = False


class ChatCompletionResponse(BaseModel):
    """聊天完成响应"""
    id: str
    model: str
    choices: List[Dict[str, Any]]
    usage: Dict[str, int]
    created: Optional[int] = None


class BaseLLMClient(ABC):
    """
    LLM客户端基类
    
    定义所有LLM客户端必须实现的接口
    """
    
    @abstractmethod
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
        pass
    
    @abstractmethod
    async def chat_completion_stream(
        self,
        messages: List[ChatMessage],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        tools: Optional[List[ToolDefinition]] = None,
        tool_choice: Optional[str] = "auto"
    ):
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
        pass
