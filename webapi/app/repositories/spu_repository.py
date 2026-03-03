from typing import List, Tuple, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import Spu, Category
from app.repositories.base_repository import BaseRepository


class SpuRepository(BaseRepository[Spu]):
    """
    SPU数据访问层
    
    提供SPU相关的数据库操作
    """

    def __init__(self, db_session: AsyncSession):
        super().__init__(Spu, db_session)

    async def get_by_code_and_tenant(
        self,
        spu_code: str,
        tenant_id: str
    ) -> Optional[Spu]:
        """
        根据SPU编码和租户ID获取记录
        
        Args:
            spu_code: SPU编码
            tenant_id: 租户ID
            
        Returns:
            SPU实例，不存在则返回None
        """
        query = select(Spu).where(
            Spu.spu_code == spu_code,
            Spu.tenant_id == tenant_id
        )
        result = await self._db_session.execute(query)
        return result.scalar_one_or_none()

    async def exists_by_code_and_tenant(
        self,
        spu_code: str,
        tenant_id: str,
        exclude_id: Optional[int] = None
    ) -> bool:
        """
        检查SPU编码在租户下是否存在
        
        Args:
            spu_code: SPU编码
            tenant_id: 租户ID
            exclude_id: 排除的ID（用于更新时检查）
            
        Returns:
            存在返回True，否则返回False
        """
        query = select(func.count()).select_from(Spu).where(
            Spu.spu_code == spu_code,
            Spu.tenant_id == tenant_id
        )
        
        if exclude_id is not None:
            query = query.where(Spu.id != exclude_id)
        
        result = await self._db_session.execute(query)
        return result.scalar() > 0

    async def get_by_tenant(
        self,
        tenant_id: str,
        is_valid: Optional[bool] = None
    ) -> List[Spu]:
        """
        根据租户ID获取SPU列表
        
        Args:
            tenant_id: 租户ID
            is_valid: 是否有效
            
        Returns:
            SPU实例列表
        """
        query = select(Spu).where(Spu.tenant_id == tenant_id)
        
        if is_valid is not None:
            query = query.where(Spu.is_valid == is_valid)
        
        query = query.order_by(Spu.create_time.desc())
        
        result = await self._db_session.execute(query)
        return result.scalars().all()

    async def page_search_by_tenant(
        self,
        page_index: int,
        page_size: int,
        tenant_id: str,
        search_params: Optional[dict] = None
    ) -> Tuple[List[Spu], int]:
        """
        分页查询SPU列表（带租户过滤）
        
        Args:
            page_index: 页码，从1开始
            page_size: 每页数量
            tenant_id: 租户ID
            search_params: 搜索参数
            
        Returns:
            (SPU列表, 总数量)
        """
        query = select(Spu).where(Spu.tenant_id == tenant_id)
        
        if search_params:
            if "spu_code" in search_params:
                query = query.where(Spu.spu_code.like(f"%{search_params['spu_code']}%"))
            if "spu_name" in search_params:
                query = query.where(Spu.spu_name.like(f"%{search_params['spu_name']}%"))
            if "category_id" in search_params:
                query = query.where(Spu.category_id == search_params["category_id"])
            if "is_valid" in search_params:
                query = query.where(Spu.is_valid == search_params["is_valid"])
        
        total_query = select(func.count()).select_from(query.subquery())
        total_result = await self._db_session.execute(total_query)
        total = total_result.scalar()
        
        query = query.order_by(Spu.create_time.desc())
        query = query.offset((page_index - 1) * page_size).limit(page_size)
        
        result = await self._db_session.execute(query)
        data = result.scalars().all()
        
        return data, total
