from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from collections import OrderedDict
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.services.system.tenant_ai_config_service import TenantAIConfigService
from app.services.system.tenant_ai_tool_service import TenantAIToolService
from app.services.system.tenant_ai_skill_service import TenantAISkillService
from app.services.system.tenant_ai_rule_service import TenantAIRuleService


class AgentInstance:
    """
    Agent实例包装类
    
    封装Agent实例及其元数据
    """
    
    def __init__(self, agent: Any, config_id: int, config_version: str):
        self.agent = agent
        self.config_id = config_id
        self.config_version = config_version
        self.is_busy = False
        self.use_count = 0
        self.last_used_at = datetime.now()
        self.created_at = datetime.now()
    
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


class TenantAgentPool:
    """
    租户Agent池
    
    管理单个租户的所有Agent实例
    """
    
    def __init__(self, tenant_id: str, max_agents: int = 10):
        self.tenant_id = tenant_id
        self.max_agents = max_agents
        self._agents: OrderedDict[int, AgentInstance] = OrderedDict()
        self._lock = asyncio.Lock()
    
    async def get_agent(self, config_id: int) -> Optional[AgentInstance]:
        """
        获取Agent实例
        
        Args:
            config_id: 配置ID
            
        Returns:
            Agent实例或None
        """
        async with self._lock:
            if config_id in self._agents:
                agent_instance = self._agents[config_id]
                
                if not agent_instance.is_busy:
                    agent_instance.mark_busy()
                    agent_instance.mark_used()
                    self._agents.move_to_end(config_id)
                    return agent_instance
            
            return None
    
    async def add_agent(self, config_id: int, agent_instance: AgentInstance) -> bool:
        """
        添加Agent实例
        
        Args:
            config_id: 配置ID
            agent_instance: Agent实例
            
        Returns:
            是否添加成功
        """
        async with self._lock:
            if len(self._agents) >= self.max_agents:
                evicted = await self._evict_lru()
                if not evicted:
                    return False
            
            agent_instance.mark_busy()
            self._agents[config_id] = agent_instance
            return True
    
    async def release_agent(self, config_id: int):
        """
        释放Agent实例
        
        Args:
            config_id: 配置ID
        """
        async with self._lock:
            if config_id in self._agents:
                self._agents[config_id].mark_idle()
    
    async def remove_agent(self, config_id: int) -> Optional[AgentInstance]:
        """
        移除Agent实例
        
        Args:
            config_id: 配置ID
            
        Returns:
            被移除的Agent实例
        """
        async with self._lock:
            return self._agents.pop(config_id, None)
    
    async def clear_all(self):
        """清空所有Agent实例"""
        async with self._lock:
            self._agents.clear()
    
    async def cleanup_expired(self, max_idle_seconds: int) -> int:
        """
        清理过期的Agent实例
        
        Args:
            max_idle_seconds: 最大空闲秒数
            
        Returns:
            清理的数量
        """
        async with self._lock:
            expired_configs = [
                config_id for config_id, agent in self._agents.items()
                if agent.is_expired(max_idle_seconds)
            ]
            
            for config_id in expired_configs:
                self._agents.pop(config_id, None)
            
            return len(expired_configs)
    
    async def _evict_lru(self) -> bool:
        """
        淘汰最近最少使用的Agent
        
        Returns:
            是否成功淘汰
        """
        for config_id, agent in self._agents.items():
            if not agent.is_busy:
                self._agents.pop(config_id)
                logger.info(f"Evicted LRU agent for tenant {self.tenant_id}, config {config_id}")
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
            "agent_count": len(self._agents),
            "max_agents": self.max_agents,
            "agents": [
                {
                    "config_id": config_id,
                    "is_busy": agent.is_busy,
                    "use_count": agent.use_count,
                    "last_used_at": agent.last_used_at.isoformat(),
                    "created_at": agent.created_at.isoformat()
                }
                for config_id, agent in self._agents.items()
            ]
        }


class AgentPoolManager:
    """
    Agent池管理器
    
    管理所有租户的Agent实例池
    """
    
    MAX_AGENTS_PER_TENANT = 10
    MAX_IDLE_SECONDS = 1800
    CLEANUP_INTERVAL = 300
    
    def __init__(self):
        self._tenant_pools: Dict[str, TenantAgentPool] = {}
        self._lock = asyncio.Lock()
        self._cleanup_task: Optional[asyncio.Task] = None
        self._is_running = False
    
    async def start_cleanup_task(self):
        """启动清理任务"""
        if self._is_running:
            return
        
        self._is_running = True
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        logger.info("Agent pool cleanup task started")
    
    async def stop_cleanup_task(self):
        """停止清理任务"""
        self._is_running = False
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        logger.info("Agent pool cleanup task stopped")
    
    async def get_agent(
        self,
        tenant_id: str,
        config_id: Optional[int],
        db: AsyncSession
    ) -> tuple[Optional[Dict[str, Any]], str]:
        """
        获取Agent实例
        
        Args:
            tenant_id: 租户ID
            config_id: 配置ID（可选）
            db: 数据库会话
            
        Returns:
            (Agent信息字典, 错误消息)
        """
        try:
            async with self._lock:
                if tenant_id not in self._tenant_pools:
                    self._tenant_pools[tenant_id] = TenantAgentPool(
                        tenant_id,
                        self.MAX_AGENTS_PER_TENANT
                    )
                
                pool = self._tenant_pools[tenant_id]
            
            if config_id is None:
                config_service = TenantAIConfigService(db)
                default_config = await config_service.get_default_config(tenant_id)
                
                if default_config is None:
                    return None, "租户未配置默认LLM配置"
                
                config_id = default_config.id
            
            agent_instance = await pool.get_agent(config_id)
            
            if agent_instance:
                logger.info(f"Reused existing agent for tenant {tenant_id}, config {config_id}")
                return self._build_agent_info(agent_instance), ""
            
            agent, error = await self._create_agent(tenant_id, config_id, db)
            
            if error:
                return None, error
            
            agent_instance = AgentInstance(
                agent=agent,
                config_id=config_id,
                config_version=datetime.now().isoformat()
            )
            
            success = await pool.add_agent(config_id, agent_instance)
            
            if not success:
                return None, "Agent池已满，无法创建新Agent"
            
            logger.info(f"Created new agent for tenant {tenant_id}, config {config_id}")
            return self._build_agent_info(agent_instance), ""
            
        except Exception as e:
            logger.error(f"获取Agent失败: {e}")
            return None, str(e)
    
    async def release_agent(self, tenant_id: str, config_id: int):
        """
        释放Agent实例
        
        Args:
            tenant_id: 租户ID
            config_id: 配置ID
        """
        try:
            async with self._lock:
                if tenant_id in self._tenant_pools:
                    pool = self._tenant_pools[tenant_id]
                    await pool.release_agent(config_id)
                    logger.info(f"Released agent for tenant {tenant_id}, config {config_id}")
        except Exception as e:
            logger.error(f"释放Agent失败: {e}")
    
    async def clear_tenant_agents(
        self,
        tenant_id: str,
        config_id: Optional[int] = None
    ):
        """
        清理租户的Agent实例
        
        Args:
            tenant_id: 租户ID
            config_id: 配置ID（可选，不传则清理所有）
        """
        try:
            async with self._lock:
                if tenant_id not in self._tenant_pools:
                    return
                
                pool = self._tenant_pools[tenant_id]
                
                if config_id:
                    await pool.remove_agent(config_id)
                    logger.info(f"Cleared agent for tenant {tenant_id}, config {config_id}")
                else:
                    await pool.clear_all()
                    del self._tenant_pools[tenant_id]
                    logger.info(f"Cleared all agents for tenant {tenant_id}")
        except Exception as e:
            logger.error(f"清理Agent失败: {e}")
    
    async def cleanup_expired_agents(self):
        """清理过期的Agent实例"""
        try:
            async with self._lock:
                total_cleaned = 0
                
                for tenant_id, pool in list(self._tenant_pools.items()):
                    cleaned = await pool.cleanup_expired(self.MAX_IDLE_SECONDS)
                    total_cleaned += cleaned
                    
                    if cleaned > 0:
                        logger.info(f"Cleaned {cleaned} expired agents for tenant {tenant_id}")
                
                if total_cleaned > 0:
                    logger.info(f"Total cleaned {total_cleaned} expired agents")
        except Exception as e:
            logger.error(f"清理过期Agent失败: {e}")
    
    def get_pool_stats(self) -> Dict[str, Any]:
        """
        获取池统计信息
        
        Returns:
            统计信息
        """
        return {
            "total_tenants": len(self._tenant_pools),
            "total_agents": sum(len(pool._agents) for pool in self._tenant_pools.values()),
            "tenants": {
                tenant_id: pool.get_stats()
                for tenant_id, pool in self._tenant_pools.items()
            }
        }
    
    async def _create_agent(
        self,
        tenant_id: str,
        config_id: int,
        db: AsyncSession
    ) -> tuple[Dict[str, Any], str]:
        """
        创建Agent实例
        
        Args:
            tenant_id: 租户ID
            config_id: 配置ID
            db: 数据库会话
            
        Returns:
            (Agent配置字典, 错误消息)
        """
        try:
            config_service = TenantAIConfigService(db)
            config = await config_service.get_by_id(config_id)
            
            if config is None or config.tenant_id != tenant_id:
                return {}, "配置不存在或无权限"
            
            tool_service = TenantAIToolService(db)
            tools = await tool_service.get_active_tools(tenant_id)
            
            skill_service = TenantAISkillService(db)
            skills = await skill_service.get_active_skills(tenant_id)
            
            rule_service = TenantAIRuleService(db)
            rules = await rule_service.get_active_rules(tenant_id)
            
            agent_config = {
                "config_id": config_id,
                "provider_code": config.provider_code,
                "model_code": config.model_code,
                "api_endpoint": config.api_endpoint,
                "temperature": config.temperature,
                "max_tokens": config.max_tokens,
                "tools": [tool.dict() for tool in tools],
                "skills": [skill.dict() for skill in skills],
                "rules": [rule.dict() for rule in rules]
            }
            
            return agent_config, ""
            
        except Exception as e:
            logger.error(f"创建Agent失败: {e}")
            return {}, str(e)
    
    def _build_agent_info(self, agent_instance: AgentInstance) -> Dict[str, Any]:
        """
        构建Agent信息
        
        Args:
            agent_instance: Agent实例
            
        Returns:
            Agent信息字典
        """
        return {
            "config_id": agent_instance.config_id,
            "config_version": agent_instance.config_version,
            "use_count": agent_instance.use_count,
            "created_at": agent_instance.created_at.isoformat(),
            "last_used_at": agent_instance.last_used_at.isoformat(),
            **agent_instance.agent
        }
    
    async def _cleanup_loop(self):
        """清理循环"""
        while self._is_running:
            try:
                await asyncio.sleep(self.CLEANUP_INTERVAL)
                await self.cleanup_expired_agents()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"清理循环异常: {e}")


_agent_pool_manager: Optional[AgentPoolManager] = None


def get_agent_pool_manager() -> AgentPoolManager:
    """
    获取Agent池管理器单例
    
    Returns:
        Agent池管理器实例
    """
    global _agent_pool_manager
    
    if _agent_pool_manager is None:
        _agent_pool_manager = AgentPoolManager()
    
    return _agent_pool_manager
