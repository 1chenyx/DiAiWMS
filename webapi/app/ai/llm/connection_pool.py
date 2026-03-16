"""
LLM连接池管理器
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
from collections import OrderedDict
import asyncio
import hashlib
import json
from loguru import logger

from app.ai.llm.client import LLMClient, create_llm_client


class LLMConnectionInstance:
    """
    LLM连接实例
    
    封装LLM客户端及其完整配置信息
    """
    
    def __init__(
        self,
        client: LLMClient,
        config_id: int,
        provider_code: str,
        model_code: str,
        tools: List[Dict[str, Any]] = None,
        skills: List[Dict[str, Any]] = None,
        rules: List[Dict[str, Any]] = None
    ):
        self.client = client
        self.config_id = config_id
        self.provider_code = provider_code
        self.model_code = model_code
        self.tools = tools or []
        self.skills = skills or []
        self.rules = rules or []
        self.is_busy = False
        self.use_count = 0
        self.last_used_at = datetime.now()
        self.created_at = datetime.now()
        
        self._config_hash = self._compute_config_hash()
    
    def _compute_config_hash(self) -> str:
        """
        计算配置哈希值
        
        用于检测配置是否变化
        
        Returns:
            配置哈希值
        """
        config_data = {
            "tools": sorted([t.get("tool_code", "") for t in self.tools]),
            "skills": sorted([s.get("skill_name", "") for s in self.skills]),
            "rules": sorted([r.get("rule_name", "") for r in self.rules])
        }
        config_str = json.dumps(config_data, sort_keys=True)
        return hashlib.md5(config_str.encode()).hexdigest()
    
    def is_config_changed(
        self,
        tools: List[Dict[str, Any]],
        skills: List[Dict[str, Any]],
        rules: List[Dict[str, Any]]
    ) -> bool:
        """
        检查配置是否变化
        
        Args:
            tools: 新的工具列表
            skills: 新的技能列表
            rules: 新的规则列表
            
        Returns:
            是否变化
        """
        new_hash = self._compute_config_hash_for(tools, skills, rules)
        return new_hash != self._config_hash
    
    @staticmethod
    def _compute_config_hash_for(
        tools: List[Dict[str, Any]],
        skills: List[Dict[str, Any]],
        rules: List[Dict[str, Any]]
    ) -> str:
        """
        计算指定配置的哈希值
        
        Args:
            tools: 工具列表
            skills: 技能列表
            rules: 规则列表
            
        Returns:
            配置哈希值
        """
        config_data = {
            "tools": sorted([t.get("tool_code", "") for t in (tools or [])]),
            "skills": sorted([s.get("skill_name", "") for s in (skills or [])]),
            "rules": sorted([r.get("rule_name", "") for r in (rules or [])])
        }
        config_str = json.dumps(config_data, sort_keys=True)
        return hashlib.md5(config_str.encode()).hexdigest()
    
    def mark_used(self):
        """标记为已使用"""
        self.use_count += 1
        self.last_used_at = datetime.now()
    
    def mark_busy(self):
        """标记为忙碌"""
        self.is_busy = True
    
    def mark_idle(self):
        """标记为空闲"""
        self.is_busy = False
    
    def is_expired(self, max_idle_seconds: int) -> bool:
        """
        检查是否过期
        
        Args:
            max_idle_seconds: 最大空闲秒数
            
        Returns:
            是否过期
        """
        if self.is_busy:
            return False
        
        idle_time = (datetime.now() - self.last_used_at).total_seconds()
        return idle_time > max_idle_seconds


class TenantLLMPool:
    """
    租户LLM连接池
    
    管理单个租户的所有LLM连接实例
    """
    
    def __init__(self, tenant_id: str, max_connections: int = 10):
        self.tenant_id = tenant_id
        self.max_connections = max_connections
        self._connections: OrderedDict[int, LLMConnectionInstance] = OrderedDict()
        self._lock = asyncio.Lock()
    
    async def get_connection(
        self,
        config_id: int,
        tools: List[Dict[str, Any]] = None,
        skills: List[Dict[str, Any]] = None,
        rules: List[Dict[str, Any]] = None
    ) -> Optional[LLMConnectionInstance]:
        """
        获取LLM连接实例
        
        如果配置变化，返回None让调用方重新创建
        
        Args:
            config_id: 配置ID
            tools: 当前工具列表
            skills: 当前技能列表
            rules: 当前规则列表
            
        Returns:
            LLM连接实例或None
        """
        async with self._lock:
            if config_id in self._connections:
                instance = self._connections[config_id]
                
                if not instance.is_busy:
                    if instance.is_config_changed(tools, skills, rules):
                        self._connections.pop(config_id)
                        logger.info(f"配置已变化，清理连接: tenant={self.tenant_id}, config={config_id}")
                        return None
                    
                    instance.mark_busy()
                    instance.mark_used()
                    self._connections.move_to_end(config_id)
                    logger.debug(f"复用LLM连接: tenant={self.tenant_id}, config={config_id}, use_count={instance.use_count}")
                    return instance
            
            return None
    
    async def add_connection(self, config_id: int, instance: LLMConnectionInstance) -> bool:
        """
        添加LLM连接实例
        
        Args:
            config_id: 配置ID
            instance: LLM连接实例
            
        Returns:
            是否添加成功
        """
        async with self._lock:
            if len(self._connections) >= self.max_connections:
                evicted = await self._evict_lru()
                if not evicted:
                    return False
            
            instance.mark_busy()
            self._connections[config_id] = instance
            logger.info(f"创建新LLM连接: tenant={self.tenant_id}, config={config_id}")
            return True
    
    async def release_connection(self, config_id: int):
        """
        释放LLM连接实例
        
        Args:
            config_id: 配置ID
        """
        async with self._lock:
            if config_id in self._connections:
                self._connections[config_id].mark_idle()
                logger.debug(f"释放LLM连接: tenant={self.tenant_id}, config={config_id}")
    
    async def remove_connection(self, config_id: int) -> Optional[LLMConnectionInstance]:
        """
        移除LLM连接实例
        
        Args:
            config_id: 配置ID
            
        Returns:
            被移除的实例
        """
        async with self._lock:
            return self._connections.pop(config_id, None)
    
    async def clear_all(self):
        """清空所有连接"""
        async with self._lock:
            self._connections.clear()
    
    async def cleanup_expired(self, max_idle_seconds: int) -> int:
        """
        清理过期的连接
        
        Args:
            max_idle_seconds: 最大空闲秒数
            
        Returns:
            清理的数量
        """
        async with self._lock:
            expired_configs = [
                config_id for config_id, conn in self._connections.items()
                if conn.is_expired(max_idle_seconds)
            ]
            
            for config_id in expired_configs:
                self._connections.pop(config_id)
                logger.info(f"清理过期LLM连接: tenant={self.tenant_id}, config={config_id}")
            
            return len(expired_configs)
    
    async def _evict_lru(self) -> bool:
        """
        淘汰最近最少使用的连接
        
        Returns:
            是否成功淘汰
        """
        for config_id, conn in self._connections.items():
            if not conn.is_busy:
                self._connections.pop(config_id)
                logger.info(f"淘汰LRU连接: tenant={self.tenant_id}, config={config_id}")
                return True
        
        return False
    
    def get_stats(self) -> Dict[str, Any]:
        """
        获取统计信息
        
        Returns:
            统计信息
        """
        return {
            "tenant_id": self.tenant_id,
            "connection_count": len(self._connections),
            "max_connections": self.max_connections,
            "connections": [
                {
                    "config_id": config_id,
                    "provider_code": conn.provider_code,
                    "model_code": conn.model_code,
                    "tools_count": len(conn.tools),
                    "skills_count": len(conn.skills),
                    "rules_count": len(conn.rules),
                    "config_hash": conn._config_hash,
                    "is_busy": conn.is_busy,
                    "use_count": conn.use_count,
                    "last_used_at": conn.last_used_at.isoformat(),
                    "created_at": conn.created_at.isoformat()
                }
                for config_id, conn in self._connections.items()
            ]
        }


class LLMConnectionPool:
    """
    LLM连接池管理器
    
    管理所有租户的LLM连接实例池
    """
    
    MAX_CONNECTIONS_PER_TENANT = 10
    MAX_IDLE_SECONDS = 1800
    CLEANUP_INTERVAL = 300
    
    def __init__(self):
        self._tenant_pools: Dict[str, TenantLLMPool] = {}
        self._lock = asyncio.Lock()
        self._cleanup_task: Optional[asyncio.Task] = None
        self._is_running = False
    
    async def start_cleanup_task(self):
        """启动清理任务"""
        if self._is_running:
            return
        
        self._is_running = True
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        logger.info("LLM连接池清理任务已启动")
    
    async def stop_cleanup_task(self):
        """停止清理任务"""
        self._is_running = False
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        logger.info("LLM连接池清理任务已停止")
    
    async def get_client(
        self,
        tenant_id: str,
        config_id: int,
        provider_code: str,
        model_code: str,
        api_key: str,
        api_endpoint: Optional[str] = None,
        tools: List[Dict[str, Any]] = None,
        skills: List[Dict[str, Any]] = None,
        rules: List[Dict[str, Any]] = None
    ) -> tuple[LLMClient, bool]:
        """
        获取LLM客户端
        
        优先从池中获取已有的客户端，如果没有则创建新的
        
        Args:
            tenant_id: 租户ID
            config_id: 配置ID
            provider_code: 服务商代码
            model_code: 模型代码
            api_key: API密钥
            api_endpoint: API端点
            tools: 工具列表
            skills: 技能列表
            rules: 规则列表
            
        Returns:
            (LLM客户端, 是否新建)
        """
        async with self._lock:
            if tenant_id not in self._tenant_pools:
                self._tenant_pools[tenant_id] = TenantLLMPool(
                    tenant_id,
                    self.MAX_CONNECTIONS_PER_TENANT
                )
            
            pool = self._tenant_pools[tenant_id]
        
        instance = await pool.get_connection(config_id, tools, skills, rules)
        
        if instance:
            return instance.client, False
        
        client = create_llm_client(
            provider_code=provider_code,
            api_key=api_key,
            base_url=api_endpoint
        )
        
        instance = LLMConnectionInstance(
            client=client,
            config_id=config_id,
            provider_code=provider_code,
            model_code=model_code,
            tools=tools,
            skills=skills,
            rules=rules
        )
        
        success = await pool.add_connection(config_id, instance)
        
        if not success:
            logger.warning(f"LLM连接池已满，直接返回新客户端: tenant={tenant_id}")
        
        return client, True
    
    async def release_client(self, tenant_id: str, config_id: int):
        """
        释放LLM客户端
        
        Args:
            tenant_id: 租户ID
            config_id: 配置ID
        """
        try:
            async with self._lock:
                if tenant_id in self._tenant_pools:
                    pool = self._tenant_pools[tenant_id]
                    await pool.release_connection(config_id)
        except Exception as e:
            logger.error(f"释放LLM客户端失败: {e}")
    
    async def invalidate_config(
        self,
        tenant_id: str,
        config_id: Optional[int] = None,
        config_type: Optional[str] = None
    ):
        """
        使配置失效，清理对应连接
        
        Args:
            tenant_id: 租户ID
            config_id: 配置ID（可选，清理特定LLM配置）
            config_type: 配置类型（可选，"tool"/"skill"/"rule"，清理所有相关连接）
        """
        try:
            async with self._lock:
                if tenant_id not in self._tenant_pools:
                    return
                
                pool = self._tenant_pools[tenant_id]
                
                if config_id:
                    await pool.remove_connection(config_id)
                    logger.info(f"配置变更，清理连接: tenant={tenant_id}, config_id={config_id}")
                elif config_type:
                    await pool.clear_all()
                    logger.info(f"{config_type}配置变更，清理所有连接: tenant={tenant_id}")
                else:
                    await pool.clear_all()
                    logger.info(f"清理租户所有连接: tenant={tenant_id}")
        except Exception as e:
            logger.error(f"清理连接失败: {e}")
    
    async def clear_tenant_connections(
        self,
        tenant_id: str,
        config_id: Optional[int] = None
    ):
        """
        清理租户的连接
        
        Args:
            tenant_id: 租户ID
            config_id: 配置ID（可选，不传则清理所有）
        """
        await self.invalidate_config(tenant_id, config_id)
    
    async def cleanup_expired_connections(self):
        """清理过期的连接"""
        try:
            async with self._lock:
                total_cleaned = 0
                
                for tenant_id, pool in list(self._tenant_pools.items()):
                    cleaned = await pool.cleanup_expired(self.MAX_IDLE_SECONDS)
                    total_cleaned += cleaned
                
                if total_cleaned > 0:
                    logger.info(f"清理过期LLM连接: {total_cleaned}个")
        except Exception as e:
            logger.error(f"清理过期连接失败: {e}")
    
    def get_pool_stats(self) -> Dict[str, Any]:
        """
        获取池统计信息
        
        Returns:
            统计信息
        """
        return {
            "total_tenants": len(self._tenant_pools),
            "total_connections": sum(len(pool._connections) for pool in self._tenant_pools.values()),
            "tenants": {
                tenant_id: pool.get_stats()
                for tenant_id, pool in self._tenant_pools.items()
            }
        }
    
    async def _cleanup_loop(self):
        """清理循环"""
        while self._is_running:
            try:
                await asyncio.sleep(self.CLEANUP_INTERVAL)
                await self.cleanup_expired_connections()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"清理循环异常: {e}")


_llm_connection_pool: Optional[LLMConnectionPool] = None


def get_llm_connection_pool() -> LLMConnectionPool:
    """
    获取LLM连接池管理器单例
    
    Returns:
        LLM连接池管理器实例
    """
    global _llm_connection_pool
    
    if _llm_connection_pool is None:
        _llm_connection_pool = LLMConnectionPool()
    
    return _llm_connection_pool
