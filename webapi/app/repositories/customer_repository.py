from typing import List, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities.customer import Customer
from app.repositories.base_repository import BaseRepository


class CustomerRepository(BaseRepository[Customer]):
    """
    客户数据访问层
    """

    def __init__(self, db_session: AsyncSession):
        super().__init__(Customer, db_session)

    async def search_by_tenant(
        self,
        page_index: int,
        page_size: int,
        tenant_id: str,
        customer_name: Optional[str] = None
    ):
        """
        根据租户ID搜索客户
        
        Args:
            page_index: 页码，从1开始
            page_size: 每页数量
            tenant_id: 租户ID
            customer_name: 客户名称（模糊查询）
            
        Returns:
            (客户列表, 总数量)
        """
        query = select(Customer).where(Customer.tenant_id == tenant_id)
        
        if customer_name:
            query = query.where(Customer.customer_name.like(f"%{customer_name}%"))
        
        total_query = select(func.count()).select_from(query.subquery())
        total_result = await self._db_session.execute(total_query)
        total = total_result.scalar()
        
        query = query.order_by(Customer.create_time.desc())
        query = query.offset((page_index - 1) * page_size).limit(page_size)
        
        result = await self._db_session.execute(query)
        data = result.scalars().all()
        
        return data, total
