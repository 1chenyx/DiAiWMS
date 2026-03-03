from typing import List, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import RoleMenu
from app.repositories.base_repository import BaseRepository


class RoleMenuRepository(BaseRepository[RoleMenu]):
    """
    角色菜单数据访问层
    """

    def __init__(self, db_session: AsyncSession):
        super().__init__(RoleMenu, db_session)

    async def get_by_role_id(self, role_id: int) -> List[RoleMenu]:
        """
        根据角色ID获取菜单列表
        
        Args:
            role_id: 角色ID
            
        Returns:
            角色菜单实例列表
        """
        query = select(RoleMenu).where(RoleMenu.role_id == role_id)
        query = query.order_by(RoleMenu.create_time.desc())
        
        result = await self._db_session.execute(query)
        return result.scalars().all()
