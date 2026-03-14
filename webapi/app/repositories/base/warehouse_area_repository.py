from typing import List, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import WarehouseArea
from app.repositories.base_repository import BaseRepository


class WarehouseAreaRepository(BaseRepository[WarehouseArea]):
    """
    库区数据访问层
    """

    def __init__(self, db_session: AsyncSession):
        super().__init__(WarehouseArea, db_session)

    async def get_by_tenant(
        self,
        tenant_id: str,
        is_valid: Optional[bool] = None
    ) -> List[WarehouseArea]:
        """
        根据租户ID获取库区列表
        
        Args:
            tenant_id: 租户ID
            is_valid: 是否有效
            
        Returns:
            库区实例列表
        """
        query = select(WarehouseArea).where(WarehouseArea.tenant_id == tenant_id)
        
        if is_valid is not None:
            query = query.where(WarehouseArea.is_valid == is_valid)
        
        query = query.order_by(WarehouseArea.create_time.desc())
        
        result = await self._db_session.execute(query)
        return result.scalars().all()
