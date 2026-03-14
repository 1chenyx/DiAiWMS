from typing import List, Tuple, Optional
from datetime import datetime
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.entities import WarehouseArea, Warehouse, GoodsLocation
from app.schemas.base.warehouse_area import WarehouseAreaViewModel, WarehouseAreaCreateViewModel, WarehouseAreaUpdateViewModel
from app.core.current_user import CurrentUser
from app.repositories.base.warehouse_area_repository import WarehouseAreaRepository
from app.services.base_service import TenantAwareService


class WarehouseAreaService(TenantAwareService[WarehouseAreaRepository, WarehouseArea]):
    def __init__(self, db_session: AsyncSession):
        repository = WarehouseAreaRepository(db_session)
        super().__init__(repository)
        self._db_session = db_session

    async def page_search(
        self,
        page_index: int,
        page_size: int,
        search_params: Optional[dict] = None,
        current_user: Optional[CurrentUser] = None
    ) -> Tuple[List[WarehouseAreaViewModel], int]:
        filters = {}
        if search_params:
            if "area_name" in search_params:
                filters["area_name"] = f"%{search_params['area_name']}%"
            if "warehouse_id" in search_params:
                filters["warehouse_id"] = search_params["warehouse_id"]
            if "is_valid" in search_params:
                filters["is_valid"] = search_params["is_valid"]
        
        warehouse_areas, totals = await self.page_query_by_tenant(
            page_index=page_index,
            page_size=page_size,
            tenant_id=current_user.tenant_id,
            filters=filters
        )
        
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
            for warehouse_area in warehouse_areas
        ]
        
        return data, totals

    async def get_warehousearea_by_warehouse_id(self, warehouse_id: int, current_user: CurrentUser) -> List[dict]:
        warehouse_areas = await self.query_by_tenant(
            current_user.tenant_id,
            filters={
                "is_valid": True,
                "warehouse_id": warehouse_id
            }
        )
        
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
        filters = {"is_valid": True}
        if warehouse_id > 0:
            filters["warehouse_id"] = warehouse_id
        
        warehouse_areas = await self.query_by_tenant(current_user.tenant_id, filters=filters)
        
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

    async def get_by_id(self, id: int, current_user: Optional[CurrentUser] = None) -> Optional[WarehouseAreaViewModel]:
        query = select(WarehouseArea).where(WarehouseArea.id == id)
        result = await self._db_session.execute(query)
        warehouse_area = result.scalar_one_or_none()
        
        if warehouse_area is None:
            return None
        
        if current_user and warehouse_area.tenant_id != current_user.tenant_id:
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
        existing = await self.get_one_by_tenant(
            current_user.tenant_id,
            filters={
                "warehouse_id": view_model.warehouse_id,
                "area_name": view_model.area_name
            }
        )
        
        if existing:
            return 0, f"区域名称 '{view_model.area_name}' 已存在"
        
        warehouse_area = await self.create_with_tenant(
            current_user.tenant_id,
            warehouse_id=view_model.warehouse_id,
            area_name=view_model.area_name,
            parent_id=view_model.parent_id,
            is_valid=view_model.is_valid,
            area_property=view_model.area_property,
            create_time=int(datetime.now().timestamp()),
            last_update_time=int(datetime.now().timestamp())
        )
        
        return warehouse_area.id, "保存成功"

    async def update(self, id: int, view_model: WarehouseAreaUpdateViewModel, current_user: CurrentUser) -> Tuple[bool, str]:
        warehouse_area = await self._repository.get_by_id(id)
        
        if warehouse_area is None:
            return False, "记录不存在"
        
        if current_user and warehouse_area.tenant_id != current_user.tenant_id:
            return False, "无权修改此记录"
        
        if view_model.warehouse_id is not None and view_model.area_name is not None:
            existing = await self.get_one_by_tenant(
                current_user.tenant_id,
                filters={
                    "warehouse_id": view_model.warehouse_id,
                    "area_name": view_model.area_name
                }
            )
            
            if existing and existing.id != id:
                return False, f"区域名称 '{view_model.area_name}' 已存在"
        
        update_data = {}
        if view_model.area_name is not None:
            update_data["area_name"] = view_model.area_name
        if view_model.warehouse_id is not None:
            update_data["warehouse_id"] = view_model.warehouse_id
        if view_model.parent_id is not None:
            update_data["parent_id"] = view_model.parent_id
        if view_model.is_valid is not None:
            update_data["is_valid"] = view_model.is_valid
        if view_model.area_property is not None:
            update_data["area_property"] = view_model.area_property
        
        update_data["last_update_time"] = int(datetime.now().timestamp())
        
        await self.update_with_tenant(id, current_user.tenant_id, **update_data)
        
        return True, "保存成功"

    async def delete(self, id: int, current_user: Optional[CurrentUser] = None) -> Tuple[bool, str]:
        query = select(GoodsLocation).where(GoodsLocation.warehouse_area_id == id)
        result = await self._db_session.execute(query)
        existing = result.scalar_one_or_none()
        
        if existing:
            return False, "存在货位，无法删除"
        
        query = select(WarehouseArea).where(WarehouseArea.id == id)
        result = await self._db_session.execute(query)
        warehouse_area = result.scalar_one_or_none()
        
        if warehouse_area is None:
            return False, "记录不存在"
        
        if current_user and warehouse_area.tenant_id != current_user.tenant_id:
            return False, "无权删除此记录"
        
        await self._db_session.delete(warehouse_area)
        await self._db_session.commit()
        
        return True, "删除成功"
