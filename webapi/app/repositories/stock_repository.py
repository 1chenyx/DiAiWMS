from typing import List, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import Stock
from app.repositories.base_repository import BaseRepository


class StockRepository(BaseRepository[Stock]):
    """
    库存数据访问层
    """

    def __init__(self, db_session: AsyncSession):
        super().__init__(Stock, db_session)

    async def get_by_tenant(
        self,
        tenant_id: str,
        is_valid: Optional[bool] = None
    ) -> List[Stock]:
        """
        根据租户ID获取库存列表
        
        Args:
            tenant_id: 租户ID
            is_valid: 是否有效
            
        Returns:
            库存实例列表
        """
        query = select(Stock).where(Stock.tenant_id == tenant_id)
        
        if is_valid is not None:
            query = query.where(Stock.is_valid == is_valid)
        
        query = query.order_by(Stock.create_time.desc())
        
        result = await self._db_session.execute(query)
        return result.scalars().all()

    async def search_by_tenant(
        self,
        page_index: int,
        page_size: int,
        tenant_id: str,
        search_params: Optional[dict] = None
    ):
        """
        根据租户ID搜索库存
        
        Args:
            page_index: 页码，从1开始
            page_size: 每页数量
            tenant_id: 租户ID
            search_params: 搜索参数
            
        Returns:
            (库存列表, 总数量)
        """
        query = select(Stock).where(Stock.tenant_id == tenant_id)
        
        if search_params:
            if "sku_code" in search_params:
                query = query.where(Stock.sku_code.like(f"%{search_params['sku_code']}%"))
            if "spu_code" in search_params:
                query = query.where(Stock.spu_code.like(f"%{search_params['spu_code']}%"))
            if "warehouse_id" in search_params:
                query = query.where(Stock.warehouse_id == search_params["warehouse_id"])
            if "is_valid" in search_params:
                query = query.where(Stock.is_valid == search_params["is_valid"])
        
        total_query = select(func.count()).select_from(query.subquery())
        total_result = await self._db_session.execute(total_query)
        total = total_result.scalar()
        
        query = query.order_by(Stock.create_time.desc())
        query = query.offset((page_index - 1) * page_size).limit(page_size)
        
        result = await self._db_session.execute(query)
        data = result.scalars().all()
        
        return data, total
