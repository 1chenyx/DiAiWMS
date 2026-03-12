from datetime import datetime
from typing import List, Tuple, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.entities.inbound_receipt import InboundReceipt
from app.models.entities.inbound_receipt_item import InboundReceiptItem
from app.models.entities.inbound_pick_putaway import InboundPickPutaway
from app.models.entities.inbound_pick_putaway_item import InboundPickPutawayItem
from app.models.entities.inbound_order import InboundOrder
from app.models.entities.stock import Stock
from app.models.entities.sku import Sku
from app.models.entities.spu import Spu
from app.models.entities.warehouse_location import WarehouseLocation
from app.schemas.inbound_receipt import (
    InboundReceiptCreate,
    InboundReceiptUpdate,
    InboundReceiptViewModel,
    InboundReceiptItemViewModel
)
from app.core.current_user import CurrentUser
from app.repositories.inbound_receipt_repository import InboundReceiptRepository
from app.services.base_service import TenantAwareService


class InboundReceiptService(TenantAwareService[InboundReceiptRepository, InboundReceipt]):
    def __init__(self, db_session: AsyncSession):
        repository = InboundReceiptRepository(db_session)
        super().__init__(repository)
        self._db_session = db_session

    async def search(
        self,
        page_index: int = 1,
        page_size: int = 10,
        receipt_no: Optional[str] = None,
        receipt_status: Optional[int] = None,
        order_no: Optional[str] = None,
        current_user: Optional[CurrentUser] = None
    ) -> Tuple[List[InboundReceiptViewModel], int]:
        filters = {}
        if receipt_no:
            filters["receipt_no"] = f"%{receipt_no}%"
        if receipt_status is not None:
            filters["receipt_status"] = receipt_status
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

            data.append(InboundReceiptViewModel(
                id=entity.id,
                receipt_no=entity.receipt_no,
                receipt_status=entity.receipt_status,
                pick_putaway_id=entity.pick_putaway_id,
                order_id=entity.order_id,
                order_no=entity.order_no,
                supplier_id=entity.supplier_id,
                supplier_name=entity.supplier_name,
                warehouse_id=entity.warehouse_id,
                warehouse_name=warehouse_name,
                goods_owner_id=entity.goods_owner_id,
                goods_owner_name=entity.goods_owner_name,
                total_qty=entity.total_qty,
                actual_qty=entity.actual_qty,
                total_weight=float(entity.total_weight),
                actual_weight=float(entity.actual_weight),
                total_volume=float(entity.total_volume),
                actual_volume=float(entity.actual_volume),
                arrival_time=entity.arrival_time,
                unload_time=entity.unload_time,
                unload_person_id=entity.unload_person_id,
                unload_person=entity.unload_person,
                inbound_time=entity.inbound_time,
                inbound_person=entity.inbound_person,
                remark=entity.remark,
                creator=entity.creator,
                create_time=entity.create_time,
                last_update_time=entity.last_update_time,
                tenant_id=entity.tenant_id,
                items=None
            ))

        return data, totals

    async def get_by_id(self, id: int, current_user: Optional[CurrentUser] = None) -> Optional[InboundReceiptViewModel]:
        query = select(InboundReceipt).where(InboundReceipt.id == id)
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

        items = await self._get_items_by_receipt_id(id)

        return InboundReceiptViewModel(
            id=entity.id,
            receipt_no=entity.receipt_no,
            receipt_status=entity.receipt_status,
            pick_putaway_id=entity.pick_putaway_id,
            order_id=entity.order_id,
            order_no=entity.order_no,
            supplier_id=entity.supplier_id,
            supplier_name=entity.supplier_name,
            warehouse_id=entity.warehouse_id,
            warehouse_name=warehouse_name,
            goods_owner_id=entity.goods_owner_id,
            goods_owner_name=entity.goods_owner_name,
            total_qty=entity.total_qty,
            actual_qty=entity.actual_qty,
            total_weight=float(entity.total_weight),
            actual_weight=float(entity.actual_weight),
            total_volume=float(entity.total_volume),
            actual_volume=float(entity.actual_volume),
            arrival_time=entity.arrival_time,
            unload_time=entity.unload_time,
            unload_person_id=entity.unload_person_id,
            unload_person=entity.unload_person,
            inbound_time=entity.inbound_time,
            inbound_person=entity.inbound_person,
            remark=entity.remark,
            creator=entity.creator,
            create_time=entity.create_time,
            last_update_time=entity.last_update_time,
            tenant_id=entity.tenant_id,
            items=items
        )

    async def _get_items_by_receipt_id(self, receipt_id: int) -> List[InboundReceiptItemViewModel]:
        query = select(InboundReceiptItem, Sku, Spu).join(Sku, InboundReceiptItem.sku_id == Sku.id)
        query = query.join(Spu, Sku.spu_id == Spu.id)
        query = query.where(InboundReceiptItem.receipt_id == receipt_id)
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
                goods_location_code = location.node_name if location else None

            items.append(InboundReceiptItemViewModel(
                id=entity.id,
                receipt_id=entity.receipt_id,
                pick_putaway_item_id=entity.pick_putaway_item_id,
                spu_id=entity.spu_id,
                spu_code=spu.spu_code if spu else None,
                spu_name=spu.spu_name if spu else None,
                sku_id=entity.sku_id,
                sku_code=sku.sku_code if sku else None,
                sku_name=sku.sku_name if sku else None,
                qty=entity.qty,
                actual_qty=entity.actual_qty,
                weight=float(entity.weight),
                actual_weight=float(entity.actual_weight),
                volume=float(entity.volume),
                actual_volume=float(entity.actual_volume),
                price=float(entity.price),
                expiry_date=entity.expiry_date,
                goods_location_id=entity.goods_location_id,
                goods_location_code=goods_location_code,
                series_number=entity.series_number,
                tenant_id=entity.tenant_id
            ))

        return items

    async def create(self, data: InboundReceiptCreate, current_user: CurrentUser) -> Tuple[int, str]:
        query = select(InboundPickPutaway).where(InboundPickPutaway.id == data.inbound_pick_putaway_id)
        result = await self._db_session.execute(query)
        pick_putaway = result.scalar_one_or_none()

        if pick_putaway is None:
            return 0, "拣货上架单不存在"

        if pick_putaway.pick_putaway_status != 2:
            return 0, "上架单状态不正确，必须完成上架才能生成入库单"

        query = select(InboundOrder).where(InboundOrder.id == pick_putaway.order_id)
        result = await self._db_session.execute(query)
        order = result.scalar_one_or_none()

        if order is None:
            return 0, "入库订单不存在"

        query = select(InboundPickPutawayItem).where(InboundPickPutawayItem.pick_putaway_id == data.inbound_pick_putaway_id)
        result = await self._db_session.execute(query)
        pick_putaway_items = result.scalars().all()

        if not pick_putaway_items:
            return 0, "上架单明细不存在"

        import uuid
        receipt_no = f"INREC{datetime.now().strftime('%Y%m%d%H%M%S')}{str(uuid.uuid4())[:8].upper()}"

        total_actual_qty = 0
        total_actual_weight = 0
        total_actual_volume = 0

        entity = await self.create_with_tenant(
            current_user.tenant_id,
            receipt_no=receipt_no,
            receipt_status=0,
            pick_putaway_id=data.inbound_pick_putaway_id,
            order_id=order.id,
            order_no=order.order_no,
            supplier_id=pick_putaway.supplier_id,
            supplier_name=pick_putaway.supplier_name,
            warehouse_id=pick_putaway.warehouse_id,
            goods_owner_id=pick_putaway.goods_owner_id,
            goods_owner_name=pick_putaway.goods_owner_name,
            total_qty=pick_putaway.total_qty,
            actual_qty=0,
            total_weight=pick_putaway.total_weight,
            actual_weight=0,
            total_volume=pick_putaway.total_volume,
            actual_volume=0,
            arrival_time=data.arrival_time or 0,
            unload_time=data.unload_time or 0,
            unload_person_id=data.unload_person_id or 0,
            unload_person=data.unload_person or '',
            inbound_time=0,
            inbound_person='',
            remark=data.remark,
            creator=current_user.user_name,
            create_time=int(datetime.now().timestamp()),
            last_update_time=int(datetime.now().timestamp())
        )

        for pick_item in pick_putaway_items:
            item_entity = InboundReceiptItem(
                receipt_id=entity.id,
                pick_putaway_item_id=pick_item.id,
                spu_id=pick_item.spu_id,
                spu_code=pick_item.spu_code,
                spu_name=pick_item.spu_name,
                sku_id=pick_item.sku_id,
                sku_code=pick_item.sku_code,
                sku_name=pick_item.sku_name,
                qty=pick_item.qty,
                actual_qty=pick_item.putaway_qty,
                weight=pick_item.weight,
                actual_weight=pick_item.weight,
                volume=pick_item.volume,
                actual_volume=pick_item.volume,
                price=pick_item.price,
                expiry_date=pick_item.expiry_date,
                batch_no=pick_item.batch_no or '',
                production_date=pick_item.production_date or 0,
                goods_location_id=pick_item.goods_location_id,
                warehouse_id=pick_item.warehouse_id,
                warehouse_name=pick_item.warehouse_name,
                warehouse_area_id=pick_item.warehouse_area_id,
                warehouse_area_name=pick_item.warehouse_area_name,
                warehouse_location_name=pick_item.warehouse_location_name,
                series_number=pick_item.series_number,
                tenant_id=current_user.tenant_id
            )
            self._db_session.add(item_entity)
            total_actual_qty += pick_item.putaway_qty
            total_actual_weight += float(pick_item.weight)
            total_actual_volume += float(pick_item.volume)

        entity.actual_qty = total_actual_qty
        entity.actual_weight = total_actual_weight
        entity.actual_volume = total_actual_volume

        pick_putaway.pick_putaway_status = 3
        pick_putaway.last_update_time = int(datetime.now().timestamp())

        await self._db_session.commit()

        if entity.id > 0:
            return entity.id, "保存成功"
        else:
            return 0, "保存失败"

    async def update(self, data: InboundReceiptUpdate, current_user: CurrentUser) -> Tuple[bool, str]:
        entity = await self.get_by_id(data.id, current_user)

        if entity is None:
            return False, "记录不存在"

        if entity.receipt_status == 1:
            return False, "已入库，无法修改"

        update_data = {}
        if data.arrival_time is not None:
            update_data["arrival_time"] = data.arrival_time
        if data.unload_time is not None:
            update_data["unload_time"] = data.unload_time
        if data.unload_person_id is not None:
            update_data["unload_person_id"] = data.unload_person_id
        if data.unload_person is not None:
            update_data["unload_person"] = data.unload_person
        if data.remark is not None:
            update_data["remark"] = data.remark
        
        update_data["last_update_time"] = int(datetime.now().timestamp())
        
        await self.update_with_tenant(data.id, current_user.tenant_id, **update_data)

        return True, "保存成功"

    async def complete_inbound(self, id: int, inbound_person: str, current_user: CurrentUser) -> Tuple[bool, str]:
        entity = await self.get_by_id(id, current_user)

        if entity is None:
            return False, "记录不存在"

        if entity.receipt_status != 0:
            return False, "入库单状态不正确"

        if not entity.tenant_id:
            return False, "入库单租户ID为空"

        query = select(InboundReceiptItem).where(InboundReceiptItem.receipt_id == id)
        result = await self._db_session.execute(query)
        receipt_items = result.scalars().all()

        for receipt_item in receipt_items:
            query = select(Stock).where(
                Stock.sku_id == receipt_item.sku_id,
                Stock.goods_location_id == receipt_item.goods_location_id,
                Stock.tenant_id == entity.tenant_id
            )
            result = await self._db_session.execute(query)
            stock = result.scalar_one_or_none()

            sku_query = select(Sku).where(Sku.id == receipt_item.sku_id)
            sku_result = await self._db_session.execute(sku_query)
            sku = sku_result.scalar_one_or_none()
            
            spu_name = ""
            sku_code = ""
            sku_name = ""
            
            if sku:
                sku_code = sku.sku_code
                sku_name = sku.sku_name
                
                spu_query = select(Spu).where(Spu.id == sku.spu_id)
                spu_result = await self._db_session.execute(spu_query)
                spu = spu_result.scalar_one_or_none()
                
                if spu:
                    spu_name = spu.spu_name

            if stock is None:
                stock = Stock(
                    sku_id=receipt_item.sku_id,
                    goods_location_id=receipt_item.goods_location_id,
                    qty=receipt_item.actual_qty,
                    goods_owner_id=entity.goods_owner_id,
                    tenant_id=entity.tenant_id,
                    is_freeze=False,
                    series_number=receipt_item.series_number,
                    expiry_date=receipt_item.expiry_date,
                    price=float(receipt_item.price),
                    putaway_date=int(datetime.now().timestamp()),
                    last_update_time=int(datetime.now().timestamp()),
                    warehouse_id=receipt_item.warehouse_id,
                    warehouse_name=receipt_item.warehouse_name,
                    warehouse_area_id=receipt_item.warehouse_area_id,
                    warehouse_area_name=receipt_item.warehouse_area_name,
                    warehouse_location_name=receipt_item.warehouse_location_name,
                    spu_name=spu_name,
                    sku_code=sku_code,
                    sku_name=sku_name,
                    batch_no=receipt_item.batch_no or '',
                    production_date=receipt_item.production_date or 0
                )
                self._db_session.add(stock)
            else:
                stock.qty += receipt_item.actual_qty
                stock.last_update_time = int(datetime.now().timestamp())

        await self.update_with_tenant(
            id,
            entity.tenant_id,
            receipt_status=1,
            inbound_time=int(datetime.now().timestamp()),
            inbound_person=inbound_person,
            last_update_time=int(datetime.now().timestamp())
        )

        await self._db_session.commit()

        return True, "入库成功"

    async def delete(self, id: int, current_user: CurrentUser) -> Tuple[bool, str]:
        entity = await self.get_by_id(id, current_user)

        if entity is None:
            return False, "记录不存在"

        if entity.receipt_status != 0:
            return False, "已入库，无法删除"

        query = select(InboundPickPutaway).where(InboundPickPutaway.id == entity.pick_putaway_id)
        result = await self._db_session.execute(query)
        pick_putaway = result.scalar_one_or_none()

        if pick_putaway:
            pick_putaway.pick_putaway_status = 2
            pick_putaway.last_update_time = int(datetime.now().timestamp())

        await self._db_session.delete(entity)
        await self._db_session.commit()

        return True, "删除成功"
