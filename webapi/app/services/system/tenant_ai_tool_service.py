from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.models.entities.system import TenantAITool
from app.repositories.system.tenant_ai_tool_repository import TenantAIToolRepository
from app.services.tenant_aware_service import TenantAwareService
from app.schemas.ai_config import (
    TenantAIToolViewModel,
    TenantAIToolCreateViewModel,
    TenantAIToolUpdateViewModel
)
from app.ai.config.config_loader import get_ai_config_loader
from app.utils.cache_manager import CacheManager
from app.core.current_user import CurrentUser
from loguru import logger


class TenantAIToolService(TenantAwareService[TenantAIToolRepository, TenantAITool]):
    """
    租户AI工具配置服务
    
    提供租户工具配置的管理功能
    """
    
    CACHE_KEY_PREFIX = "ai_tool"
    CACHE_EXPIRE_MINUTES = 60
    
    def __init__(self, db_session: AsyncSession):
        repository = TenantAIToolRepository(db_session)
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
    
    async def get_active_tools(self, tenant_id: str) -> List[TenantAIToolViewModel]:
        """
        获取租户激活的工具列表
        
        Args:
            tenant_id: 租户ID
            
        Returns:
            激活的工具列表
        """
        cache_key = self._get_cache_key(tenant_id)
        cached_tools = self._cache.get(cache_key)
        if cached_tools:
            return cached_tools
        
        result = await self._db_session.execute(
            select(TenantAITool).where(
                and_(
                    TenantAITool.tenant_id == tenant_id,
                    TenantAITool.is_active == True,
                    TenantAITool.is_valid == True
                )
            ).order_by(TenantAITool.tool_category, TenantAITool.tool_code)
        )
        tools = result.scalars().all()
        
        view_models = [await self._to_view_model(tool) for tool in tools]
        self._cache.set_absolute_expire(cache_key, view_models, self.CACHE_EXPIRE_MINUTES)
        
        return view_models
    
    async def get_tool_list(
        self,
        current_user: CurrentUser,
        category: str = None,
        page_index: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """
        获取工具配置列表
        
        Args:
            current_user: 当前用户
            category: 工具分类（可选）
            page_index: 页码
            page_size: 每页数量
            
        Returns:
            分页结果
        """
        filters = {"is_valid": True}
        if category:
            filters["tool_category"] = category
        
        tools, total = await self.page_query_by_tenant(
            page_index,
            page_size,
            current_user.tenant_id,
            filters,
            TenantAITool.last_update_time.desc()
        )
        
        view_models = [await self._to_view_model(tool) for tool in tools]
        
        return {
            "data": view_models,
            "totals": total,
            "page_index": page_index,
            "page_size": page_size
        }
    
    async def activate_tool(
        self,
        view_model: TenantAIToolCreateViewModel,
        current_user: CurrentUser
    ) -> tuple[int, str]:
        """
        激活工具
        
        Args:
            view_model: 创建视图模型
            current_user: 当前用户
            
        Returns:
            (工具ID, 错误消息)
        """
        try:
            system_tool = self._config_loader.get_tool(view_model.tool_code)
            if not system_tool:
                return 0, f"系统工具不存在: {view_model.tool_code}"
            
            existing = await self._db_session.execute(
                select(TenantAITool).where(
                    and_(
                        TenantAITool.tenant_id == current_user.tenant_id,
                        TenantAITool.tool_code == view_model.tool_code,
                        TenantAITool.is_valid == True
                    )
                )
            )
            existing_tool = existing.scalar_one_or_none()
            
            if existing_tool:
                existing_tool.is_active = True
                existing_tool.config = view_model.config
                existing_tool.description = view_model.description
                await self._db_session.commit()
                
                self._clear_cache(current_user.tenant_id)
                return existing_tool.id, ""
            
            tool = await self.create_with_tenant(
                tenant_id=current_user.tenant_id,
                tool_code=view_model.tool_code,
                tool_name=view_model.tool_name,
                tool_category=view_model.tool_category,
                is_active=True,
                config=view_model.config,
                description=view_model.description,
                is_valid=True,
                creator=current_user.user_name
            )
            
            self._clear_cache(current_user.tenant_id)
            
            return tool.id, ""
        except Exception as e:
            logger.error(f"激活工具失败: {e}")
            return 0, str(e)
    
    async def deactivate_tool(
        self,
        tool_id: int,
        current_user: CurrentUser
    ) -> tuple[bool, str]:
        """
        停用工具
        
        Args:
            tool_id: 工具ID
            current_user: 当前用户
            
        Returns:
            (是否成功, 错误消息)
        """
        try:
            tool = await self.get_by_id(tool_id)
            if tool is None or tool.tenant_id != current_user.tenant_id:
                return False, "工具不存在或无权限"
            
            tool.is_active = False
            await self._db_session.commit()
            
            self._clear_cache(current_user.tenant_id)
            
            return True, ""
        except Exception as e:
            logger.error(f"停用工具失败: {e}")
            return False, str(e)
    
    async def update_tool_config(
        self,
        tool_id: int,
        view_model: TenantAIToolUpdateViewModel,
        current_user: CurrentUser
    ) -> tuple[bool, str]:
        """
        更新工具配置
        
        Args:
            tool_id: 工具ID
            view_model: 更新视图模型
            current_user: 当前用户
            
        Returns:
            (是否成功, 错误消息)
        """
        try:
            tool = await self.get_by_id(tool_id)
            if tool is None or tool.tenant_id != current_user.tenant_id:
                return False, "工具不存在或无权限"
            
            update_data = {}
            if view_model.is_active is not None:
                update_data["is_active"] = view_model.is_active
            if view_model.config is not None:
                update_data["config"] = view_model.config
            if view_model.description is not None:
                update_data["description"] = view_model.description
            
            if update_data:
                await self.update_with_tenant(tool_id, current_user.tenant_id, **update_data)
            
            self._clear_cache(current_user.tenant_id)
            
            return True, ""
        except Exception as e:
            logger.error(f"更新工具配置失败: {e}")
            return False, str(e)
    
    async def _to_view_model(self, tool: TenantAITool) -> TenantAIToolViewModel:
        """
        转换为视图模型
        
        Args:
            tool: 工具实体
            
        Returns:
            工具视图模型
        """
        return TenantAIToolViewModel(
            id=tool.id,
            tenant_id=tool.tenant_id,
            tool_code=tool.tool_code,
            tool_name=tool.tool_name,
            tool_category=tool.tool_category,
            is_active=tool.is_active,
            config=tool.config,
            description=tool.description,
            is_valid=tool.is_valid,
            creator=tool.creator,
            create_time=tool.create_time,
            last_update_time=tool.last_update_time
        )
