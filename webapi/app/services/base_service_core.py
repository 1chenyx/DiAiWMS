from typing import TypeVar, Generic, Optional, List, Dict, Any

from app.repositories.base_repository import BaseRepository
from app.models.base import WMSBaseModel

RepositoryType = TypeVar("RepositoryType", bound=BaseRepository)
ModelType = TypeVar("ModelType", bound=WMSBaseModel)


class BaseService(Generic[RepositoryType, ModelType]):
    """
    基础服务类
    
    提供通用的业务逻辑处理方法
    """

    def __init__(self, repository: RepositoryType):
        """
        初始化服务
        
        Args:
            repository: 仓储实例
        """
        self._repository = repository

    async def get_by_id(self, id: int) -> Optional[ModelType]:
        """
        根据ID获取记录
        
        Args:
            id: 主键ID
            
        Returns:
            模型实例，不存在则返回None
        """
        return await self._repository.get_by_id(id)

    async def get_all(
        self,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[Any] = None,
        limit: Optional[int] = None
    ) -> List[ModelType]:
        """
        获取所有记录
        
        Args:
            filters: 过滤条件
            order_by: 排序字段
            limit: 限制数量
            
        Returns:
            模型实例列表
        """
        return await self._repository.get_all(filters, order_by, limit)

    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        统计记录数量
        
        Args:
            filters: 过滤条件
            
        Returns:
            记录数量
        """
        return await self._repository.count(filters)

    async def exists(self, id: int) -> bool:
        """
        检查记录是否存在
        
        Args:
            id: 主键ID
            
        Returns:
            存在返回True，否则返回False
        """
        return await self._repository.exists(id)

    async def create(self, **kwargs) -> ModelType:
        """
        创建新记录
        
        Args:
            **kwargs: 模型字段值
            
        Returns:
            创建的模型实例
        """
        return await self._repository.create(**kwargs)

    async def update(self, id: int, **kwargs) -> Optional[ModelType]:
        """
        更新记录
        
        Args:
            id: 主键ID
            **kwargs: 要更新的字段值
            
        Returns:
            更新后的模型实例，不存在则返回None
        """
        return await self._repository.update(id, **kwargs)

    async def delete(self, id: int) -> bool:
        """
        删除记录
        
        Args:
            id: 主键ID
            
        Returns:
            删除成功返回True，记录不存在返回False
        """
        return await self._repository.delete(id)

    async def bulk_create(self, instances: List[ModelType]) -> List[ModelType]:
        """
        批量创建记录
        
        Args:
            instances: 模型实例列表
            
        Returns:
            创建的模型实例列表
        """
        return await self._repository.bulk_create(instances)

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
        return await self._repository.bulk_update(ids, update_data)

    async def bulk_delete(self, ids: List[int]) -> int:
        """
        批量删除记录
        
        Args:
            ids: 主键ID列表
            
        Returns:
            删除的记录数量
        """
        return await self._repository.bulk_delete(ids)

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
            filters: 过滤条件
            order_by: 排序字段
            
        Returns:
            (记录列表, 总数量)
        """
        return await self._repository.page_query(page_index, page_size, filters, order_by)