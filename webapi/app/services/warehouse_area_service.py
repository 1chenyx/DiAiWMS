from typing import List, Tuple, Optional
from datetime import datetime
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.entities import WarehouseArea, Warehouse, GoodsLocation
from app.schemas.warehouse_area import WarehouseAreaViewModel, WarehouseAreaCreateViewModel, WarehouseAreaUpdateViewModel
from app.core.current_user import CurrentUser


class WarehouseAreaService:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def page_search(
        self,
        page_index: int,
        page_size: int,
        search_params: Optional[dict] = None,
        current_user: Optional[CurrentUser] = None
    ) -> Tuple[List[WarehouseAreaViewModel], int]:
        query = select(WarehouseArea, Warehouse).join(
            Warehouse, WarehouseArea.warehouse_id == Warehouse.id
        ).where(WarehouseArea.tenant_id == current_user.tenant_id)
        
        if search_params:
            if "area_name" in search_params:
                query = query.where(WarehouseArea.area_name.like(f"%{search_params['area_name']}%"))
            if "warehouse_id" in search_params:
                query = query.where(WarehouseArea.warehouse_id == search_params["warehouse_id"])
            if "is_valid" in search_params:
                query = query.where(WarehouseArea.is_valid == search_params["is_valid"])
        
        total_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db_session.execute(total_query)
        totals = total_result.scalar()
        
        query = query.order_by(WarehouseArea.create_time.desc())
        query = query.offset((page_index - 1) * page_size).limit(page_size)
        
        result = await self.db_session.execute(query)
        rows = result.all()
        
        data = [
            WarehouseAreaViewModel(
                id=warehouse_area.id,
                warehouse_id=warehouse_area.warehouse_id,
                area_name=warehouse_area.area_name,
                parent_id=warehouse_area.parent_id,
                create_time=int(warehouse_area.create_time),
                last_update_time=int(warehouse_area.last_update_time),
                is_valid=warehouse_area.is_valid,
                tenant_id=warehouse_area.tenant_id,
                area_property=warehouse_area.area_property
            )
            for warehouse_area, warehouse in rows
        ]
        
        return data, totals

    async def get_warehousearea_by_warehouse_id(self, warehouse_id: int, current_user: CurrentUser) -> List[dict]:
        query = select(WarehouseArea).where(
            WarehouseArea.is_valid == True,
            WarehouseArea.tenant_id == current_user.tenant_id,
            WarehouseArea.warehouse_id == warehouse_id
        )
        result = await self.db_session.execute(query)
        warehouse_areas = result.scalars().all()
        
        return [
            {
                "code": "warehousearea",
                "name": warehouse_area.area_name,
                "value": str(warehouse_area.id),
                "comments": "warehouseareas of warehouse"
            }
            for warehouse_area in warehouse_areas
        ]

    async def get_all(self, warehouse_id: int, current_user: CurrentUser) -> List[WarehouseAreaViewModel]:
        query = select(WarehouseArea).where(
            WarehouseArea.is_valid == True,
            WarehouseArea.tenant_id == current_user.tenant_id
        )
        
        if warehouse_id > 0:
            query = query.where(WarehouseArea.warehouse_id == warehouse_id)
        
        result = await self.db_session.execute(query)
        warehouse_areas = result.scalars().all()
        
        return [
            WarehouseAreaViewModel(
                id=warehouse_area.id,
                warehouse_id=warehouse_area.warehouse_id,
                area_name=warehouse_area.area_name,
                parent_id=warehouse_area.parent_id,
                create_time=int(warehouse_area.create_time),
                last_update_time=int(warehouse_area.last_update_time),
                is_valid=warehouse_area.is_valid,
                tenant_id=warehouse_area.tenant_id,
                area_property=warehouse_area.area_property
            )
            for warehouse_area in warehouse_areas
        ]

    async def get_by_id(self, id: int) -> Optional[WarehouseAreaViewModel]:
        query = select(WarehouseArea).where(WarehouseArea.id == id)
        result = await self.db_session.execute(query)
        warehouse_area = result.scalar_one_or_none()
        
        if warehouse_area is None:
            return None
        
        return WarehouseAreaViewModel(
            id=warehouse_area.id,
            warehouse_id=warehouse_area.warehouse_id,
            area_name=warehouse_area.area_name,
            parent_id=warehouse_area.parent_id,
            create_time=int(warehouse_area.create_time),
            last_update_time=int(warehouse_area.last_update_time),
            is_valid=warehouse_area.is_valid,
            tenant_id=warehouse_area.tenant_id,
            area_property=warehouse_area.area_property
        )

    async def add(self, view_model: WarehouseAreaCreateViewModel, current_user: CurrentUser) -> Tuple[int, str]:
        query = select(WarehouseArea).where(
            WarehouseArea.warehouse_id == view_model.warehouse_id,
            WarehouseArea.area_name == view_model.area_name,
            WarehouseArea.tenant_id == current_user.tenant_id
        )
        result = await self.db_session.execute(query)
        existing = result.scalar_one_or_none()
        
        if existing:
            return 0, f"区域名称 '{view_model.area_name}' 已存在"
        
        warehouse_area = WarehouseArea(
            warehouse_id=view_model.warehouse_id,
            area_name=view_model.area_name,
            parent_id=view_model.parent_id,
            is_valid=view_model.is_valid,
            area_property=view_model.area_property,
            create_time=int(datetime.now().timestamp()),
            last_update_time=int(datetime.now().timestamp()),
            tenant_id=current_user.tenant_id
        )
        
        self.db_session.add(warehouse_area)
        await self.db_session.commit()
        await self.db_session.refresh(warehouse_area)
        
        return warehouse_area.id, "保存成功"

    async def update(self, id: int, view_model: WarehouseAreaUpdateViewModel, current_user: CurrentUser) -> Tuple[bool, str]:
        query = select(WarehouseArea).where(WarehouseArea.id == id)
        result = await self.db_session.execute(query)
        warehouse_area = result.scalar_one_or_none()
        
        if warehouse_area is None:
            return False, "记录不存在"
        
        if view_model.warehouse_id is not None:
            query = select(WarehouseArea).where(
                WarehouseArea.id != id,
                WarehouseArea.warehouse_id == view_model.warehouse_id,
                WarehouseArea.area_name == view_model.area_name,
                WarehouseArea.tenant_id == current_user.tenant_id
            )
            result = await self.db_session.execute(query)
            existing = result.scalar_one_or_none()
            
            if existing:
                return False, f"区域名称 '{view_model.area_name}' 已存在"
        
        if view_model.area_name is not None:
            warehouse_area.area_name = view_model.area_name
        if view_model.warehouse_id is not None:
            warehouse_area.warehouse_id = view_model.warehouse_id
        if view_model.parent_id is not None:
            warehouse_area.parent_id = view_model.parent_id
        if view_model.is_valid is not None:
            warehouse_area.is_valid = view_model.is_valid
        if view_model.area_property is not None:
            warehouse_area.area_property = view_model.area_property
        
        warehouse_area.last_update_time = int(datetime.now().timestamp())
        
        gl_query = select(GoodsLocation).where(GoodsLocation.warehouse_area_id == id)
        gl_result = await self.db_session.execute(gl_query)
        goods_locations = gl_result.scalars().all()
        
        for gl in goods_locations:
            gl.warehouse_area_name = warehouse_area.area_name
            gl.warehouse_area_property = warehouse_area.area_property
            gl.is_valid = warehouse_area.is_valid
        
        await self.db_session.commit()
        
        return True, "保存成功"

    async def delete(self, id: int) -> Tuple[bool, str]:
        query = select(GoodsLocation).where(GoodsLocation.warehouse_area_id == id)
        result = await self.db_session.execute(query)
        existing = result.scalar_one_or_none()
        
        if existing:
            return False, "存在货位，无法删除"
        
        query = select(WarehouseArea).where(WarehouseArea.id == id)
        result = await self.db_session.execute(query)
        warehouse_area = result.scalar_one_or_none()
        
        if warehouse_area is None:
            return False, "记录不存在"
        
        await self.db_session.delete(warehouse_area)
        await self.db_session.commit()
        
        return True, "删除成功"
