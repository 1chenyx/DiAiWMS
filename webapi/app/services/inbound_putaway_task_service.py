from typing import List, Tuple
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.models.entities.inbound_putaway_task import InboundPutawayTask
from app.models.entities.inbound_pick_putaway_item import InboundPickPutawayItem
from app.models.entities.warehouse_location import WarehouseLocation
from app.repositories.inbound_putaway_task_repository import InboundPutawayTaskRepository
from app.services.base_service import TenantAwareService
from app.schemas.inbound_putaway_task import InboundPutawayTaskCreate, InboundPutawayTaskViewModel
from app.core.user import CurrentUser
from datetime import datetime


class InboundPutawayTaskService(TenantAwareService[InboundPutawayTaskRepository, InboundPutawayTask]):
    
    async def create_task(self, data: InboundPutawayTaskCreate, current_user: CurrentUser) -> Tuple[int, str]:
        query = select(InboundPickPutawayItem).where(InboundPickPutawayItem.id == data.pick_putaway_item_id)
        result = await self._db_session.execute(query)
        pick_item = result.scalar_one_or_none()
        
        if pick_item is None:
            return 0, "拣货上架单明细不存在"
        
        total_putaway = await self._get_total_putaway_qty(data.pick_putaway_item_id)
        remaining_qty = pick_item.qty - total_putaway
        
        if data.putaway_qty > remaining_qty:
            return 0, f"上架数量不能超过剩余数量 {remaining_qty}"
        
        warehouse_id = 0
        warehouse_name = ""
        warehouse_area_id = 0
        warehouse_area_name = ""
        warehouse_location_name = ""
        
        if data.goods_location_id > 0:
            location_query = select(WarehouseLocation).where(WarehouseLocation.id == data.goods_location_id)
            location_result = await self._db_session.execute(location_query)
            location = location_result.scalar_one_or_none()
            
            if location:
                warehouse_location_name = location.node_name
                warehouse_area_id = location.parent_id
                
                if location.parent_id > 0:
                    area_query = select(WarehouseLocation).where(WarehouseLocation.id == location.parent_id)
                    area_result = await self._db_session.execute(area_query)
                    area = area_result.scalar_one_or_none()
                    
                    if area:
                        warehouse_area_name = area.node_name
                        warehouse_id = area.parent_id
                        
                        if area.parent_id > 0:
                            warehouse_query = select(WarehouseLocation).where(WarehouseLocation.id == area.parent_id)
                            warehouse_result = await self._db_session.execute(warehouse_query)
                            warehouse = warehouse_result.scalar_one_or_none()
                            
                            if warehouse:
                                warehouse_name = warehouse.node_name
        
        entity = await self.create_with_tenant(
            current_user.tenant_id,
            pick_putaway_item_id=data.pick_putaway_item_id,
            putaway_qty=data.putaway_qty,
            weight=pick_item.weight,
            volume=pick_item.volume,
            price=pick_item.price,
            expiry_date=pick_item.expiry_date,
            batch_no=pick_item.batch_no or '',
            production_date=pick_item.production_date or 0,
            goods_location_id=data.goods_location_id,
            warehouse_id=warehouse_id,
            warehouse_name=warehouse_name,
            warehouse_area_id=warehouse_area_id,
            warehouse_area_name=warehouse_area_name,
            warehouse_location_name=warehouse_location_name,
            putaway_person_id=current_user.user_id,
            putaway_person=current_user.user_name,
            putaway_time=int(datetime.now().timestamp()),
            series_number=pick_item.series_number,
            creator=current_user.user_name,
            create_time=int(datetime.now().timestamp()),
            last_update_time=int(datetime.now().timestamp())
        )
        
        await self._update_pick_putaway_item_putaway_qty(data.pick_putaway_item_id)
        
        if entity.id > 0:
            return entity.id, "创建成功"
        else:
            return 0, "创建失败"
    
    async def _get_total_putaway_qty(self, pick_putaway_item_id: int) -> int:
        query = select(func.sum(InboundPutawayTask.putaway_qty)).where(
            InboundPutawayTask.pick_putaway_item_id == pick_putaway_item_id
        )
        result = await self._db_session.execute(query)
        total = result.scalar()
        return total if total else 0
    
    async def _update_pick_putaway_item_putaway_qty(self, pick_putaway_item_id: int):
        total_putaway = await self._get_total_putaway_qty(pick_putaway_item_id)
        
        query = select(InboundPickPutawayItem).where(InboundPickPutawayItem.id == pick_putaway_item_id)
        result = await self._db_session.execute(query)
        pick_item = result.scalar_one_or_none()
        
        if pick_item:
            pick_item.putaway_qty = total_putaway
            pick_item.last_update_time = int(datetime.now().timestamp())
    
    async def get_tasks_by_pick_putaway_item_id(self, pick_putaway_item_id: int) -> List[InboundPutawayTaskViewModel]:
        query = select(InboundPutawayTask).where(
            InboundPutawayTask.pick_putaway_item_id == pick_putaway_item_id
        ).order_by(InboundPutawayTask.create_time.desc())
        
        result = await self._db_session.execute(query)
        entities = result.scalars().all()
        
        return [
            InboundPutawayTaskViewModel(
                id=entity.id,
                pick_putaway_item_id=entity.pick_putaway_item_id,
                putaway_qty=entity.putaway_qty,
                weight=float(entity.weight),
                volume=float(entity.volume),
                price=float(entity.price),
                expiry_date=entity.expiry_date,
                goods_location_id=entity.goods_location_id,
                warehouse_id=entity.warehouse_id,
                warehouse_name=entity.warehouse_name,
                warehouse_area_id=entity.warehouse_area_id,
                warehouse_area_name=entity.warehouse_area_name,
                warehouse_location_name=entity.warehouse_location_name,
                putaway_person_id=entity.putaway_person_id,
                putaway_person=entity.putaway_person,
                putaway_time=entity.putaway_time,
                series_number=entity.series_number,
                tenant_id=entity.tenant_id,
                create_time=entity.create_time
            )
            for entity in entities
        ]
