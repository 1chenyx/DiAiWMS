from typing import List, Tuple, Optional
from datetime import datetime
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.entities import Sku, Spu, Stock
from app.schemas.base.sku import SkuViewModel, SkuCreateViewModel, SkuUpdateViewModel
from app.core.current_user import CurrentUser
from app.repositories.base.sku_repository import SkuRepository
from app.services.base_service import TenantAwareService


class SkuService(TenantAwareService[SkuRepository, Sku]):
    """
    SKU服务类
    
    提供SKU相关的业务逻辑处理,包括SKU查询、创建、更新、删除等操作
    """
    def __init__(self, db_session: AsyncSession):
        repository = SkuRepository(db_session)
        super().__init__(repository)
        self._db_session = db_session

    async def page_search(
        self,
        page_index: int,
        page_size: int,
        search_params: Optional[dict] = None,
        current_user: Optional[CurrentUser] = None
    ) -> Tuple[List[SkuViewModel], int]:
        """
        分页查询SKU列表
        
        Args:
            page_index: 页码,从1开始
            page_size: 每页数量
            search_params: 搜索参数
            current_user: 当前登录用户
            
        Returns:
            SKU列表和总数量
        """
        query = select(Sku, Spu).join(
            Spu, Sku.spu_id == Spu.id
        )
        
        if current_user:
            query = query.where(Sku.tenant_id == current_user.tenant_id)
        
        if search_params:
            if "sku_code" in search_params:
                query = query.where(Sku.sku_code.like(f"%{search_params['sku_code']}%"))
            if "sku_name" in search_params:
                query = query.where(Sku.sku_name.like(f"%{search_params['sku_name']}%"))
            if "spu_id" in search_params:
                query = query.where(Sku.spu_id == search_params["spu_id"])
            if "bar_code" in search_params:
                query = query.where(Sku.bar_code.like(f"%{search_params['bar_code']}%"))
        
        total_query = select(func.count()).select_from(query.subquery())
        total_result = await self._db_session.execute(total_query)
        totals = total_result.scalar()
        
        query = query.order_by(Sku.create_time.desc())
        query = query.offset((page_index - 1) * page_size).limit(page_size)
        
        result = await self._db_session.execute(query)
        rows = result.all()
        
        sku_ids = [sku.id for sku, spu in rows]
        
        stock_query = select(
            Stock.sku_id,
            func.sum(Stock.qty).label('total_available')
        ).where(
            Stock.sku_id.in_(sku_ids)
        ).group_by(Stock.sku_id)
        
        stock_result = await self._db_session.execute(stock_query)
        stock_dict = {row.sku_id: row.total_available or 0 for row in stock_result}
        
        data = [
            SkuViewModel(
                id=sku.id,
                tenant_id=sku.tenant_id,
                spu_id=sku.spu_id,
                sku_code=sku.sku_code,
                sku_name=sku.sku_name,
                bar_code=sku.bar_code,
                weight=float(sku.weight),
                lenght=float(sku.lenght),
                width=float(sku.width),
                height=float(sku.height),
                volume=float(sku.volume),
                unit=sku.unit,
                cost=float(sku.cost),
                price=float(sku.price),
                create_time=int(sku.create_time),
                last_update_time=int(sku.last_update_time),
                available_quantity=stock_dict.get(sku.id, 0)
            )
            for sku, spu in rows
        ]
        
        return data, totals

    async def get_all(self, spu_id: int = 0, current_user: Optional[CurrentUser] = None) -> List[SkuViewModel]:
        filters = {}
        if spu_id > 0:
            filters["spu_id"] = spu_id
        
        if current_user:
            filters["tenant_id"] = current_user.tenant_id
        
        skus = await self._repository.get_all(filters=filters)
        
        return [
            SkuViewModel(
                id=sku.id,
                tenant_id=sku.tenant_id,
                spu_id=sku.spu_id,
                sku_code=sku.sku_code,
                sku_name=sku.sku_name,
                bar_code=sku.bar_code,
                weight=float(sku.weight),
                lenght=float(sku.lenght),
                width=float(sku.width),
                height=float(sku.height),
                volume=float(sku.volume),
                unit=sku.unit,
                cost=float(sku.cost),
                price=float(sku.price),
                create_time=int(sku.create_time),
                last_update_time=int(sku.last_update_time)
            )
            for sku in skus
        ]

    async def get_by_id(self, id: int, current_user: Optional[CurrentUser] = None) -> Optional[SkuViewModel]:
        sku = await self._repository.get_by_id(id)
        
        if sku is None:
            return None
        
        if current_user and sku.tenant_id != current_user.tenant_id:
            return None
        
        stock_query = select(
            func.sum(Stock.qty).label('total_available')
        ).where(
            Stock.sku_id == id
        )
        
        stock_result = await self._db_session.execute(stock_query)
        available_quantity = stock_result.scalar() or 0
        
        return SkuViewModel(
            id=sku.id,
            tenant_id=sku.tenant_id,
            spu_id=sku.spu_id,
            sku_code=sku.sku_code,
            sku_name=sku.sku_name,
            bar_code=sku.bar_code,
            weight=float(sku.weight),
            lenght=float(sku.lenght),
            width=float(sku.width),
            height=float(sku.height),
            volume=float(sku.volume),
            unit=sku.unit,
            cost=float(sku.cost),
            price=float(sku.price),
            create_time=int(sku.create_time),
            last_update_time=int(sku.last_update_time),
            available_quantity=available_quantity
        )

    async def add(self, view_model: SkuCreateViewModel, current_user: CurrentUser) -> Tuple[int, str]:
        existing = await self.get_one_by_tenant(
            current_user.tenant_id,
            filters={"sku_code": view_model.sku_code}
        )
        
        if existing:
            return 0, f"SKU编码 '{view_model.sku_code}' 已存在"
        
        sku = await self.create_with_tenant(
            current_user.tenant_id,
            spu_id=view_model.spu_id,
            sku_code=view_model.sku_code,
            sku_name=view_model.sku_name,
            bar_code=view_model.bar_code,
            weight=view_model.weight,
            lenght=view_model.lenght,
            width=view_model.width,
            height=view_model.height,
            volume=view_model.volume,
            unit=view_model.unit,
            cost=view_model.cost,
            price=view_model.price,
            create_time=int(datetime.now().timestamp()),
            last_update_time=int(datetime.now().timestamp())
        )
        
        return sku.id, "保存成功"

    async def update(self, id: int, view_model: SkuUpdateViewModel, current_user: CurrentUser) -> Tuple[bool, str]:
        sku = await self._repository.get_by_id(id)
        
        if sku is None:
            return False, "记录不存在"
        
        if view_model.sku_code is not None:
            existing = await self.get_one_by_tenant(
                current_user.tenant_id,
                filters={"sku_code": view_model.sku_code}
            )
            
            if existing and existing.id != id:
                return False, f"SKU编码 '{view_model.sku_code}' 已存在"
        
        update_data = {}
        if view_model.spu_id is not None:
            update_data["spu_id"] = view_model.spu_id
        if view_model.sku_code is not None:
            update_data["sku_code"] = view_model.sku_code
        if view_model.sku_name is not None:
            update_data["sku_name"] = view_model.sku_name
        if view_model.bar_code is not None:
            update_data["bar_code"] = view_model.bar_code
        if view_model.weight is not None:
            update_data["weight"] = view_model.weight
        if view_model.lenght is not None:
            update_data["lenght"] = view_model.lenght
        if view_model.width is not None:
            update_data["width"] = view_model.width
        if view_model.height is not None:
            update_data["height"] = view_model.height
        if view_model.volume is not None:
            update_data["volume"] = view_model.volume
        if view_model.unit is not None:
            update_data["unit"] = view_model.unit
        if view_model.cost is not None:
            update_data["cost"] = view_model.cost
        if view_model.price is not None:
            update_data["price"] = view_model.price
        
        update_data["last_update_time"] = int(datetime.now().timestamp())
        
        if update_data:
            await self.update_with_tenant(id, current_user.tenant_id, **update_data)
        
        return True, "保存成功"

    async def delete(self, id: int, current_user: Optional[CurrentUser] = None) -> Tuple[bool, str]:
        sku = await self._repository.get_by_id(id)
        
        if sku is None:
            return False, "记录不存在"
        
        if current_user and sku.tenant_id != current_user.tenant_id:
            return False, "无权删除此记录"
        
        result = await self._repository.delete(id)
        
        if not result:
            return False, "删除失败"
        
        return True, "删除成功"
