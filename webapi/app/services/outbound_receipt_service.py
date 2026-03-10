from datetime import datetime
from typing import List, Tuple, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from app.models.entities.outbound_receipt import OutboundReceipt
from app.models.entities.outbound_receipt_item import OutboundReceiptItem
from app.models.entities.outbound_pick_putaway import OutboundPickPutaway
from app.models.entities.outbound_pick_putaway_item import OutboundPickPutawayItem
from app.models.entities.outbound_order import OutboundOrder
from app.models.entities.stock import Stock
from app.models.entities.sku import Sku
from app.models.entities.spu import Spu
from app.models.entities.warehouse_location import WarehouseLocation
from app.schemas.outbound_receipt import (
    OutboundReceiptCreate,
    OutboundReceiptUpdate,
    OutboundReceiptViewModel,
    OutboundReceiptItemViewModel
)
from app.core.current_user import CurrentUser
from app.repositories.outbound_receipt_repository import OutboundReceiptRepository
from app.services.base_service import TenantAwareService


class OutboundReceiptService(TenantAwareService[OutboundReceiptRepository, OutboundReceipt]):
    def __init__(self, db_session: AsyncSession):
        repository = OutboundReceiptRepository(db_session)
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
    ) -> Tuple[List[OutboundReceiptViewModel], int]:
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

            data.append(OutboundReceiptViewModel(
                id=entity.id,
                receipt_no=entity.receipt_no,
                receipt_status=entity.receipt_status,
                pick_putaway_id=entity.pick_putaway_id,
                order_id=entity.order_id,
                order_no=entity.order_no,
                customer_id=entity.customer_id,
                customer_name=entity.customer_name,
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
                package_no=entity.package_no,
                package_person=entity.package_person,
                package_time=entity.package_time,
                weighing_no=entity.weighing_no,
                weighing_person=entity.weighing_person,
                weighing_weight=float(entity.weighing_weight),
                waybill_no=entity.waybill_no,
                carrier=entity.carrier,
                freightfee=float(entity.freightfee),
                outbound_time=entity.outbound_time,
                outbound_person=entity.outbound_person,
                remark=entity.remark,
                creator=entity.creator,
                create_time=entity.create_time,
                last_update_time=entity.last_update_time,
                tenant_id=entity.tenant_id,
                items=None
            ))

        return data, totals

    async def get_by_id(self, id: int, current_user: Optional[CurrentUser] = None) -> Optional[OutboundReceiptViewModel]:
        query = select(OutboundReceipt).where(OutboundReceipt.id == id)
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

        return OutboundReceiptViewModel(
            id=entity.id,
            receipt_no=entity.receipt_no,
            receipt_status=entity.receipt_status,
            pick_putaway_id=entity.pick_putaway_id,
            order_id=entity.order_id,
            order_no=entity.order_no,
            customer_id=entity.customer_id,
            customer_name=entity.customer_name,
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
            package_no=entity.package_no,
            package_person=entity.package_person,
            package_time=entity.package_time,
            weighing_no=entity.weighing_no,
            weighing_person=entity.weighing_person,
            weighing_weight=float(entity.weighing_weight),
            waybill_no=entity.waybill_no,
            carrier=entity.carrier,
            freightfee=float(entity.freightfee),
            outbound_time=entity.outbound_time,
            outbound_person=entity.outbound_person,
            remark=entity.remark,
            creator=entity.creator,
            create_time=entity.create_time,
            last_update_time=entity.last_update_time,
            tenant_id=entity.tenant_id,
            items=items
        )

    async def _get_items_by_receipt_id(self, receipt_id: int) -> List[OutboundReceiptItemViewModel]:
        query = select(OutboundReceiptItem, Sku, Spu).join(Sku, OutboundReceiptItem.sku_id == Sku.id)
        query = query.join(Spu, Sku.spu_id == Spu.id)
        query = query.where(OutboundReceiptItem.receipt_id == receipt_id)
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

            items.append(OutboundReceiptItemViewModel(
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

    async def create(self, data: OutboundReceiptCreate, current_user: CurrentUser) -> Tuple[int, str]:
        query = select(OutboundPickPutaway).where(OutboundPickPutaway.id == data.pick_putaway_id)
        result = await self._db_session.execute(query)
        pick_putaway = result.scalar_one_or_none()

        if pick_putaway is None:
            return 0, "拣货上架单不存在"

        if pick_putaway.pick_putaway_status != 2:
            return 0, "拣货单状态不正确，必须完成拣货才能生成出库单"

        query = select(OutboundOrder).where(OutboundOrder.id == pick_putaway.order_id)
        result = await self._db_session.execute(query)
        order = result.scalar_one_or_none()

        if order is None:
            return 0, "出库订单不存在"

        query = select(OutboundPickPutawayItem).where(OutboundPickPutawayItem.pick_putaway_id == data.pick_putaway_id)
        result = await self._db_session.execute(query)
        pick_putaway_items = result.scalars().all()

        if not pick_putaway_items:
            return 0, "拣货单明细不存在"

        import uuid
        receipt_no = f"OUTREC{datetime.now().strftime('%Y%m%d%H%M%S')}{str(uuid.uuid4())[:8].upper()}"

        total_actual_qty = 0
        total_actual_weight = 0
        total_actual_volume = 0

        entity = await self.create_with_tenant(
            current_user.tenant_id,
            receipt_no=receipt_no,
            receipt_status=0,
            pick_putaway_id=data.pick_putaway_id,
            order_id=order.id,
            order_no=order.order_no,
            customer_id=pick_putaway.customer_id,
            customer_name=pick_putaway.customer_name,
            warehouse_id=pick_putaway.warehouse_id,
            goods_owner_id=pick_putaway.goods_owner_id,
            goods_owner_name=pick_putaway.goods_owner_name,
            total_qty=pick_putaway.total_qty,
            actual_qty=0,
            total_weight=pick_putaway.total_weight,
            actual_weight=0,
            total_volume=pick_putaway.total_volume,
            actual_volume=0,
            package_no=data.package_no or '',
            package_person=data.package_person or '',
            package_time=int(datetime.now().timestamp()) if data.package_person else 0,
            weighing_no=data.weighing_no or '',
            weighing_person=data.weighing_person or '',
            weighing_weight=data.weighing_weight or 0,
            waybill_no=data.waybill_no or '',
            carrier=data.carrier or '',
            freightfee=data.freightfee or 0,
            outbound_time=0,
            outbound_person='',
            remark=data.remark,
            creator=current_user.user_name,
            create_time=int(datetime.now().timestamp()),
            last_update_time=int(datetime.now().timestamp())
        )

        for pick_item in pick_putaway_items:
            item_entity = OutboundReceiptItem(
                receipt_id=entity.id,
                pick_putaway_item_id=pick_item.id,
                spu_id=pick_item.spu_id,
                spu_code=pick_item.spu_code,
                spu_name=pick_item.spu_name,
                sku_id=pick_item.sku_id,
                sku_code=pick_item.sku_code,
                sku_name=pick_item.sku_name,
                qty=pick_item.qty,
                actual_qty=pick_item.picked_qty,
                weight=pick_item.weight,
                actual_weight=pick_item.weight,
                volume=pick_item.volume,
                actual_volume=pick_item.volume,
                price=pick_item.price,
                expiry_date=pick_item.expiry_date,
                batch_no=pick_item.batch_no or '',
                production_date=pick_item.production_date or 0,
                goods_location_id=pick_item.goods_location_id,
                series_number=pick_item.series_number,
                tenant_id=current_user.tenant_id
            )
            self._db_session.add(item_entity)
            total_actual_qty += pick_item.picked_qty
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

    async def update(self, data: OutboundReceiptUpdate, current_user: CurrentUser) -> Tuple[bool, str]:
        entity = await self.get_by_id(data.id)

        if entity is None:
            return False, "记录不存在"

        if entity.receipt_status == 1:
            return False, "已出库，无法修改"

        update_data = {}
        if data.package_no is not None:
            update_data["package_no"] = data.package_no
        if data.package_person is not None:
            update_data["package_person"] = data.package_person
            if data.package_person:
                update_data["package_time"] = int(datetime.now().timestamp())
        if data.weighing_no is not None:
            update_data["weighing_no"] = data.weighing_no
        if data.weighing_person is not None:
            update_data["weighing_person"] = data.weighing_person
        if data.weighing_weight is not None:
            update_data["weighing_weight"] = data.weighing_weight
        if data.waybill_no is not None:
            update_data["waybill_no"] = data.waybill_no
        if data.carrier is not None:
            update_data["carrier"] = data.carrier
        if data.freightfee is not None:
            update_data["freightfee"] = data.freightfee
        if data.remark is not None:
            update_data["remark"] = data.remark
        
        update_data["last_update_time"] = int(datetime.now().timestamp())
        
        await self.update_with_tenant(data.id, current_user.tenant_id, **update_data)

        return True, "保存成功"

    async def complete_outbound(self, id: int, outbound_person: str, current_user: CurrentUser) -> Tuple[bool, str]:
        entity = await self.get_by_id(id)

        if entity is None:
            return False, "记录不存在"

        if entity.receipt_status != 0:
            return False, "出库单状态不正确"

        query = select(OutboundReceiptItem).where(OutboundReceiptItem.receipt_id == id)
        result = await self._db_session.execute(query)
        receipt_items = result.scalars().all()

        for receipt_item in receipt_items:
            query = select(Stock).where(
                Stock.sku_id == receipt_item.sku_id,
                Stock.goods_location_id == receipt_item.goods_location_id,
                Stock.batch_no == receipt_item.batch_no,
                Stock.production_date == receipt_item.production_date,
                Stock.tenant_id == entity.tenant_id
            )
            result = await self._db_session.execute(query)
            stock = result.scalar_one_or_none()

            if stock is None:
                return False, f"SKU {receipt_item.sku_id} 在库位 {receipt_item.goods_location_id} 批次 {receipt_item.batch_no} 没有库存记录"

            if stock.qty < receipt_item.actual_qty:
                return False, f"SKU {receipt_item.sku_id} 在库位 {receipt_item.goods_location_id} 批次 {receipt_item.batch_no} 库存不足"

            stock.qty -= receipt_item.actual_qty
            stock.last_update_time = int(datetime.now().timestamp())

        await self.update_with_tenant(
            id,
            entity.tenant_id,
            receipt_status=1,
            outbound_time=int(datetime.now().timestamp()),
            outbound_person=outbound_person,
            last_update_time=int(datetime.now().timestamp())
        )

        await self._db_session.commit()

        return True, "出库成功"

    async def delete(self, id: int, current_user: CurrentUser) -> Tuple[bool, str]:
        entity = await self.get_by_id(id)

        if entity is None:
            return False, "记录不存在"

        if entity.receipt_status != 0:
            return False, "已出库，无法删除"

        query = select(OutboundPickPutaway).where(OutboundPickPutaway.id == entity.pick_putaway_id)
        result = await self._db_session.execute(query)
        pick_putaway = result.scalar_one_or_none()

        if pick_putaway:
            pick_putaway.pick_putaway_status = 2
            pick_putaway.last_update_time = int(datetime.now().timestamp())

        await self._db_session.delete(entity)
        await self._db_session.commit()

        return True, "删除成功"
