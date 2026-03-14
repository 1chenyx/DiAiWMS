from typing import List, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import UserRole
from app.repositories.base_repository import BaseRepository


class UserRoleRepository(BaseRepository[UserRole]):
    """
    用户角色数据访问层
    """

    def __init__(self, db_session: AsyncSession):
        super().__init__(UserRole, db_session)

    async def get_by_user_id(self, user_id: int) -> List[UserRole]:
        """
        根据用户ID获取角色列表
        
        Args:
            user_id: 用户ID
            
        Returns:
            用户角色实例列表
        """
        query = select(UserRole).where(UserRole.user_id == user_id)
        query = query.order_by(UserRole.create_time.desc())
        
        result = await self._db_session.execute(query)
        return result.scalars().all()
