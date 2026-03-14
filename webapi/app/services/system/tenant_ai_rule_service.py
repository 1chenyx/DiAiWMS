from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.models.entities.system import TenantAIRule
from app.repositories.system.tenant_ai_rule_repository import TenantAIRuleRepository
from app.services.tenant_aware_service import TenantAwareService
from app.schemas.ai_config import (
    TenantAIRuleViewModel,
    TenantAIRuleCreateViewModel,
    TenantAIRuleUpdateViewModel
)
from app.ai.config.config_loader import get_ai_config_loader
from app.utils.cache_manager import CacheManager
from app.core.current_user import CurrentUser
from loguru import logger


class TenantAIRuleService(TenantAwareService[TenantAIRuleRepository, TenantAIRule]):
    """
    租户AI规则配置服务
    
    提供租户规则配置的管理功能
    """
    
    CACHE_KEY_PREFIX = "ai_rule"
    CACHE_EXPIRE_MINUTES = 60
    
    def __init__(self, db_session: AsyncSession):
        repository = TenantAIRuleRepository(db_session)
        super().__init__(repository)
        self._db_session = db_session
        self._config_loader = get_ai_config_loader()
        self._cache = CacheManager()
    
    def _get_cache_key(self, tenant_id: str) -> str:
        """
        获取缓存key
        
        Args:
            tenant_id: 租户ID
            
        Returns:
            缓存key
        """
        return f"ModernWMS:{tenant_id}:{self.CACHE_KEY_PREFIX}:list"
    
    def _clear_cache(self, tenant_id: str):
        """
        清理缓存
        
        Args:
            tenant_id: 租户ID
        """
        cache_key = self._get_cache_key(tenant_id)
        self._cache.remove(cache_key)
    
    async def get_active_rules(self, tenant_id: str) -> List[TenantAIRuleViewModel]:
        """
        获取租户激活的规则列表（包括系统规则和租户自定义规则）
        
        Args:
            tenant_id: 租户ID
            
        Returns:
            激活的规则列表
        """
        cache_key = self._get_cache_key(tenant_id)
        cached_rules = self._cache.get(cache_key)
        if cached_rules:
            return cached_rules
        
        system_rules = self._config_loader.get_active_rules()
        
        result = await self._db_session.execute(
            select(TenantAIRule).where(
                and_(
                    TenantAIRule.tenant_id == tenant_id,
                    TenantAIRule.is_active == True,
                    TenantAIRule.is_valid == True
                )
            ).order_by(TenantAIRule.priority.desc())
        )
        tenant_rules = result.scalars().all()
        
        all_rules = []
        
        for system_rule in system_rules:
            all_rules.append(TenantAIRuleViewModel(
                id=0,
                tenant_id=tenant_id,
                rule_name=system_rule.get("name", ""),
                rule_category=system_rule.get("category", ""),
                priority=system_rule.get("priority", 0),
                content=system_rule.get("content", ""),
                description=system_rule.get("description", ""),
                is_active=True,
                is_system=True,
                is_valid=True,
                creator="system",
                create_time=0,
                last_update_time=0
            ))
        
        for tenant_rule in tenant_rules:
            all_rules.append(await self._to_view_model(tenant_rule))
        
        all_rules.sort(key=lambda x: x.priority, reverse=True)
        
        self._cache.set_absolute_expire(cache_key, all_rules, self.CACHE_EXPIRE_MINUTES)
        
        return all_rules
    
    async def get_rule_by_id(
        self,
        rule_id: int,
        current_user: CurrentUser
    ) -> Optional[TenantAIRuleViewModel]:
        """
        根据ID获取规则
        
        Args:
            rule_id: 规则ID
            current_user: 当前用户
            
        Returns:
            规则视图模型
        """
        rule = await self.get_by_id(rule_id)
        if rule is None or rule.tenant_id != current_user.tenant_id:
            return None
        
        return await self._to_view_model(rule)
    
    async def get_rule_list(
        self,
        current_user: CurrentUser,
        category: str = None,
        page_index: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """
        获取规则配置列表
        
        Args:
            current_user: 当前用户
            category: 规则类别（可选）
            page_index: 页码
            page_size: 每页数量
            
        Returns:
            分页结果
        """
        filters = {"is_valid": True}
        if category:
            filters["rule_category"] = category
        
        rules, total = await self.page_query_by_tenant(
            page_index,
            page_size,
            current_user.tenant_id,
            filters,
            TenantAIRule.priority.desc()
        )
        
        view_models = [await self._to_view_model(rule) for rule in rules]
        
        return {
            "data": view_models,
            "totals": total,
            "page_index": page_index,
            "page_size": page_size
        }
    
    async def create_rule(
        self,
        view_model: TenantAIRuleCreateViewModel,
        current_user: CurrentUser
    ) -> tuple[int, str]:
        """
        创建规则
        
        Args:
            view_model: 创建视图模型
            current_user: 当前用户
            
        Returns:
            (规则ID, 错误消息)
        """
        try:
            rule = await self.create_with_tenant(
                tenant_id=current_user.tenant_id,
                rule_name=view_model.rule_name,
                rule_category=view_model.rule_category,
                priority=view_model.priority,
                content=view_model.content,
                description=view_model.description,
                is_active=view_model.is_active,
                is_system=False,
                is_valid=True,
                creator=current_user.user_name
            )
            
            self._clear_cache(current_user.tenant_id)
            
            return rule.id, ""
        except Exception as e:
            logger.error(f"创建规则失败: {e}")
            return 0, str(e)
    
    async def update_rule(
        self,
        rule_id: int,
        view_model: TenantAIRuleUpdateViewModel,
        current_user: CurrentUser
    ) -> tuple[bool, str]:
        """
        更新规则
        
        Args:
            rule_id: 规则ID
            view_model: 更新视图模型
            current_user: 当前用户
            
        Returns:
            (是否成功, 错误消息)
        """
        try:
            rule = await self.get_by_id(rule_id)
            if rule is None or rule.tenant_id != current_user.tenant_id:
                return False, "规则不存在或无权限"
            
            if rule.is_system:
                return False, "系统规则不能修改"
            
            update_data = {}
            if view_model.rule_name is not None:
                update_data["rule_name"] = view_model.rule_name
            if view_model.rule_category is not None:
                update_data["rule_category"] = view_model.rule_category
            if view_model.priority is not None:
                update_data["priority"] = view_model.priority
            if view_model.content is not None:
                update_data["content"] = view_model.content
            if view_model.description is not None:
                update_data["description"] = view_model.description
            if view_model.is_active is not None:
                update_data["is_active"] = view_model.is_active
            
            if update_data:
                await self.update_with_tenant(rule_id, current_user.tenant_id, **update_data)
            
            self._clear_cache(current_user.tenant_id)
            
            return True, ""
        except Exception as e:
            logger.error(f"更新规则失败: {e}")
            return False, str(e)
    
    async def delete_rule(
        self,
        rule_id: int,
        current_user: CurrentUser
    ) -> tuple[bool, str]:
        """
        删除规则（软删除）
        
        Args:
            rule_id: 规则ID
            current_user: 当前用户
            
        Returns:
            (是否成功, 错误消息)
        """
        try:
            rule = await self.get_by_id(rule_id)
            if rule is None or rule.tenant_id != current_user.tenant_id:
                return False, "规则不存在或无权限"
            
            if rule.is_system:
                return False, "系统规则不能删除"
            
            await self.update_with_tenant(
                rule_id,
                current_user.tenant_id,
                is_valid=False
            )
            
            self._clear_cache(current_user.tenant_id)
            
            return True, ""
        except Exception as e:
            logger.error(f"删除规则失败: {e}")
            return False, str(e)
    
    async def _to_view_model(self, rule: TenantAIRule) -> TenantAIRuleViewModel:
        """
        转换为视图模型
        
        Args:
            rule: 规则实体
            
        Returns:
            规则视图模型
        """
        return TenantAIRuleViewModel(
            id=rule.id,
            tenant_id=rule.tenant_id,
            rule_name=rule.rule_name,
            rule_category=rule.rule_category,
            priority=rule.priority,
            content=rule.content,
            description=rule.description,
            is_active=rule.is_active,
            is_system=rule.is_system,
            is_valid=rule.is_valid,
            creator=rule.creator,
            create_time=rule.create_time,
            last_update_time=rule.last_update_time
        )
