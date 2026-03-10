from typing import List, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities.freightfee import Freightfee
from app.repositories.base_repository import BaseRepository


class FreightFeeRepository(BaseRepository[Freightfee]):
    """
    运费数据访问层
    """

    def __init__(self, db_session: AsyncSession):
        super().__init__(Freightfee, db_session)

    async def search_by_tenant(
        self,
        page_index: int,
        page_size: int,
        tenant_id: str,
        search_params: Optional[dict] = None
    ):
        """
        根据租户ID搜索运费
        
        Args:
            page_index: 页码，从1开始
            page_size: 每页数量
            tenant_id: 租户ID
            search_params: 搜索参数
            
        Returns:
            (运费列表, 总数量)
        """
        query = select(Freightfee).where(Freightfee.tenant_id == tenant_id)
        
        if search_params:
            if "fee_name" in search_params:
                query = query.where(Freightfee.fee_name.like(f"%{search_params['fee_name']}%"))
            if "carrier" in search_params:
                if isinstance(search_params["carrier"], str) and "%" in search_params["carrier"]:
                    query = query.where(Freightfee.carrier.like(search_params["carrier"]))
                else:
                    query = query.where(Freightfee.carrier == search_params["carrier"])
            if "departure_city" in search_params:
                if isinstance(search_params["departure_city"], str) and "%" in search_params["departure_city"]:
                    query = query.where(Freightfee.departure_city.like(search_params["departure_city"]))
                else:
                    query = query.where(Freightfee.departure_city == search_params["departure_city"])
            if "arrival_city" in search_params:
                if isinstance(search_params["arrival_city"], str) and "%" in search_params["arrival_city"]:
                    query = query.where(Freightfee.arrival_city.like(search_params["arrival_city"]))
                else:
                    query = query.where(Freightfee.arrival_city == search_params["arrival_city"])
        
        total_query = select(func.count()).select_from(query.subquery())
        total_result = await self._db_session.execute(total_query)
        total = total_result.scalar()
        
        query = query.order_by(Freightfee.create_time.desc())
        query = query.offset((page_index - 1) * page_size).limit(page_size)
        
        result = await self._db_session.execute(query)
        data = result.scalars().all()
        
        return data, total
