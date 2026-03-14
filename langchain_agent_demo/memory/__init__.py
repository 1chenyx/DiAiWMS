"""
LangChain Agent Demo - 记忆模块
提供灵活的记忆存储后端和管理功能
"""
from .memory_system import (
    Message,
    ConversationSummary,
    BaseMemoryBackend,
    InMemoryBackend,
    RedisBackend,
    SQLiteBackend,
    MemoryManager,
    MemoryBackendFactory
)

__all__ = [
    'Message',
    'ConversationSummary',
    'BaseMemoryBackend',
    'InMemoryBackend',
    'RedisBackend',
    'SQLiteBackend',
    'MemoryManager',
    'MemoryBackendFactory'
]
