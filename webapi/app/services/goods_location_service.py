from typing import List, Tuple, Optional
from datetime import datetime
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.entities import GoodsLocation, WarehouseArea, Warehouse, Stock
from app.schemas.goods_location import GoodsLocationViewModel, GoodsLocationCreateViewModel, GoodsLocationUpdateViewModel
from app.core.current_user import CurrentUser


class GoodsLocationService:
    """
    货位服务类
    
    提供货位相关的业务逻辑处理,包括货位查询、创建、更新、删除等操作
    """
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def get_goodslocation_by_warehouse_area_id(self, warehouse_area_id: int, current_user: CurrentUser) -> List[dict]:
        """
        根据库区ID获取货位列表,用于下拉选择
        
        Args:
            warehouse_area_id: 库区ID
            current_user: 当前登录用户
            
        Returns:
            货位字典列表
        """
        query = select(GoodsLocation).where(
            GoodsLocation.is_valid == True,
            GoodsLocation.tenant_id == current_user.tenant_id,
            GoodsLocation.warehouse_area_id == warehouse_area_id
        )
        result = await self.db_session.execute(query)
        goods_locations = result.scalars().all()
        
        return [
            {
                "code": "goodslocation",
                "name": goods_location.location_name,
                "value": str(goods_location.id),
                "comments": "goodslocations of warehousearea"
            }
            for goods_location in goods_locations
        ]

    async def page_search(
        self,
        page_index: int,
        page_size: int,
        search_params: Optional[dict] = None,
        current_user: Optional[CurrentUser] = None
    ) -> Tuple[List[GoodsLocationViewModel], int]:
        """
        分页查询货位列表
        
        Args:
            page_index: 页码,从1开始
            page_size: 每页数量
            search_params: 搜索参数
            current_user: 当前登录用户
            
        Returns:
            货位列表和总数量
        """
        query = select(GoodsLocation).where(GoodsLocation.tenant_id == current_user.tenant_id)
        
        if search_params:
            if "location_name" in search_params:
                query = query.where(GoodsLocation.location_name.like(f"%{search_params['location_name']}%"))
            if "warehouse_id" in search_params:
                query = query.where(GoodsLocation.warehouse_id == search_params["warehouse_id"])
            if "warehouse_area_id" in search_params:
                query = query.where(GoodsLocation.warehouse_area_id == search_params["warehouse_area_id"])
            if "is_valid" in search_params:
                query = query.where(GoodsLocation.is_valid == search_params["is_valid"])
        
        total_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db_session.execute(total_query)
        totals = total_result.scalar()
        
        query = query.order_by(GoodsLocation.create_time.desc())
        query = query.offset((page_index - 1) * page_size).limit(page_size)
        
        result = await self.db_session.execute(query)
        goods_locations = result.scalars().all()
        
        data = [
            GoodsLocationViewModel(
                id=gl.id,
                warehouse_id=gl.warehouse_id,
                warehouse_name=gl.warehouse_name,
                warehouse_area_name=gl.warehouse_area_name,
                warehouse_area_property=gl.warehouse_area_property,
                location_name=gl.location_name,
                location_length=float(gl.location_length),
                location_width=float(gl.location_width),
                location_heigth=float(gl.location_heigth),
                location_volume=float(gl.location_volume),
                location_load=float(gl.location_load),
                roadway_number=gl.roadway_number,
                shelf_number=gl.shelf_number,
                layer_number=gl.layer_number,
                tag_number=gl.tag_number,
                create_time=int(gl.create_time),
                last_update_time=int(gl.last_update_time),
                is_valid=gl.is_valid,
                tenant_id=gl.tenant_id,
                warehouse_area_id=gl.warehouse_area_id
            )
            for gl in goods_locations
        ]
        
        return data, totals

    async def get_all(self, current_user: CurrentUser) -> List[GoodsLocationViewModel]:
        query = select(GoodsLocation).where(GoodsLocation.tenant_id == current_user.tenant_id)
        result = await self.db_session.execute(query)
        goods_locations = result.scalars().all()
        
        return [
            GoodsLocationViewModel(
                id=gl.id,
                warehouse_id=gl.warehouse_id,
                warehouse_name=gl.warehouse_name,
                warehouse_area_name=gl.warehouse_area_name,
                warehouse_area_property=gl.warehouse_area_property,
                location_name=gl.location_name,
                location_length=float(gl.location_length),
                location_width=float(gl.location_width),
                location_heigth=float(gl.location_heigth),
                location_volume=float(gl.location_volume),
                location_load=float(gl.location_load),
                roadway_number=gl.roadway_number,
                shelf_number=gl.shelf_number,
                layer_number=gl.layer_number,
                tag_number=gl.tag_number,
                create_time=int(gl.create_time),
                last_update_time=int(gl.last_update_time),
                is_valid=gl.is_valid,
                tenant_id=gl.tenant_id,
                warehouse_area_id=gl.warehouse_area_id
            )
            for gl in goods_locations
        ]

    async def get_by_id(self, id: int) -> Optional[GoodsLocationViewModel]:
        query = select(GoodsLocation).where(GoodsLocation.id == id)
        result = await self.db_session.execute(query)
        goods_location = result.scalar_one_or_none()
        
        if goods_location is None:
            return None
        
        return GoodsLocationViewModel(
            id=goods_location.id,
            warehouse_id=goods_location.warehouse_id,
            warehouse_name=goods_location.warehouse_name,
            warehouse_area_name=goods_location.warehouse_area_name,
            warehouse_area_property=goods_location.warehouse_area_property,
            location_name=goods_location.location_name,
            location_length=float(goods_location.location_length),
            location_width=float(goods_location.location_width),
            location_heigth=float(goods_location.location_heigth),
            location_volume=float(goods_location.location_volume),
            location_load=float(goods_location.location_load),
            roadway_number=goods_location.roadway_number,
            shelf_number=goods_location.shelf_number,
            layer_number=goods_location.layer_number,
            tag_number=goods_location.tag_number,
            create_time=int(goods_location.create_time),
            last_update_time=int(goods_location.last_update_time),
            is_valid=goods_location.is_valid,
            tenant_id=goods_location.tenant_id,
            warehouse_area_id=goods_location.warehouse_area_id
        )

    async def add(self, view_model: GoodsLocationCreateViewModel, current_user: CurrentUser) -> Tuple[int, str]:
        query = select(GoodsLocation).where(
            GoodsLocation.location_name == view_model.location_name,
            GoodsLocation.tenant_id == current_user.tenant_id
        )
        result = await self.db_session.execute(query)
        existing = result.scalar_one_or_none()
        
        if existing:
            return 0, f"货位名称 '{view_model.location_name}' 已存在"
        
        wa_query = select(WarehouseArea).where(WarehouseArea.id == view_model.warehouse_area_id)
        wa_result = await self.db_session.execute(wa_query)
        warehouse_area = wa_result.scalar_one_or_none()
        
        if warehouse_area:
            w_query = select(Warehouse).where(Warehouse.id == warehouse_area.warehouse_id)
            w_result = await self.db_session.execute(w_query)
            warehouse = w_result.scalar_one_or_none()
            
            warehouse_name = warehouse.warehouse_name if warehouse else ""
            warehouse_area_name = warehouse_area.area_name
            warehouse_area_property = warehouse_area.area_property
        else:
            warehouse_name = ""
            warehouse_area_name = ""
            warehouse_area_property = 0
        
        goods_location = GoodsLocation(
            warehouse_id=view_model.warehouse_id,
            warehouse_name=warehouse_name,
            warehouse_area_name=warehouse_area_name,
            warehouse_area_property=warehouse_area_property,
            location_name=view_model.location_name,
            location_length=view_model.location_length,
            location_width=view_model.location_width,
            location_heigth=view_model.location_heigth,
            location_volume=view_model.location_volume,
            location_load=view_model.location_load,
            roadway_number=view_model.roadway_number,
            shelf_number=view_model.shelf_number,
            layer_number=view_model.layer_number,
            tag_number=view_model.tag_number,
            create_time=int(datetime.now().timestamp()),
            last_update_time=int(datetime.now().timestamp()),
            is_valid=view_model.is_valid,
            tenant_id=current_user.tenant_id,
            warehouse_area_id=view_model.warehouse_area_id
        )
        
        self.db_session.add(goods_location)
        await self.db_session.commit()
        await self.db_session.refresh(goods_location)
        
        return goods_location.id, "保存成功"

    async def update(self, id: int, view_model: GoodsLocationUpdateViewModel, current_user: CurrentUser) -> Tuple[bool, str]:
        query = select(GoodsLocation).where(GoodsLocation.id == id)
        result = await self.db_session.execute(query)
        goods_location = result.scalar_one_or_none()
        
        if goods_location is None:
            return False, "记录不存在"
        
        if view_model.location_name is not None:
            query = select(GoodsLocation).where(
                GoodsLocation.id != id,
                GoodsLocation.location_name == view_model.location_name,
                GoodsLocation.tenant_id == current_user.tenant_id
            )
            result = await self.db_session.execute(query)
            existing = result.scalar_one_or_none()
            
            if existing:
                return False, f"货位名称 '{view_model.location_name}' 已存在"
        
        if view_model.location_name is not None:
            goods_location.location_name = view_model.location_name
        if view_model.location_length is not None:
            goods_location.location_length = view_model.location_length
        if view_model.location_width is not None:
            goods_location.location_width = view_model.location_width
        if view_model.location_heigth is not None:
            goods_location.location_heigth = view_model.location_heigth
        if view_model.location_volume is not None:
            goods_location.location_volume = view_model.location_volume
        if view_model.location_load is not None:
            goods_location.location_load = view_model.location_load
        if view_model.roadway_number is not None:
            goods_location.roadway_number = view_model.roadway_number
        if view_model.shelf_number is not None:
            goods_location.shelf_number = view_model.shelf_number
        if view_model.layer_number is not None:
            goods_location.layer_number = view_model.layer_number
        if view_model.tag_number is not None:
            goods_location.tag_number = view_model.tag_number
        if view_model.warehouse_area_id is not None:
            goods_location.warehouse_area_id = view_model.warehouse_area_id
        if view_model.is_valid is not None:
            goods_location.is_valid = view_model.is_valid
        
        goods_location.last_update_time = int(datetime.now().timestamp())
        
        await self.db_session.commit()
        
        return True, "保存成功"

    async def delete(self, id: int) -> Tuple[bool, str]:
        query = select(Stock).where(Stock.goods_location_id == id)
        result = await self.db_session.execute(query)
        existing = result.scalar_one_or_none()
        
        if existing:
            return False, "存在库存，无法删除"
        
        query = select(GoodsLocation).where(GoodsLocation.id == id)
        result = await self.db_session.execute(query)
        goods_location = result.scalar_one_or_none()
        
        if goods_location is None:
            return False, "记录不存在"
        
        await self.db_session.delete(goods_location)
        await self.db_session.commit()
        
        return True, "删除成功"
