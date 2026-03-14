from typing import List, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import Sku
from app.repositories.base_repository import BaseRepository


class SkuRepository(BaseRepository[Sku]):
    """
    SKU数据访问层
    """

    def __init__(self, db_session: AsyncSession):
        super().__init__(Sku, db_session)

    async def get_by_spu_id(
        self,
        spu_id: int
    ) -> List[Sku]:
        """
        根据SPU ID获取SKU列表
        
        Args:
            spu_id: SPU ID
            
        Returns:
            SKU实例列表
        """
        query = select(Sku).where(Sku.spu_id == spu_id)
        query = query.order_by(Sku.create_time.desc())
        
        result = await self._db_session.execute(query)
        return result.scalars().all()

    async def get_by_tenant(
        self,
        tenant_id: str,
        is_valid: Optional[bool] = None
    ) -> List[Sku]:
        """
        根据租户ID获取SKU列表
        
        Args:
            tenant_id: 租户ID
            is_valid: 是否有效
            
        Returns:
            SKU实例列表
        """
        query = select(Sku).where(Sku.tenant_id == tenant_id)
        
        if is_valid is not None:
            query = query.where(Sku.is_valid == is_valid)
        
        query = query.order_by(Sku.create_time.desc())
        
        result = await self._db_session.execute(query)
        return result.scalars().all()
