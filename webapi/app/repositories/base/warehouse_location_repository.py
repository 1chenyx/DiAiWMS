from typing import List, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import WarehouseLocation
from app.repositories.base_repository import BaseRepository


class WarehouseLocationRepository(BaseRepository[WarehouseLocation]):
    """
    库位数据访问层
    """

    def __init__(self, db_session: AsyncSession):
        super().__init__(WarehouseLocation, db_session)

    async def get_by_tenant(
        self,
        tenant_id: str,
        is_valid: Optional[bool] = None
    ) -> List[WarehouseLocation]:
        """
        根据租户ID获取库位列表
        
        Args:
            tenant_id: 租户ID
            is_valid: 是否有效
            
        Returns:
            库位实例列表
        """
        query = select(WarehouseLocation).where(WarehouseLocation.tenant_id == tenant_id)
        
        if is_valid is not None:
            query = query.where(WarehouseLocation.is_valid == is_valid)
        
        query = query.order_by(WarehouseLocation.create_time.desc())
        
        result = await self._db_session.execute(query)
        return result.scalars().all()
