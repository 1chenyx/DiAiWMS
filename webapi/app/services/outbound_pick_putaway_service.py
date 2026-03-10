from datetime import datetime
from typing import List, Tuple, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from app.models.entities.outbound_pick_putaway import OutboundPickPutaway
from app.models.entities.outbound_pick_putaway_item import OutboundPickPutawayItem
from app.models.entities.outbound_order import OutboundOrder
from app.models.entities.outbound_order_item import OutboundOrderItem
from app.models.entities.stock import Stock
from app.models.entities.sku import Sku
from app.models.entities.spu import Spu
from app.models.entities.warehouse_location import WarehouseLocation
from app.schemas.outbound_pick_putaway import (
    OutboundPickPutawayCreate,
    OutboundPickPutawayUpdate,
    OutboundPickPutawayItemUpdate,
    OutboundPickPutawayViewModel,
    OutboundPickPutawayItemViewModel
)
from app.core.current_user import CurrentUser
from app.repositories.outbound_pick_putaway_repository import OutboundPickPutawayRepository
from app.services.base_service import TenantAwareService


class OutboundPickPutawayService(TenantAwareService[OutboundPickPutawayRepository, OutboundPickPutaway]):
    def __init__(self, db_session: AsyncSession):
        repository = OutboundPickPutawayRepository(db_session)
        super().__init__(repository)
        self._db_session = db_session

    async def search(
        self,
        page_index: int = 1,
        page_size: int = 10,
        pick_putaway_no: Optional[str] = None,
        pick_putaway_status: Optional[int] = None,
        order_no: Optional[str] = None,
        current_user: Optional[CurrentUser] = None
    ) -> Tuple[List[OutboundPickPutawayViewModel], int]:
        filters = {}
        if pick_putaway_no:
            filters["pick_putaway_no"] = f"%{pick_putaway_no}%"
        if pick_putaway_status is not None:
            filters["pick_putaway_status"] = pick_putaway_status
        if order_no:
            filters["order_no"] = f"%{order_no}%"
        
        entities, totals = await self.page_query_by_tenant(
            page_index=page_index,
            page_size=page_size,
            tenant_id=current_user.tenant_id if current_user else "",
            filters=filters
        )

        data = []
        for entity in entities:
            warehouse_name = None
            if entity.warehouse_id > 0:
                warehouse_query = select(WarehouseLocation).where(WarehouseLocation.id == entity.warehouse_id)
                warehouse_result = await self._db_session.execute(warehouse_query)
                warehouse = warehouse_result.scalar_one_or_none()
                warehouse_name = warehouse.node_name if warehouse else None

            data.append(OutboundPickPutawayViewModel(
                id=entity.id,
                pick_putaway_no=entity.pick_putaway_no,
                pick_putaway_status=entity.pick_putaway_status,
                order_id=entity.order_id,
                order_no=entity.order_no,
                customer_id=entity.customer_id,
                customer_name=entity.customer_name,
                warehouse_id=entity.warehouse_id,
                warehouse_name=warehouse_name,
                goods_owner_id=entity.goods_owner_id,
                goods_owner_name=entity.goods_owner_name,
                total_qty=entity.total_qty,
                picked_qty=entity.picked_qty,
                total_weight=float(entity.total_weight),
                total_volume=float(entity.total_volume),
                picker_id=entity.picker_id,
                picker=entity.picker,
                pick_start_time=entity.pick_start_time,
                pick_end_time=entity.pick_end_time,
                remark=entity.remark,
                creator=entity.creator,
                create_time=entity.create_time,
                last_update_time=entity.last_update_time,
                tenant_id=entity.tenant_id,
                items=None
            ))

        return data, totals

    async def get_by_id(self, id: int, current_user: Optional[CurrentUser] = None) -> Optional[OutboundPickPutawayViewModel]:
        query = select(OutboundPickPutaway).where(OutboundPickPutaway.id == id)
        result = await self._db_session.execute(query)
        entity = result.scalar_one_or_none()

        if entity is None:
            return None
        
        if current_user and entity.tenant_id != current_user.tenant_id:
            return None

        warehouse_name = None
        if entity.warehouse_id > 0:
            warehouse_query = select(WarehouseLocation).where(WarehouseLocation.id == entity.warehouse_id)
            warehouse_result = await self._db_session.execute(warehouse_query)
            warehouse = warehouse_result.scalar_one_or_none()
            warehouse_name = warehouse.node_name if warehouse else None

        items = await self._get_items_by_pick_putaway_id(id)

        return OutboundPickPutawayViewModel(
            id=entity.id,
            pick_putaway_no=entity.pick_putaway_no,
            pick_putaway_status=entity.pick_putaway_status,
            order_id=entity.order_id,
            order_no=entity.order_no,
            customer_id=entity.customer_id,
            customer_name=entity.customer_name,
            warehouse_id=entity.warehouse_id,
            warehouse_name=warehouse_name,
            goods_owner_id=entity.goods_owner_id,
            goods_owner_name=entity.goods_owner_name,
            total_qty=entity.total_qty,
            picked_qty=entity.picked_qty,
            total_weight=float(entity.total_weight),
            total_volume=float(entity.total_volume),
            picker_id=entity.picker_id,
            picker=entity.picker,
            pick_start_time=entity.pick_start_time,
            pick_end_time=entity.pick_end_time,
            remark=entity.remark,
            creator=entity.creator,
            create_time=entity.create_time,
            last_update_time=entity.last_update_time,
            tenant_id=entity.tenant_id,
            items=items
        )

    async def _get_items_by_pick_putaway_id(self, pick_putaway_id: int) -> List[OutboundPickPutawayItemViewModel]:
        query = select(OutboundPickPutawayItem, Sku, Spu).join(Sku, OutboundPickPutawayItem.sku_id == Sku.id)
        query = query.join(Spu, Sku.spu_id == Spu.id)
        query = query.where(OutboundPickPutawayItem.pick_putaway_id == pick_putaway_id)
        result = await self._db_session.execute(query)
        rows = result.all()

        items = []
        for row in rows:
            entity, sku, spu = row
            goods_location_code = None
            if entity.goods_location_id > 0:
                location_query = select(WarehouseLocation).where(WarehouseLocation.id == entity.goods_location_id)
                location_result = await self._db_session.execute(location_query)
                location = location_result.scalar_one_or_none()
                goods_location_code = location.location_code if location else None

            items.append(OutboundPickPutawayItemViewModel(
                id=entity.id,
                pick_putaway_id=entity.pick_putaway_id,
                order_item_id=entity.order_item_id,
                spu_id=entity.spu_id,
                spu_code=spu.spu_code if spu else None,
                spu_name=spu.spu_name if spu else None,
                sku_id=entity.sku_id,
                sku_code=sku.sku_code if sku else None,
                sku_name=sku.sku_name if sku else None,
                qty=entity.qty,
                picked_qty=entity.picked_qty,
                weight=float(entity.weight),
                volume=float(entity.volume),
                price=float(entity.price),
                expiry_date=entity.expiry_date,
                goods_location_id=entity.goods_location_id,
                goods_location_code=goods_location_code,
                picker_id=entity.picker_id,
                picker=entity.picker,
                pick_time=entity.pick_time,
                series_number=entity.series_number,
                tenant_id=entity.tenant_id
            ))

        return items

    async def create(self, data: OutboundPickPutawayCreate, current_user: CurrentUser) -> Tuple[int, str]:
        query = select(OutboundOrder).where(OutboundOrder.id == data.order_id)
        result = await self._db_session.execute(query)
        order = result.scalar_one_or_none()

        if order is None:
            return 0, "出库订单不存在"

        if order.order_status != 0:
            return 0, "订单已处理，无法生成拣货单"

        query = select(OutboundOrderItem).where(OutboundOrderItem.order_id == data.order_id)
        result = await self._db_session.execute(query)
        order_items = result.scalars().all()

        if not order_items:
            return 0, "订单明细不存在"

        for order_item in order_items:
            query = select(func.sum(Stock.qty)).where(
                Stock.sku_id == order_item.sku_id,
                Stock.tenant_id == current_user.tenant_id
            )
            result = await self._db_session.execute(query)
            available_stock = result.scalar() or 0

            if available_stock < order_item.qty:
                sku = await self.get_one_entity_by_tenant(
                    Sku,
                    current_user.tenant_id,
                    filters={"id": order_item.sku_id}
                )
                sku_code = sku.sku_code if sku else str(order_item.sku_id)
                return 0, f"商品 {sku_code} 库存不足，可用库存: {available_stock}，需要: {order_item.qty}"

        import uuid
        pick_putaway_no = f"PICK{datetime.now().strftime('%Y%m%d%H%M%S')}{str(uuid.uuid4())[:8].upper()}"

        entity = await self.create_with_tenant(
            current_user.tenant_id,
            pick_putaway_no=pick_putaway_no,
            pick_putaway_status=0,
            order_id=order.id,
            order_no=order.order_no,
            customer_id=order.customer_id,
            customer_name=order.customer_name,
            warehouse_id=order.warehouse_id,
            goods_owner_id=order.goods_owner_id,
            goods_owner_name=order.goods_owner_name,
            total_qty=order.total_qty,
            picked_qty=0,
            total_weight=order.total_weight,
            total_volume=order.total_volume,
            picker_id=0,
            picker='',
            pick_start_time=0,
            pick_end_time=0,
            remark=data.remark,
            creator=current_user.user_name,
            create_time=int(datetime.now().timestamp()),
            last_update_time=int(datetime.now().timestamp())
        )

        for order_item in order_items:
            item_entity = OutboundPickPutawayItem(
                pick_putaway_id=entity.id,
                order_item_id=order_item.id,
                spu_id=order_item.spu_id,
                spu_code=order_item.spu_code,
                spu_name=order_item.spu_name,
                sku_id=order_item.sku_id,
                sku_code=order_item.sku_code,
                sku_name=order_item.sku_name,
                qty=order_item.qty,
                picked_qty=0,
                weight=order_item.weight,
                volume=order_item.volume,
                price=order_item.price,
                expiry_date=order_item.expiry_date,
                batch_no=order_item.batch_no or '',
                production_date=order_item.production_date or 0,
                goods_location_id=order_item.goods_location_id,
                picker_id=0,
                picker='',
                pick_time=0,
                series_number='',
                tenant_id=current_user.tenant_id
            )
            self._db_session.add(item_entity)

        order.order_status = 1
        order.last_update_time = int(datetime.now().timestamp())

        await self._db_session.commit()

        if entity.id > 0:
            return entity.id, "保存成功"
        else:
            return 0, "保存失败"

    async def update(self, data: OutboundPickPutawayUpdate, current_user: CurrentUser) -> Tuple[bool, str]:
        entity = await self.get_by_id(data.id)

        if entity is None:
            return False, "记录不存在"

        if data.pick_putaway_status is not None:
            if entity.pick_putaway_status == 3:
                return False, "已生成出库单，无法修改"
        
        update_data = {}
        if data.pick_putaway_status is not None:
            update_data["pick_putaway_status"] = data.pick_putaway_status
        if data.picker_id is not None:
            update_data["picker_id"] = data.picker_id
        if data.picker is not None:
            update_data["picker"] = data.picker
        if data.remark is not None:
            update_data["remark"] = data.remark
        
        update_data["last_update_time"] = int(datetime.now().timestamp())
        
        await self.update_with_tenant(data.id, current_user.tenant_id, **update_data)

        return True, "保存成功"

    async def update_item(self, data: OutboundPickPutawayItemUpdate) -> Tuple[bool, str]:
        query = select(OutboundPickPutawayItem).where(OutboundPickPutawayItem.id == data.id)
        result = await self._db_session.execute(query)
        item = result.scalar_one_or_none()

        if item is None:
            return False, "记录不存在"

        if data.picked_qty > item.qty:
            return False, "拣货数量不能超过订单数量"

        item.picked_qty = data.picked_qty
        item.picker_id = data.picker_id
        item.picker = data.picker
        item.pick_time = data.pick_time

        query = select(OutboundPickPutaway).where(OutboundPickPutaway.id == item.pick_putaway_id)
        result = await self._db_session.execute(query)
        pick_putaway = result.scalar_one_or_none()

        if pick_putaway:
            query = select(func.sum(OutboundPickPutawayItem.picked_qty)).where(
                OutboundPickPutawayItem.pick_putaway_id == item.pick_putaway_id
            )
            result = await self._db_session.execute(query)
            total_picked = result.scalar() or 0
            pick_putaway.picked_qty = total_picked
            pick_putaway.last_update_time = int(datetime.now().timestamp())

        await self._db_session.commit()

        return True, "保存成功"

    async def start_pick(self, id: int, picker_id: int, picker: str, current_user: CurrentUser) -> Tuple[bool, str]:
        entity = await self.get_by_id(id)

        if entity is None:
            return False, "记录不存在"

        if entity.pick_putaway_status != 0:
            return False, "拣货单状态不正确"

        await self.update_with_tenant(
            id,
            entity.tenant_id,
            pick_putaway_status=1,
            picker_id=picker_id,
            picker=picker,
            pick_start_time=int(datetime.now().timestamp()),
            last_update_time=int(datetime.now().timestamp())
        )

        return True, "开始拣货成功"

    async def complete_pick(self, id: int, current_user: CurrentUser) -> Tuple[bool, str]:
        entity = await self.get_by_id(id)

        if entity is None:
            return False, "记录不存在"

        if entity.pick_putaway_status != 1:
            return False, "拣货单状态不正确"

        if entity.picked_qty < entity.total_qty:
            return False, "拣货数量不足，无法完成拣货"

        await self.update_with_tenant(
            id,
            entity.tenant_id,
            pick_putaway_status=2,
            pick_end_time=int(datetime.now().timestamp()),
            last_update_time=int(datetime.now().timestamp())
        )

        return True, "完成拣货成功"

    async def delete(self, id: int, current_user: CurrentUser) -> Tuple[bool, str]:
        entity = await self.get_by_id(id)

        if entity is None:
            return False, "记录不存在"

        if entity.pick_putaway_status != 0:
            return False, "拣货单已处理，无法删除"

        query = select(OutboundOrder).where(OutboundOrder.id == entity.order_id)
        result = await self._db_session.execute(query)
        order = result.scalar_one_or_none()

        if order:
            order.order_status = 0
            order.last_update_time = int(datetime.now().timestamp())

        await self._db_session.delete(entity)
        await self._db_session.commit()

        return True, "删除成功"
