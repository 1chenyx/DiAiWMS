from typing import List, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import Warehouse
from app.repositories.base_repository import BaseRepository


class WarehouseRepository(BaseRepository[Warehouse]):
    """
    仓库数据访问层
    """

    def __init__(self, db_session: AsyncSession):
        super().__init__(Warehouse, db_session)

    async def get_by_tenant(
        self,
        tenant_id: str,
        is_valid: Optional[bool] = None
    ) -> List[Warehouse]:
        """
        根据租户ID获取仓库列表
        
        Args:
            tenant_id: 租户ID
            is_valid: 是否有效
            
        Returns:
            仓库实例列表
        """
        query = select(Warehouse).where(Warehouse.tenant_id == tenant_id)
        
        if is_valid is not None:
            query = query.where(Warehouse.is_valid == is_valid)
        
        query = query.order_by(Warehouse.create_time.desc())
        
        result = await self._db_session.execute(query)
        return result.scalars().all()

    async def page_search_by_tenant(
        self,
        page_index: int,
        page_size: int,
        tenant_id: str,
        search_params: Optional[dict] = None
    ):
        """
        分页查询仓库列表（带租户过滤）
        
        Args:
            page_index: 页码，从1开始
            page_size: 每页数量
            tenant_id: 租户ID
            search_params: 搜索参数
            
        Returns:
            (仓库列表, 总数量)
        """
        query = select(Warehouse).where(Warehouse.tenant_id == tenant_id)
        
        if search_params:
            if "warehouse_name" in search_params:
                query = query.where(Warehouse.warehouse_name.like(f"%{search_params['warehouse_name']}%"))
            if "warehouse_code" in search_params:
                query = query.where(Warehouse.warehouse_code.like(f"%{search_params['warehouse_code']}%"))
            if "is_valid" in search_params:
                query = query.where(Warehouse.is_valid == search_params["is_valid"])
        
        total_query = select(func.count()).select_from(query.subquery())
        total_result = await self._db_session.execute(total_query)
        total = total_result.scalar()
        
        query = query.order_by(Warehouse.create_time.desc())
        query = query.offset((page_index - 1) * page_size).limit(page_size)
        
        result = await self._db_session.execute(query)
        data = result.scalars().all()
        
        return data, total
