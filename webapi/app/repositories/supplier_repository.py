from typing import List, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities.supplier import Supplier
from app.repositories.base_repository import BaseRepository


class SupplierRepository(BaseRepository[Supplier]):
    """
    供应商数据访问层
    """

    def __init__(self, db_session: AsyncSession):
        super().__init__(Supplier, db_session)

    async def search_by_tenant(
        self,
        page_index: int,
        page_size: int,
        tenant_id: str,
        search_params: Optional[dict] = None
    ):
        """
        根据租户ID搜索供应商
        
        Args:
            page_index: 页码，从1开始
            page_size: 每页数量
            tenant_id: 租户ID
            search_params: 搜索参数
            
        Returns:
            (供应商列表, 总数量)
        """
        query = select(Supplier).where(Supplier.tenant_id == tenant_id)
        
        if search_params:
            if "supplier_name" in search_params:
                query = query.where(Supplier.supplier_name.like(f"%{search_params['supplier_name']}%"))
            if "is_valid" in search_params:
                query = query.where(Supplier.is_valid == search_params["is_valid"])
        
        total_query = select(func.count()).select_from(query.subquery())
        total_result = await self._db_session.execute(total_query)
        total = total_result.scalar()
        
        query = query.order_by(Supplier.create_time.desc())
        query = query.offset((page_index - 1) * page_size).limit(page_size)
        
        result = await self._db_session.execute(query)
        data = result.scalars().all()
        
        return data, total
