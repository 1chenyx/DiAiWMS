from typing import List, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import GoodsLocation
from app.repositories.base_repository import BaseRepository


class GoodsLocationRepository(BaseRepository[GoodsLocation]):
    """
    货位数据访问层
    """

    def __init__(self, db_session: AsyncSession):
        super().__init__(GoodsLocation, db_session)

    async def get_by_tenant(
        self,
        tenant_id: str,
        is_valid: Optional[bool] = None
    ) -> List[GoodsLocation]:
        """
        根据租户ID获取货位列表
        
        Args:
            tenant_id: 租户ID
            is_valid: 是否有效
            
        Returns:
            货位实例列表
        """
        query = select(GoodsLocation).where(GoodsLocation.tenant_id == tenant_id)
        
        if is_valid is not None:
            query = query.where(GoodsLocation.is_valid == is_valid)
        
        query = query.order_by(GoodsLocation.create_time.desc())
        
        result = await self._db_session.execute(query)
        return result.scalars().all()
