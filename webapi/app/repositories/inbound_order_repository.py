from typing import List, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import InboundOrder
from app.repositories.base_repository import BaseRepository


class InboundOrderRepository(BaseRepository[InboundOrder]):
    """
    入库单数据访问层
    """

    def __init__(self, db_session: AsyncSession):
        super().__init__(InboundOrder, db_session)

    async def search_by_tenant(
        self,
        page_index: int,
        page_size: int,
        tenant_id: str,
        search_params: Optional[dict] = None
    ):
        """
        根据租户ID搜索入库单
        
        Args:
            page_index: 页码，从1开始
            page_size: 每页数量
            tenant_id: 租户ID
            search_params: 搜索参数
            
        Returns:
            (入库单列表, 总数量)
        """
        query = select(InboundOrder).where(InboundOrder.tenant_id == tenant_id)
        
        if search_params:
            if "inbound_order_code" in search_params:
                query = query.where(InboundOrder.inbound_order_code.like(f"%{search_params['inbound_order_code']}%"))
            if "supplier_id" in search_params:
                query = query.where(InboundOrder.supplier_id == search_params["supplier_id"])
            if "order_status" in search_params:
                query = query.where(InboundOrder.order_status == search_params["order_status"])
        
        total_query = select(func.count()).select_from(query.subquery())
        total_result = await self._db_session.execute(total_query)
        total = total_result.scalar()
        
        query = query.order_by(InboundOrder.create_time.desc())
        query = query.offset((page_index - 1) * page_size).limit(page_size)
        
        result = await self._db_session.execute(query)
        data = result.scalars().all()
        
        return data, total
