from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from app.models.entities.tenant_ai_config import TenantAIConfig
from app.schemas.ai_config import (
    TenantAIConfigViewModel,
    TenantAIConfigCreateViewModel,
    TenantAIConfigUpdateViewModel
)
from app.ai.config_loader import get_ai_config_loader
from app.utils.cache_manager import CacheManager


class TenantAIConfigService:
    """
    租户AI配置服务
    """
    
    CACHE_KEY_PREFIX = "ai_default_config"
    CACHE_EXPIRE_MINUTES = 60
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.config_loader = get_ai_config_loader()
        self.cache = CacheManager()
    
    def _get_cache_key(self, tenant_id: str) -> str:
        """
        获取缓存key
        
        Args:
            tenant_id: 租户ID
            
        Returns:
            缓存key
        """
        return f"{self.CACHE_KEY_PREFIX}_{tenant_id}"
    
    def _clear_cache(self, tenant_id: str):
        """
        清理缓存
        
        Args:
            tenant_id: 租户ID
        """
        cache_key = self._get_cache_key(tenant_id)
        self.cache.remove(cache_key)
    
    def _set_cache(self, tenant_id: str, config: TenantAIConfigViewModel):
        """
        设置缓存
        
        Args:
            tenant_id: 租户ID
            config: 配置视图模型
        """
        cache_key = self._get_cache_key(tenant_id)
        self.cache.set_sliding_expire(
            cache_key,
            config,
            self.CACHE_EXPIRE_MINUTES
        )
    
    def _get_cache(self, tenant_id: str) -> Optional[TenantAIConfigViewModel]:
        """
        获取缓存
        
        Args:
            tenant_id: 租户ID
            
        Returns:
            配置视图模型
        """
        cache_key = self._get_cache_key(tenant_id)
        return self.cache.get(cache_key)
    
    async def get_by_id(self, config_id: int) -> Optional[TenantAIConfigViewModel]:
        """
        根据ID获取配置
        
        Args:
            config_id: 配置ID
            
        Returns:
            配置视图模型
        """
        result = await self.db.execute(
            select(TenantAIConfig).where(TenantAIConfig.id == config_id)
        )
        config = result.scalar_one_or_none()
        
        if config is None:
            return None
        
        return await self._to_view_model(config)
    
    async def get_list(
        self,
        tenant_id: str,
        provider_code: Optional[str] = None,
        is_default: Optional[bool] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """
        获取配置列表
        
        Args:
            tenant_id: 租户ID
            provider_code: 提供商代码
            is_default: 是否默认配置
            page: 页码
            page_size: 每页数量
            
        Returns:
            分页结果
        """
        conditions = [
            TenantAIConfig.tenant_id == tenant_id,
            TenantAIConfig.is_valid == True
        ]
        
        if provider_code:
            conditions.append(TenantAIConfig.provider_code == provider_code)
        
        if is_default is not None:
            conditions.append(TenantAIConfig.is_default == is_default)
        
        query = select(TenantAIConfig).where(and_(*conditions))
        
        total_result = await self.db.execute(
            select(TenantAIConfig.id).where(and_(*conditions))
        )
        total = len(total_result.scalars().all())
        
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        
        result = await self.db.execute(query)
        configs = result.scalars().all()
        
        view_models = []
        for config in configs:
            view_model = await self._to_view_model(config)
            view_models.append(view_model)
        
        return {
            'total': total,
            'page': page,
            'page_size': page_size,
            'items': view_models
        }
    
    async def get_default(self, tenant_id: str) -> Optional[TenantAIConfigViewModel]:
        """
        获取默认配置
        
        Args:
            tenant_id: 租户ID
            
        Returns:
            默认配置视图模型
        """
        cached_config = self._get_cache(tenant_id)
        if cached_config:
            return cached_config
        
        result = await self.db.execute(
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
        self._set_cache(tenant_id, view_model)
        
        return view_model
    
    async def create(
        self,
        view_model: TenantAIConfigCreateViewModel,
        tenant_id: str,
        creator: str
    ) -> Optional[TenantAIConfigViewModel]:
        """
        创建配置
        
        Args:
            view_model: 创建视图模型
            tenant_id: 租户ID
            creator: 创建人
            
        Returns:
            配置视图模型
        """
        current_time = int(__import__('time').time() * 1000)
        
        config = TenantAIConfig(
            provider_code=view_model.provider_code,
            model_code=view_model.model_code,
            api_key=view_model.api_key,
            api_endpoint=view_model.api_endpoint,
            is_default=view_model.is_default,
            tenant_id=tenant_id,
            creator=creator,
            create_time=current_time,
            last_update_time=current_time,
            is_valid=True
        )
        
        self.db.add(config)
        await self.db.flush()
        
        result = await self.db.execute(
            select(TenantAIConfig).where(
                and_(
                    TenantAIConfig.tenant_id == tenant_id,
                    TenantAIConfig.is_valid == True
                )
            )
        )
        all_configs = result.scalars().all()
        
        if len(all_configs) == 1:
            config.is_default = True
        elif view_model.is_default:
            result = await self.db.execute(
                select(TenantAIConfig).where(
                    and_(
                        TenantAIConfig.tenant_id == tenant_id,
                        TenantAIConfig.is_default == True,
                        TenantAIConfig.id != config.id,
                        TenantAIConfig.is_valid == True
                    )
                )
            )
            other_defaults = result.scalars().all()
            
            for other_config in other_defaults:
                other_config.is_default = False
        
        await self.db.commit()
        await self.db.refresh(config)
        
        view_model = await self._to_view_model(config)
        
        if config.is_default:
            self._set_cache(tenant_id, view_model)
        
        return view_model
    
    async def update(
        self,
        config_id: int,
        view_model: TenantAIConfigUpdateViewModel
    ) -> Optional[TenantAIConfigViewModel]:
        """
        更新配置
        
        Args:
            config_id: 配置ID
            view_model: 更新视图模型
            
        Returns:
            配置视图模型
        """
        result = await self.db.execute(
            select(TenantAIConfig).where(TenantAIConfig.id == config_id)
        )
        config = result.scalar_one_or_none()
        
        if config is None:
            return None
        
        current_time = int(__import__('time').time() * 1000)
        
        was_default = config.is_default
        
        if view_model.api_key is not None:
            config.api_key = view_model.api_key
        if view_model.api_endpoint is not None:
            config.api_endpoint = view_model.api_endpoint
        if view_model.is_default is not None:
            if view_model.is_default and not config.is_default:
                result = await self.db.execute(
                    select(TenantAIConfig).where(
                        and_(
                            TenantAIConfig.tenant_id == config.tenant_id,
                            TenantAIConfig.is_default == True,
                            TenantAIConfig.id != config_id,
                            TenantAIConfig.is_valid == True
                        )
                    )
                )
                other_defaults = result.scalars().all()
                
                for other_config in other_defaults:
                    other_config.is_default = False
            
            config.is_default = view_model.is_default
        
        config.last_update_time = current_time
        
        await self.db.commit()
        await self.db.refresh(config)
        
        view_model = await self._to_view_model(config)
        
        if was_default or config.is_default:
            self._clear_cache(config.tenant_id)
            if config.is_default:
                self._set_cache(config.tenant_id, view_model)
        
        return view_model
    
    async def delete(self, config_id: int) -> bool:
        """
        删除配置（软删除）
        
        Args:
            config_id: 配置ID
            
        Returns:
            是否成功
        """
        result = await self.db.execute(
            select(TenantAIConfig).where(TenantAIConfig.id == config_id)
        )
        config = result.scalar_one_or_none()
        
        if config is None:
            return False
        
        tenant_id = config.tenant_id
        was_default = config.is_default
        
        config.is_valid = False
        config.last_update_time = int(__import__('time').time() * 1000)
        
        await self.db.commit()
        
        if was_default:
            self._clear_cache(tenant_id)
        
        return True
    
    async def set_default(self, config_id: int) -> Optional[TenantAIConfigViewModel]:
        """
        设置为默认配置
        
        Args:
            config_id: 配置ID
            
        Returns:
            配置视图模型
        """
        result = await self.db.execute(
            select(TenantAIConfig).where(TenantAIConfig.id == config_id)
        )
        config = result.scalar_one_or_none()
        
        if config is None:
            return None
        
        if not config.is_valid:
            return None
        
        result = await self.db.execute(
            select(TenantAIConfig).where(
                and_(
                    TenantAIConfig.tenant_id == config.tenant_id,
                    TenantAIConfig.is_default == True,
                    TenantAIConfig.id != config_id,
                    TenantAIConfig.is_valid == True
                )
            )
        )
        other_defaults = result.scalars().all()
        
        for other_config in other_defaults:
            other_config.is_default = False
        
        config.is_default = True
        config.last_update_time = int(__import__('time').time() * 1000)
        
        await self.db.commit()
        await self.db.refresh(config)
        
        view_model = await self._to_view_model(config)
        self._set_cache(config.tenant_id, view_model)
        
        return view_model
    
    async def _to_view_model(self, config: TenantAIConfig) -> TenantAIConfigViewModel:
        """
        转换为视图模型
        
        Args:
            config: 配置实体
            
        Returns:
            配置视图模型
        """
        provider = self.config_loader.get_provider(config.provider_code)
        model = self.config_loader.get_model(config.provider_code, config.model_code)
        
        return TenantAIConfigViewModel(
            id=config.id,
            provider_code=config.provider_code,
            provider_name=provider.get('name', '') if provider else '',
            model_code=config.model_code,
            model_name=model.get('name', '') if model else '',
            api_key=config.api_key,
            api_endpoint=config.api_endpoint,
            is_default=config.is_default,
            tenant_id=config.tenant_id,
            creator=config.creator,
            create_time=config.create_time,
            last_update_time=config.last_update_time,
            is_valid=config.is_valid
        )
