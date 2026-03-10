from typing import List, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import User
from app.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    """
    用户数据访问层
    """

    def __init__(self, db_session: AsyncSession):
        super().__init__(User, db_session)

    async def get_by_user_num(self, user_num: str) -> Optional[User]:
        """
        根据用户编号获取用户
        
        Args:
            user_num: 用户编号
            
        Returns:
            用户实例，不存在则返回None
        """
        query = select(User).where(User.user_num == user_num)
        result = await self._db_session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_tenant(
        self,
        tenant_id: str,
        is_valid: Optional[bool] = None
    ) -> List[User]:
        """
        根据租户ID获取用户列表
        
        Args:
            tenant_id: 租户ID
            is_valid: 是否有效
            
        Returns:
            用户实例列表
        """
        query = select(User).where(User.tenant_id == tenant_id)
        
        if is_valid is not None:
            query = query.where(User.is_valid == is_valid)
        
        query = query.order_by(User.create_time.desc())
        
        result = await self._db_session.execute(query)
        return result.scalars().all()

    async def search_by_tenant(
        self,
        page_index: int,
        page_size: int,
        tenant_id: str,
        search_params: Optional[dict] = None
    ):
        """
        根据租户ID搜索用户
        
        Args:
            page_index: 页码，从1开始
            page_size: 每页数量
            tenant_id: 租户ID
            search_params: 搜索参数
            
        Returns:
            (用户列表, 总数量)
        """
        query = select(User).where(User.tenant_id == tenant_id)
        
        if search_params:
            if "user_name" in search_params:
                query = query.where(User.user_name.like(f"%{search_params['user_name']}%"))
        
        total_query = select(func.count()).select_from(query.subquery())
        total_result = await self._db_session.execute(total_query)
        total = total_result.scalar()
        
        query = query.order_by(User.create_time.desc())
        query = query.offset((page_index - 1) * page_size).limit(page_size)
        
        result = await self._db_session.execute(query)
        data = result.scalars().all()
        
        return data, total
