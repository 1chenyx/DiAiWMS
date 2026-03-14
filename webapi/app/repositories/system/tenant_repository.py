from typing import List, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import Tenant
from app.repositories.base_repository import BaseRepository


class TenantRepository(BaseRepository[Tenant]):
    """
    租户数据访问层
    """

    def __init__(self, db_session: AsyncSession):
        super().__init__(Tenant, db_session)

    async def get_by_tenant_code(self, tenant_code: str) -> Optional[Tenant]:
        """
        根据租户编码获取租户
        
        Args:
            tenant_code: 租户编码
            
        Returns:
            租户实例，不存在则返回None
        """
        query = select(Tenant).where(Tenant.tenant_code == tenant_code)
        result = await self._db_session.execute(query)
        return result.scalar_one_or_none()

    async def exists_by_tenant_code(self, tenant_code: str, exclude_id: Optional[int] = None) -> bool:
        """
        检查租户编码是否存在
        
        Args:
            tenant_code: 租户编码
            exclude_id: 排除的ID（用于更新时检查）
            
        Returns:
            存在返回True，否则返回False
        """
        query = select(func.count()).select_from(Tenant).where(Tenant.tenant_code == tenant_code)
        
        if exclude_id is not None:
            query = query.where(Tenant.id != exclude_id)
        
        result = await self._db_session.execute(query)
        return result.scalar() > 0
