from typing import List, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import FreightFee
from app.repositories.base_repository import BaseRepository


class FreightFeeRepository(BaseRepository[FreightFee]):
    """
    运费数据访问层
    """

    def __init__(self, db_session: AsyncSession):
        super().__init__(FreightFee, db_session)

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
        query = select(FreightFee).where(FreightFee.tenant_id == tenant_id)
        
        if search_params:
            if "fee_name" in search_params:
                query = query.where(FreightFee.fee_name.like(f"%{search_params['fee_name']}%"))
        
        total_query = select(func.count()).select_from(query.subquery())
        total_result = await self._db_session.execute(total_query)
        total = total_result.scalar()
        
        query = query.order_by(FreightFee.create_time.desc())
        query = query.offset((page_index - 1) * page_size).limit(page_size)
        
        result = await self._db_session.execute(query)
        data = result.scalars().all()
        
        return data, total
