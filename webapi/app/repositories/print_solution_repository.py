from typing import List, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import PrintSolution
from app.repositories.base_repository import BaseRepository


class PrintSolutionRepository(BaseRepository[PrintSolution]):
    """
    打印方案数据访问层
    """

    def __init__(self, db_session: AsyncSession):
        super().__init__(PrintSolution, db_session)

    async def get_by_tenant(
        self,
        tenant_id: str,
        is_valid: Optional[bool] = None
    ) -> List[PrintSolution]:
        """
        根据租户ID获取打印方案列表
        
        Args:
            tenant_id: 租户ID
            is_valid: 是否有效
            
        Returns:
            打印方案实例列表
        """
        query = select(PrintSolution).where(PrintSolution.tenant_id == tenant_id)
        
        if is_valid is not None:
            query = query.where(PrintSolution.is_valid == is_valid)
        
        query = query.order_by(PrintSolution.create_time.desc())
        
        result = await self._db_session.execute(query)
        return result.scalars().all()
