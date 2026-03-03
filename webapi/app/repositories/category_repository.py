from typing import List, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import Category
from app.repositories.base_repository import BaseRepository


class CategoryRepository(BaseRepository[Category]):
    """
    分类数据访问层
    """

    def __init__(self, db_session: AsyncSession):
        super().__init__(Category, db_session)

    async def get_by_tenant(
        self,
        tenant_id: str,
        is_valid: Optional[bool] = None
    ) -> List[Category]:
        """
        根据租户ID获取分类列表
        
        Args:
            tenant_id: 租户ID
            is_valid: 是否有效
            
        Returns:
            分类实例列表
        """
        query = select(Category).where(Category.tenant_id == tenant_id)
        
        if is_valid is not None:
            query = query.where(Category.is_valid == is_valid)
        
        query = query.order_by(Category.create_time.desc())
        
        result = await self._db_session.execute(query)
        return result.scalars().all()

    async def get_by_parent_id(
        self,
        parent_id: int,
        tenant_id: str
    ) -> List[Category]:
        """
        根据父级ID获取子分类列表
        
        Args:
            parent_id: 父级ID
            tenant_id: 租户ID
            
        Returns:
            分类实例列表
        """
        query = select(Category).where(
            Category.parent_id == parent_id,
            Category.tenant_id == tenant_id
        )
        query = query.order_by(Category.create_time.desc())
        
        result = await self._db_session.execute(query)
        return result.scalars().all()
