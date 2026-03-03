from typing import TypeVar, Generic, Type, Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy import select, func, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeMeta

from app.models.base import WMSBaseModel

ModelType = TypeVar("ModelType", bound=WMSBaseModel)


class BaseRepository(Generic[ModelType]):
    """
    基础仓储类
    
    提供通用的数据库操作方法，包括增删改查等基础功能
    """

    def __init__(self, model: Type[ModelType], db_session: AsyncSession):
        """
        初始化仓储
        
        Args:
            model: 模型类
            db_session: 数据库会话
        """
        self._model = model
        self._db_session = db_session

    async def get_by_id(self, id: int) -> Optional[ModelType]:
        """
        根据ID获取单条记录
        
        Args:
            id: 主键ID
            
        Returns:
            模型实例，不存在则返回None
        """
        query = select(self._model).where(self._model.id == id)
        result = await self._db_session.execute(query)
        return result.scalar_one_or_none()

    async def get_all(
        self,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[Any] = None,
        limit: Optional[int] = None
    ) -> List[ModelType]:
        """
        获取所有记录
        
        Args:
            filters: 过滤条件字典
            order_by: 排序字段
            limit: 限制数量
            
        Returns:
            模型实例列表
        """
        query = select(self._model)
        
        if filters:
            for key, value in filters.items():
                if hasattr(self._model, key):
                    if isinstance(value, (list, tuple)):
                        query = query.where(getattr(self._model, key).in_(value))
                    else:
                        query = query.where(getattr(self._model, key) == value)
        
        if order_by is not None:
            query = query.order_by(order_by)
        
        if limit is not None:
            query = query.limit(limit)
        
        result = await self._db_session.execute(query)
        return result.scalars().all()

    async def get_by_field(
        self,
        field_name: str,
        field_value: Any
    ) -> Optional[ModelType]:
        """
        根据字段获取单条记录
        
        Args:
            field_name: 字段名
            field_value: 字段值
            
        Returns:
            模型实例，不存在则返回None
        """
        if not hasattr(self._model, field_name):
            return None
        
        query = select(self._model).where(getattr(self._model, field_name) == field_value)
        result = await self._db_session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_fields(
        self,
        filters: Dict[str, Any]
    ) -> List[ModelType]:
        """
        根据多个字段条件获取记录
        
        Args:
            filters: 过滤条件字典
            
        Returns:
            模型实例列表
        """
        query = select(self._model)
        
        for key, value in filters.items():
            if hasattr(self._model, key):
                query = query.where(getattr(self._model, key) == value)
        
        result = await self._db_session.execute(query)
        return result.scalars().all()

    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        统计记录数量
        
        Args:
            filters: 过滤条件字典
            
        Returns:
            记录数量
        """
        query = select(func.count()).select_from(self._model)
        
        if filters:
            for key, value in filters.items():
                if hasattr(self._model, key):
                    if isinstance(value, (list, tuple)):
                        query = query.where(getattr(self._model, key).in_(value))
                    else:
                        query = query.where(getattr(self._model, key) == value)
        
        result = await self._db_session.execute(query)
        return result.scalar()

    async def exists(self, id: int) -> bool:
        """
        检查记录是否存在
        
        Args:
            id: 主键ID
            
        Returns:
            存在返回True，否则返回False
        """
        query = select(func.count()).select_from(self._model).where(self._model.id == id)
        result = await self._db_session.execute(query)
        return result.scalar() > 0

    async def exists_by_field(self, field_name: str, field_value: Any) -> bool:
        """
        根据字段检查记录是否存在
        
        Args:
            field_name: 字段名
            field_value: 字段值
            
        Returns:
            存在返回True，否则返回False
        """
        if not hasattr(self._model, field_name):
            return False
        
        query = select(func.count()).select_from(self._model).where(
            getattr(self._model, field_name) == field_value
        )
        result = await self._db_session.execute(query)
        return result.scalar() > 0

    async def create(self, **kwargs) -> ModelType:
        """
        创建新记录
        
        Args:
            **kwargs: 模型字段值
            
        Returns:
            创建的模型实例
        """
        instance = self._model(**kwargs)
        self._db_session.add(instance)
        await self._db_session.commit()
        await self._db_session.refresh(instance)
        return instance

    async def update(self, id: int, **kwargs) -> Optional[ModelType]:
        """
        更新记录
        
        Args:
            id: 主键ID
            **kwargs: 要更新的字段值
            
        Returns:
            更新后的模型实例，不存在则返回None
        """
        instance = await self.get_by_id(id)
        if not instance:
            return None
        
        for key, value in kwargs.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        
        instance.last_update_time = int(datetime.now().timestamp())
        await self._db_session.commit()
        await self._db_session.refresh(instance)
        return instance

    async def delete(self, id: int) -> bool:
        """
        删除记录
        
        Args:
            id: 主键ID
            
        Returns:
            删除成功返回True，记录不存在返回False
        """
        instance = await self.get_by_id(id)
        if not instance:
            return False
        
        await self._db_session.delete(instance)
        await self._db_session.commit()
        return True

    async def bulk_create(self, instances: List[ModelType]) -> List[ModelType]:
        """
        批量创建记录
        
        Args:
            instances: 模型实例列表
            
        Returns:
            创建的模型实例列表
        """
        self._db_session.add_all(instances)
        await self._db_session.commit()
        for instance in instances:
            await self._db_session.refresh(instance)
        return instances

    async def bulk_update(
        self,
        ids: List[int],
        update_data: Dict[str, Any]
    ) -> int:
        """
        批量更新记录
        
        Args:
            ids: 主键ID列表
            update_data: 要更新的字段数据
            
        Returns:
            更新的记录数量
        """
        if not ids:
            return 0
        
        update_data["last_update_time"] = int(datetime.now().timestamp())
        query = update(self._model).where(self._model.id.in_(ids)).values(**update_data)
        result = await self._db_session.execute(query)
        await self._db_session.commit()
        return result.rowcount

    async def bulk_delete(self, ids: List[int]) -> int:
        """
        批量删除记录
        
        Args:
            ids: 主键ID列表
            
        Returns:
            删除的记录数量
        """
        if not ids:
            return 0
        
        query = delete(self._model).where(self._model.id.in_(ids))
        result = await self._db_session.execute(query)
        await self._db_session.commit()
        return result.rowcount

    async def page_query(
        self,
        page_index: int,
        page_size: int,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[Any] = None
    ) -> tuple[List[ModelType], int]:
        """
        分页查询
        
        Args:
            page_index: 页码，从1开始
            page_size: 每页数量
            filters: 过滤条件字典
            order_by: 排序字段
            
        Returns:
            (记录列表, 总数量)
        """
        query = select(self._model)
        
        if filters:
            for key, value in filters.items():
                if hasattr(self._model, key):
                    if isinstance(value, str) and "%" in value:
                        query = query.where(getattr(self._model, key).like(value))
                    elif isinstance(value, (list, tuple)):
                        query = query.where(getattr(self._model, key).in_(value))
                    else:
                        query = query.where(getattr(self._model, key) == value)
        
        total_query = select(func.count()).select_from(query.subquery())
        total_result = await self._db_session.execute(total_query)
        total = total_result.scalar()
        
        if order_by is not None:
            query = query.order_by(order_by)
        
        query = query.offset((page_index - 1) * page_size).limit(page_size)
        
        result = await self._db_session.execute(query)
        data = result.scalars().all()
        
        return data, total
