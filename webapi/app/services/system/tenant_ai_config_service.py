from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.models.entities.system import TenantAIConfig
from app.repositories.system.tenant_ai_config_repository import TenantAIConfigRepository
from app.services.tenant_aware_service import TenantAwareService
from app.schemas.ai_config import (
    TenantAIConfigViewModel,
    TenantAIConfigCreateViewModel,
    TenantAIConfigUpdateViewModel
)
from app.ai.config.config_loader import get_ai_config_loader
from app.utils.cache_manager import CacheManager
from app.core.current_user import CurrentUser
from loguru import logger


class TenantAIConfigService(TenantAwareService[TenantAIConfigRepository, TenantAIConfig]):
    """
    租户AI配置服务
    
    提供租户LLM配置的管理功能
    """
    
    CACHE_KEY_PREFIX = "ai_config"
    CACHE_EXPIRE_MINUTES = 60
    
    def __init__(self, db_session: AsyncSession):
        repository = TenantAIConfigRepository(db_session)
        super().__init__(repository)
        self._db_session = db_session
        self._config_loader = get_ai_config_loader()
        self._cache = CacheManager()
    
    def _get_cache_key(self, tenant_id: str, config_id: int = None) -> str:
        """
        获取缓存key
        
        Args:
            tenant_id: 租户ID
            config_id: 配置ID（可选）
            
        Returns:
            缓存key
        """
        if config_id:
            return f"ModernWMS:{tenant_id}:{self.CACHE_KEY_PREFIX}:{config_id}"
        return f"ModernWMS:{tenant_id}:{self.CACHE_KEY_PREFIX}:default"
    
    def _clear_cache(self, tenant_id: str, config_id: int = None):
        """
        清理缓存
        
        Args:
            tenant_id: 租户ID
            config_id: 配置ID（可选）
        """
        cache_key = self._get_cache_key(tenant_id, config_id)
        self._cache.remove(cache_key)
        
        if config_id is None:
            default_key = self._get_cache_key(tenant_id)
            self._cache.remove(default_key)
    
    async def get_default_config(self, tenant_id: str) -> Optional[TenantAIConfigViewModel]:
        """
        获取租户默认配置
        
        Args:
            tenant_id: 租户ID
            
        Returns:
            默认配置视图模型
        """
        cache_key = self._get_cache_key(tenant_id)
        cached_config = self._cache.get(cache_key)
        if cached_config:
            return cached_config
        
        result = await self._db_session.execute(
            select(TenantAIConfig).where(
                and_(
                    TenantAIConfig.tenant_id == tenant_id,
                    TenantAIConfig.is_default == True,
                    TenantAIConfig.is_valid == True
                )
            )
        )
        config = result.scalar_one_or_none()
        
        if config is None:
            return None
        
        view_model = await self._to_view_model(config)
        self._cache.set_absolute_expire(cache_key, view_model, self.CACHE_EXPIRE_MINUTES)
        
        return view_model
    
    async def get_config_by_id(
        self,
        config_id: int,
        current_user: CurrentUser
    ) -> Optional[TenantAIConfigViewModel]:
        """
        根据ID获取配置
        
        Args:
            config_id: 配置ID
            current_user: 当前用户
            
        Returns:
            配置视图模型
        """
        cache_key = self._get_cache_key(current_user.tenant_id, config_id)
        cached_config = self._cache.get(cache_key)
        if cached_config:
            return cached_config
        
        config = await self.get_by_id(config_id)
        if config is None or config.tenant_id != current_user.tenant_id:
            return None
        
        view_model = await self._to_view_model(config)
        self._cache.set_absolute_expire(cache_key, view_model, self.CACHE_EXPIRE_MINUTES)
        
        return view_model
    
    async def get_config_list(
        self,
        current_user: CurrentUser,
        provider_code: str = None,
        page_index: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """
        获取配置列表
        
        Args:
            current_user: 当前用户
            provider_code: 服务商代码（可选）
            page_index: 页码
            page_size: 每页数量
            
        Returns:
            分页结果
        """
        filters = {"is_valid": True}
        if provider_code:
            filters["provider_code"] = provider_code
        
        configs, total = await self.page_query_by_tenant(
            page_index,
            page_size,
            current_user.tenant_id,
            filters,
            TenantAIConfig.last_update_time.desc()
        )
        
        view_models = []
        for config in configs:
            view_model = await self._to_view_model(config)
            view_models.append(view_model)
        
        return {
            "data": view_models,
            "totals": total,
            "page_index": page_index,
            "page_size": page_size
        }
    
    async def create_config(
        self,
        view_model: TenantAIConfigCreateViewModel,
        current_user: CurrentUser
    ) -> tuple[int, str]:
        """
        创建配置
        
        Args:
            view_model: 创建视图模型
            current_user: 当前用户
            
        Returns:
            (配置ID, 错误消息)
        """
        try:
            provider = self._config_loader.get_provider(view_model.provider_code)
            if not provider:
                return 0, f"服务商不存在: {view_model.provider_code}"
            
            model = self._config_loader.get_model(view_model.provider_code, view_model.model_code)
            if not model:
                return 0, f"模型不存在: {view_model.model_code}"
            
            config = await self.create_with_tenant(
                tenant_id=current_user.tenant_id,
                provider_code=view_model.provider_code,
                model_code=view_model.model_code,
                api_key=view_model.api_key,
                api_endpoint=view_model.api_endpoint or provider.get("api_base", ""),
                is_default=view_model.is_default,
                temperature=view_model.temperature,
                max_tokens=view_model.max_tokens,
                is_valid=True,
                creator=current_user.user_name
            )
            
            if view_model.is_default:
                await self._set_as_default(config.id, current_user.tenant_id)
            
            self._clear_cache(current_user.tenant_id)
            
            return config.id, ""
        except Exception as e:
            logger.error(f"创建AI配置失败: {e}")
            return 0, str(e)
    
    async def update_config(
        self,
        config_id: int,
        view_model: TenantAIConfigUpdateViewModel,
        current_user: CurrentUser
    ) -> tuple[bool, str]:
        """
        更新配置
        
        Args:
            config_id: 配置ID
            view_model: 更新视图模型
            current_user: 当前用户
            
        Returns:
            (是否成功, 错误消息)
        """
        try:
            config = await self.get_by_id(config_id)
            if config is None or config.tenant_id != current_user.tenant_id:
                return False, "配置不存在或无权限"
            
            update_data = {}
            if view_model.api_key is not None:
                update_data["api_key"] = view_model.api_key
            if view_model.api_endpoint is not None:
                update_data["api_endpoint"] = view_model.api_endpoint
            if view_model.temperature is not None:
                update_data["temperature"] = view_model.temperature
            if view_model.max_tokens is not None:
                update_data["max_tokens"] = view_model.max_tokens
            
            if view_model.is_default is not None and view_model.is_default:
                await self._set_as_default(config_id, current_user.tenant_id)
                update_data["is_default"] = True
            
            if update_data:
                await self.update_with_tenant(config_id, current_user.tenant_id, **update_data)
            
            self._clear_cache(current_user.tenant_id, config_id)
            
            return True, ""
        except Exception as e:
            logger.error(f"更新AI配置失败: {e}")
            return False, str(e)
    
    async def delete_config(
        self,
        config_id: int,
        current_user: CurrentUser
    ) -> tuple[bool, str]:
        """
        删除配置（软删除）
        
        Args:
            config_id: 配置ID
            current_user: 当前用户
            
        Returns:
            (是否成功, 错误消息)
        """
        try:
            config = await self.get_by_id(config_id)
            if config is None or config.tenant_id != current_user.tenant_id:
                return False, "配置不存在或无权限"
            
            await self.update_with_tenant(
                config_id,
                current_user.tenant_id,
                is_valid=False
            )
            
            self._clear_cache(current_user.tenant_id, config_id)
            
            return True, ""
        except Exception as e:
            logger.error(f"删除AI配置失败: {e}")
            return False, str(e)
    
    async def set_as_default(
        self,
        config_id: int,
        current_user: CurrentUser
    ) -> tuple[bool, str]:
        """
        设置为默认配置
        
        Args:
            config_id: 配置ID
            current_user: 当前用户
            
        Returns:
            (是否成功, 错误消息)
        """
        try:
            config = await self.get_by_id(config_id)
            if config is None or config.tenant_id != current_user.tenant_id:
                return False, "配置不存在或无权限"
            
            if not config.is_valid:
                return False, "配置已失效"
            
            await self._set_as_default(config_id, current_user.tenant_id)
            
            self._clear_cache(current_user.tenant_id)
            
            return True, ""
        except Exception as e:
            logger.error(f"设置默认配置失败: {e}")
            return False, str(e)
    
    async def _set_as_default(self, config_id: int, tenant_id: str):
        """
        设置为默认配置（内部方法）
        
        Args:
            config_id: 配置ID
            tenant_id: 租户ID
        """
        result = await self._db_session.execute(
            select(TenantAIConfig).where(
                and_(
                    TenantAIConfig.tenant_id == tenant_id,
                    TenantAIConfig.is_default == True,
                    TenantAIConfig.id != config_id,
                    TenantAIConfig.is_valid == True
                )
            )
        )
        other_defaults = result.scalars().all()
        
        for other_config in other_defaults:
            other_config.is_default = False
        
        config = await self.get_by_id(config_id)
        if config:
            config.is_default = True
        
        await self._db_session.commit()
    
    async def _to_view_model(self, config: TenantAIConfig) -> TenantAIConfigViewModel:
        """
        转换为视图模型
        
        Args:
            config: 配置实体
            
        Returns:
            配置视图模型
        """
        provider = self._config_loader.get_provider(config.provider_code)
        model = self._config_loader.get_model(config.provider_code, config.model_code)
        
        return TenantAIConfigViewModel(
            id=config.id,
            tenant_id=config.tenant_id,
            provider_code=config.provider_code,
            provider_name=provider.get("name", "") if provider else config.provider_code,
            model_code=config.model_code,
            model_name=model.get("name", "") if model else config.model_code,
            api_key=config.api_key,
            api_endpoint=config.api_endpoint,
            is_default=config.is_default,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
            is_valid=config.is_valid,
            creator=config.creator,
            create_time=config.create_time,
            last_update_time=config.last_update_time
        )
