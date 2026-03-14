"""
LangChain Agent Demo - 记忆管理系统
提供灵活的记忆存储后端，支持多种存储方式（内存、Redis、SQLite、PostgreSQL等）
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field
import json
import logging

logger = logging.getLogger(__name__)


class Message(BaseModel):
    """消息模型"""
    role: str = Field(..., description="消息角色（user/assistant/system）")
    content: str = Field(..., description="消息内容")
    timestamp: datetime = Field(default_factory=datetime.now, description="时间戳")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")


class ConversationSummary(BaseModel):
    """对话摘要模型"""
    summary: str = Field(..., description="摘要内容")
    message_count: int = Field(..., description="消息数量")
    timestamp: datetime = Field(default_factory=datetime.now, description="摘要时间")


class BaseMemoryBackend(ABC):
    """记忆存储后端基类"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        初始化记忆存储后端
        
        Args:
            config: 后端配置
        """
        self.config = config or {}
        self._max_history = self.config.get('max_history', 10)
    
    @abstractmethod
    def add_message(
        self,
        session_id: str,
        message: Message
    ) -> None:
        """
        添加消息到记忆
        
        Args:
            session_id: 会话ID
            message: 消息对象
        """
        pass
    
    @abstractmethod
    def get_messages(
        self,
        session_id: str,
        limit: Optional[int] = None
    ) -> List[Message]:
        """
        获取会话消息
        
        Args:
            session_id: 会话ID
            limit: 消息数量限制
        
        Returns:
            List[Message]: 消息列表
        """
        pass
    
    @abstractmethod
    def clear_session(self, session_id: str) -> None:
        """
        清除会话记忆
        
        Args:
            session_id: 会话ID
        """
        pass
    
    @abstractmethod
    def get_all_sessions(self) -> List[str]:
        """
        获取所有会话ID
        
        Returns:
            List[str]: 会话ID列表
        """
        pass
    
    @abstractmethod
    def delete_session(self, session_id: str) -> bool:
        """
        删除会话
        
        Args:
            session_id: 会话ID
        
        Returns:
            bool: 是否成功删除
        """
        pass
    
    def set_max_history(self, max_history: int) -> None:
        """
        设置最大历史记录数
        
        Args:
            max_history: 最大历史记录数
        """
        self._max_history = max_history
    
    def get_max_history(self) -> int:
        """
        获取最大历史记录数
        
        Returns:
            int: 最大历史记录数
        """
        return self._max_history


class InMemoryBackend(BaseMemoryBackend):
    """内存存储后端"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        初始化内存存储后端
        
        Args:
            config: 后端配置
        """
        super().__init__(config)
        self._sessions: Dict[str, List[Message]] = {}
        self._summaries: Dict[str, ConversationSummary] = {}
    
    def add_message(
        self,
        session_id: str,
        message: Message
    ) -> None:
        """添加消息到内存"""
        if session_id not in self._sessions:
            self._sessions[session_id] = []
        
        self._sessions[session_id].append(message)
        
        # 限制历史记录数量
        if len(self._sessions[session_id]) > self._max_history:
            self._sessions[session_id] = self._sessions[session_id][-self._max_history:]
    
    def get_messages(
        self,
        session_id: str,
        limit: Optional[int] = None
    ) -> List[Message]:
        """从内存获取消息"""
        messages = self._sessions.get(session_id, [])
        
        if limit:
            return messages[-limit:]
        
        return messages
    
    def clear_session(self, session_id: str) -> None:
        """清除会话记忆"""
        if session_id in self._sessions:
            self._sessions[session_id] = []
        if session_id in self._summaries:
            del self._summaries[session_id]
    
    def get_all_sessions(self) -> List[str]:
        """获取所有会话ID"""
        return list(self._sessions.keys())
    
    def delete_session(self, session_id: str) -> bool:
        """删除会话"""
        if session_id in self._sessions:
            del self._sessions[session_id]
            if session_id in self._summaries:
                del self._summaries[session_id]
            return True
        return False
    
    def set_summary(self, session_id: str, summary: ConversationSummary) -> None:
        """
        设置对话摘要
        
        Args:
            session_id: 会话ID
            summary: 摘要对象
        """
        self._summaries[session_id] = summary
    
    def get_summary(self, session_id: str) -> Optional[ConversationSummary]:
        """
        获取对话摘要
        
        Args:
            session_id: 会话ID
        
        Returns:
            Optional[ConversationSummary]: 摘要对象
        """
        return self._summaries.get(session_id)


class RedisBackend(BaseMemoryBackend):
    """Redis存储后端"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        初始化Redis存储后端
        
        Args:
            config: 后端配置
        """
        super().__init__(config)
        self._client = None
        self._initialize_client()
    
    def _initialize_client(self) -> None:
        """初始化Redis客户端"""
        try:
            import redis
            
            self._client = redis.Redis(
                host=self.config.get('redis_host', 'localhost'),
                port=self.config.get('redis_port', 6379),
                db=self.config.get('redis_db', 0),
                password=self.config.get('redis_password'),
                decode_responses=True
            )
            
            # 测试连接
            self._client.ping()
            logger.info("Redis连接成功")
        
        except ImportError:
            logger.error("redis库未安装，请运行: pip install redis")
            raise
        except Exception as e:
            logger.error(f"Redis连接失败: {e}")
            raise
    
    def _get_session_key(self, session_id: str) -> str:
        """获取会话键"""
        return f"agent:memory:session:{session_id}"
    
    def _get_summary_key(self, session_id: str) -> str:
        """获取摘要键"""
        return f"agent:memory:summary:{session_id}"
    
    def add_message(
        self,
        session_id: str,
        message: Message
    ) -> None:
        """添加消息到Redis"""
        if not self._client:
            raise RuntimeError("Redis客户端未初始化")
        
        key = self._get_session_key(session_id)
        message_json = message.json()
        
        # 使用列表存储消息
        self._client.rpush(key, message_json)
        
        # 限制历史记录数量
        self._client.ltrim(key, -self._max_history, -1)
    
    def get_messages(
        self,
        session_id: str,
        limit: Optional[int] = None
    ) -> List[Message]:
        """从Redis获取消息"""
        if not self._client:
            raise RuntimeError("Redis客户端未初始化")
        
        key = self._get_session_key(session_id)
        
        if limit:
            message_jsons = self._client.lrange(key, -limit, -1)
        else:
            message_jsons = self._client.lrange(key, 0, -1)
        
        messages = []
        for msg_json in message_jsons:
            try:
                message_dict = json.loads(msg_json)
                messages.append(Message(**message_dict))
            except Exception as e:
                logger.error(f"解析消息失败: {e}")
        
        return messages
    
    def clear_session(self, session_id: str) -> None:
        """清除会话记忆"""
        if not self._client:
            raise RuntimeError("Redis客户端未初始化")
        
        session_key = self._get_session_key(session_id)
        summary_key = self._get_summary_key(session_id)
        
        self._client.delete(session_key)
        self._client.delete(summary_key)
    
    def get_all_sessions(self) -> List[str]:
        """获取所有会话ID"""
        if not self._client:
            raise RuntimeError("Redis客户端未初始化")
        
        pattern = "agent:memory:session:*"
        keys = self._client.keys(pattern)
        
        session_ids = []
        for key in keys:
            # 提取session_id
            session_id = key.replace("agent:memory:session:", "")
            session_ids.append(session_id)
        
        return session_ids
    
    def delete_session(self, session_id: str) -> bool:
        """删除会话"""
        try:
            self.clear_session(session_id)
            return True
        except Exception:
            return False


class SQLiteBackend(BaseMemoryBackend):
    """SQLite存储后端"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        初始化SQLite存储后端
        
        Args:
            config: 后端配置
        """
        super().__init__(config)
        self._conn = None
        self._initialize_database()
    
    def _initialize_database(self) -> None:
        """初始化SQLite数据库"""
        try:
            import sqlite3
            
            db_path = self.config.get('sqlite_path', ':memory:')
            self._conn = sqlite3.connect(db_path, check_same_thread=False)
            self._conn.row_factory = sqlite3.Row
            
            # 创建表
            self._create_tables()
            logger.info("SQLite数据库初始化成功")
        
        except Exception as e:
            logger.error(f"SQLite初始化失败: {e}")
            raise
    
    def _create_tables(self) -> None:
        """创建数据库表"""
        cursor = self._conn.cursor()
        
        # 创建消息表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                metadata TEXT
            )
        ''')
        
        # 创建摘要表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS summaries (
                session_id TEXT PRIMARY KEY,
                summary TEXT NOT NULL,
                message_count INTEGER NOT NULL,
                timestamp TEXT NOT NULL
            )
        ''')
        
        # 创建索引
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_session_id 
            ON messages(session_id)
        ''')
        
        self._conn.commit()
    
    def add_message(
        self,
        session_id: str,
        message: Message
    ) -> None:
        """添加消息到SQLite"""
        if not self._conn:
            raise RuntimeError("数据库连接未初始化")
        
        cursor = self._conn.cursor()
        
        cursor.execute('''
            INSERT INTO messages (session_id, role, content, timestamp, metadata)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            session_id,
            message.role,
            message.content,
            message.timestamp.isoformat(),
            json.dumps(message.metadata)
        ))
        
        self._conn.commit()
        
        # 限制历史记录数量
        self._prune_old_messages(session_id)
    
    def _prune_old_messages(self, session_id: str) -> None:
        """清理旧消息"""
        cursor = self._conn.cursor()
        
        # 获取当前消息数量
        cursor.execute('''
            SELECT COUNT(*) as count FROM messages WHERE session_id = ?
        ''', (session_id,))
        
        count = cursor.fetchone()['count']
        
        if count > self._max_history:
            # 删除旧消息
            delete_count = count - self._max_history
            cursor.execute('''
                DELETE FROM messages 
                WHERE id IN (
                    SELECT id FROM messages 
                    WHERE session_id = ? 
                    ORDER BY id ASC 
                    LIMIT ?
                )
            ''', (session_id, delete_count))
            
            self._conn.commit()
    
    def get_messages(
        self,
        session_id: str,
        limit: Optional[int] = None
    ) -> List[Message]:
        """从SQLite获取消息"""
        if not self._conn:
            raise RuntimeError("数据库连接未初始化")
        
        cursor = self._conn.cursor()
        
        if limit:
            cursor.execute('''
                SELECT * FROM messages 
                WHERE session_id = ? 
                ORDER BY id DESC 
                LIMIT ?
            ''', (session_id, limit))
        else:
            cursor.execute('''
                SELECT * FROM messages 
                WHERE session_id = ? 
                ORDER BY id ASC
            ''', (session_id,))
        
        rows = cursor.fetchall()
        messages = []
        
        for row in rows:
            metadata = json.loads(row['metadata']) if row['metadata'] else {}
            message = Message(
                role=row['role'],
                content=row['content'],
                timestamp=datetime.fromisoformat(row['timestamp']),
                metadata=metadata
            )
            messages.append(message)
        
        # 如果有limit，需要反转顺序
        if limit:
            messages.reverse()
        
        return messages
    
    def clear_session(self, session_id: str) -> None:
        """清除会话记忆"""
        if not self._conn:
            raise RuntimeError("数据库连接未初始化")
        
        cursor = self._conn.cursor()
        
        cursor.execute('DELETE FROM messages WHERE session_id = ?', (session_id,))
        cursor.execute('DELETE FROM summaries WHERE session_id = ?', (session_id,))
        
        self._conn.commit()
    
    def get_all_sessions(self) -> List[str]:
        """获取所有会话ID"""
        if not self._conn:
            raise RuntimeError("数据库连接未初始化")
        
        cursor = self._conn.cursor()
        
        cursor.execute('SELECT DISTINCT session_id FROM messages')
        rows = cursor.fetchall()
        
        return [row['session_id'] for row in rows]
    
    def delete_session(self, session_id: str) -> bool:
        """删除会话"""
        try:
            self.clear_session(session_id)
            return True
        except Exception:
            return False


class MemoryManager:
    """记忆管理器 - 提供记忆管理的统一接口"""
    
    def __init__(self, backend: BaseMemoryBackend):
        """
        初始化记忆管理器
        
        Args:
            backend: 记忆存储后端
        """
        self.backend = backend
        self._enable_summarization = False
        self._summarization_threshold = 5
    
    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        metadata: Dict[str, Any] = None
    ) -> None:
        """
        添加消息
        
        Args:
            session_id: 会话ID
            role: 消息角色
            content: 消息内容
            metadata: 元数据
        """
        message = Message(
            role=role,
            content=content,
            metadata=metadata or {}
        )
        
        self.backend.add_message(session_id, message)
    
    def get_messages(
        self,
        session_id: str,
        limit: Optional[int] = None
    ) -> List[Message]:
        """
        获取消息
        
        Args:
            session_id: 会话ID
            limit: 消息数量限制
        
        Returns:
            List[Message]: 消息列表
        """
        return self.backend.get_messages(session_id, limit)
    
    def get_messages_as_string(
        self,
        session_id: str,
        limit: Optional[int] = None
    ) -> str:
        """
        获取消息为字符串格式
        
        Args:
            session_id: 会话ID
            limit: 消息数量限制
        
        Returns:
            str: 消息字符串
        """
        messages = self.get_messages(session_id, limit)
        
        lines = []
        for msg in messages:
            lines.append(f"{msg.role}: {msg.content}")
        
        return "\n".join(lines)
    
    def clear_session(self, session_id: str) -> None:
        """
        清除会话
        
        Args:
            session_id: 会话ID
        """
        self.backend.clear_session(session_id)
    
    def get_all_sessions(self) -> List[str]:
        """
        获取所有会话
        
        Returns:
            List[str]: 会话ID列表
        """
        return self.backend.get_all_sessions()
    
    def delete_session(self, session_id: str) -> bool:
        """
        删除会话
        
        Args:
            session_id: 会话ID
        
        Returns:
            bool: 是否成功删除
        """
        return self.backend.delete_session(session_id)
    
    def set_summarization(self, enabled: bool, threshold: int = 5) -> None:
        """
        设置摘要配置
        
        Args:
            enabled: 是否启用摘要
            threshold: 摘要触发阈值
        """
        self._enable_summarization = enabled
        self._summarization_threshold = threshold
    
    def should_summarize(self, session_id: str) -> bool:
        """
        检查是否应该生成摘要
        
        Args:
            session_id: 会话ID
        
        Returns:
            bool: 是否应该生成摘要
        """
        if not self._enable_summarization:
            return False
        
        messages = self.get_messages(session_id)
        return len(messages) >= self._summarization_threshold


class MemoryBackendFactory:
    """记忆存储后端工厂"""
    
    @staticmethod
    def create_backend(
        backend_type: str,
        config: Dict[str, Any] = None
    ) -> BaseMemoryBackend:
        """
        创建记忆存储后端
        
        Args:
            backend_type: 后端类型（in_memory, redis, sqlite, postgresql）
            config: 后端配置
        
        Returns:
            BaseMemoryBackend: 记忆存储后端实例
        
        Raises:
            ValueError: 当后端类型不支持时
        """
        config = config or {}
        
        if backend_type == "in_memory":
            return InMemoryBackend(config)
        elif backend_type == "redis":
            return RedisBackend(config)
        elif backend_type == "sqlite":
            return SQLiteBackend(config)
        elif backend_type == "postgresql":
            # PostgreSQL后端需要额外实现
            raise NotImplementedError("PostgreSQL后端尚未实现")
        else:
            raise ValueError(f"不支持的后端类型: {backend_type}")
