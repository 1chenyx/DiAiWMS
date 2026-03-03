from typing import List, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import InboundPickPutaway
from app.repositories.base_repository import BaseRepository


class InboundPickPutawayRepository(BaseRepository[InboundPickPutaway]):
    """
    入库拣货上架数据访问层
    """

    def __init__(self, db_session: AsyncSession):
        super().__init__(InboundPickPutaway, db_session)

    async def search_by_tenant(
        self,
        page_index: int,
        page_size: int,
        tenant_id: str,
        search_params: Optional[dict] = None
    ):
        """
        根据租户ID搜索入库拣货上架
        
        Args:
            page_index: 页码，从1开始
            page_size: 每页数量
            tenant_id: 租户ID
            search_params: 搜索参数
            
        Returns:
            (入库拣货上架列表, 总数量)
        """
        query = select(InboundPickPutaway).where(InboundPickPutaway.tenant_id == tenant_id)
        
        if search_params:
            if "pick_putaway_code" in search_params:
                query = query.where(InboundPickPutaway.pick_putaway_code.like(f"%{search_params['pick_putaway_code']}%"))
        
        total_query = select(func.count()).select_from(query.subquery())
        total_result = await self._db_session.execute(total_query)
        total = total_result.scalar()
        
        query = query.order_by(InboundPickPutaway.create_time.desc())
        query = query.offset((page_index - 1) * page_size).limit(page_size)
        
        result = await self._db_session.execute(query)
        data = result.scalars().all()
        
        return data, total
