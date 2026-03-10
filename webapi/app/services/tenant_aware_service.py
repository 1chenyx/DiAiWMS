from typing import TypeVar, Generic, Optional, List, Dict, Any
from sqlalchemy import select

from app.services.base_service_core import BaseService, RepositoryType, ModelType


class TenantAwareService(BaseService[RepositoryType, ModelType]):
    """
    租户感知服务基类
    
    提供带租户过滤的业务逻辑处理方法
    """

    async def get_by_tenant(
        self,
        tenant_id: str,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[Any] = None,
        limit: Optional[int] = None
    ) -> List[ModelType]:
        """
        根据租户ID获取记录
        
        Args:
            tenant_id: 租户ID
            filters: 额外过滤条件
            order_by: 排序字段
            limit: 限制数量
            
        Returns:
            模型实例列表
        """
        if filters is None:
            filters = {}
        filters["tenant_id"] = tenant_id
        return await self._repository.get_all(filters, order_by, limit)

    async def count_by_tenant(
        self,
        tenant_id: str,
        filters: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        根据租户ID统计记录数量
        
        Args:
            tenant_id: 租户ID
            filters: 额外过滤条件
            
        Returns:
            记录数量
        """
        if filters is None:
            filters = {}
        filters["tenant_id"] = tenant_id
        return await self._repository.count(filters)

    async def page_query_by_tenant(
        self,
        page_index: int,
        page_size: int,
        tenant_id: str,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[Any] = None
    ) -> tuple[List[ModelType], int]:
        """
        分页查询（带租户过滤）
        
        Args:
            page_index: 页码，从1开始
            page_size: 每页数量
            tenant_id: 租户ID
            filters: 额外过滤条件
            order_by: 排序字段
            
        Returns:
            (记录列表, 总数量)
        """
        if filters is None:
            filters = {}
        filters["tenant_id"] = tenant_id
        return await self._repository.page_query(page_index, page_size, filters, order_by)

    async def create_with_tenant(
        self,
        tenant_id: str,
        **kwargs
    ) -> ModelType:
        """
        创建新记录（带租户ID）
        
        Args:
            tenant_id: 租户ID
            **kwargs: 模型字段值
            
        Returns:
            创建的模型实例
        """
        kwargs["tenant_id"] = tenant_id
        return await self._repository.create(**kwargs)

    async def update_with_tenant(
        self,
        id: int,
        tenant_id: str,
        **kwargs
    ) -> Optional[ModelType]:
        """
        更新记录（带租户ID验证）
        
        Args:
            id: 主键ID
            tenant_id: 租户ID
            **kwargs: 要更新的字段值
            
        Returns:
            更新后的模型实例，不存在或不属于该租户则返回None
        """
        entity = await self.get_by_id(id)
        if entity is None:
            return None
        
        if hasattr(entity, 'tenant_id') and entity.tenant_id != tenant_id:
            return None
        
        kwargs["tenant_id"] = tenant_id
        return await self._repository.update(id, **kwargs)

    async def query_by_tenant(
        self,
        tenant_id: str,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[Any] = None,
        limit: Optional[int] = None
    ) -> List[ModelType]:
        """
        根据租户ID查询记录（通用查询方法）
        
        Args:
            tenant_id: 租户ID
            filters: 额外过滤条件
            order_by: 排序字段
            limit: 限制数量
            
        Returns:
            模型实例列表
        """
        model = self._repository._model
        query = select(model).where(model.tenant_id == tenant_id)
        
        if filters:
            for key, value in filters.items():
                if hasattr(model, key):
                    query = query.where(getattr(model, key) == value)
        
        if order_by is not None:
            if isinstance(order_by, (list, tuple)):
                query = query.order_by(*order_by)
            else:
                query = query.order_by(order_by)
        
        if limit is not None:
            query = query.limit(limit)
        
        result = await self._repository._db_session.execute(query)
        return result.scalars().all()

    async def get_one_by_tenant(
        self,
        tenant_id: str,
        filters: Optional[Dict[str, Any]] = None
    ) -> Optional[ModelType]:
        """
        根据租户ID和条件查询单条记录
        
        Args:
            tenant_id: 租户ID
            filters: 额外过滤条件
            
        Returns:
            模型实例，不存在则返回None
        """
        model = self._repository._model
        query = select(model).where(model.tenant_id == tenant_id)
        
        if filters:
            for key, value in filters.items():
                if hasattr(model, key):
                    query = query.where(getattr(model, key) == value)
        
        result = await self._repository._db_session.execute(query)
        return result.scalar_one_or_none()

    async def query_entity_by_tenant(
        self,
        entity_class: Any,
        tenant_id: str,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[Any] = None,
        limit: Optional[int] = None
    ) -> List[Any]:
        """
        查询任意实体（带租户过滤）
        
        Args:
            entity_class: 实体类
            tenant_id: 租户ID
            filters: 额外过滤条件
            order_by: 排序字段
            limit: 限制数量
            
        Returns:
            实体实例列表
        """
        query = select(entity_class).where(entity_class.tenant_id == tenant_id)
        
        if filters:
            for key, value in filters.items():
                if hasattr(entity_class, key):
                    query = query.where(getattr(entity_class, key) == value)
        
        if order_by is not None:
            if isinstance(order_by, (list, tuple)):
                query = query.order_by(*order_by)
            else:
                query = query.order_by(order_by)
        
        if limit is not None:
            query = query.limit(limit)
        
        result = await self._repository._db_session.execute(query)
        return result.scalars().all()

    async def get_one_entity_by_tenant(
        self,
        entity_class: Any,
        tenant_id: str,
        filters: Optional[Dict[str, Any]] = None
    ) -> Optional[Any]:
        """
        查询单个实体（带租户过滤）
        
        Args:
            entity_class: 实体类
            tenant_id: 租户ID
            filters: 额外过滤条件
            
        Returns:
            实体实例，不存在则返回None
        """
        query = select(entity_class).where(entity_class.tenant_id == tenant_id)
        
        if filters:
            for key, value in filters.items():
                if hasattr(entity_class, key):
                    query = query.where(getattr(entity_class, key) == value)
        
        result = await self._repository._db_session.execute(query)
        return result.scalar_one_or_none()