from datetime import datetime
from typing import List, Tuple, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.entities.inbound_pick_putaway import InboundPickPutaway
from app.models.entities.inbound_pick_putaway_item import InboundPickPutawayItem
from app.models.entities.inbound_order import InboundOrder
from app.models.entities.inbound_order_item import InboundOrderItem
from app.models.entities.stock import Stock
from app.models.entities.sku import Sku
from app.models.entities.spu import Spu
from app.models.entities.warehouse_location import WarehouseLocation
from app.schemas.inbound_pick_putaway import (
    InboundPickPutawayCreate,
    InboundPickPutawayUpdate,
    InboundPickPutawayItemUpdate,
    InboundPickPutawayItemSelectLocation,
    InboundPickPutawayViewModel,
    InboundPickPutawayItemViewModel
)
from app.core.current_user import CurrentUser
from app.repositories.inbound_pick_putaway_repository import InboundPickPutawayRepository
from app.services.base_service import TenantAwareService


class InboundPickPutawayService(TenantAwareService[InboundPickPutawayRepository, InboundPickPutaway]):
    def __init__(self, db_session: AsyncSession):
        repository = InboundPickPutawayRepository(db_session)
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
    ) -> Tuple[List[InboundPickPutawayViewModel], int]:
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

            data.append(InboundPickPutawayViewModel(
                id=entity.id,
                pick_putaway_no=entity.pick_putaway_no,
                pick_putaway_status=entity.pick_putaway_status,
                order_id=entity.order_id,
                order_no=entity.order_no,
                supplier_id=entity.supplier_id,
                supplier_name=entity.supplier_name,
                warehouse_id=entity.warehouse_id,
                warehouse_name=warehouse_name,
                goods_owner_id=entity.goods_owner_id,
                goods_owner_name=entity.goods_owner_name,
                total_qty=entity.total_qty,
                putaway_qty=entity.putaway_qty,
                total_weight=float(entity.total_weight),
                total_volume=float(entity.total_volume),
                putaway_person_id=entity.putaway_person_id,
                putaway_person=entity.putaway_person,
                putaway_start_time=entity.putaway_start_time,
                putaway_end_time=entity.putaway_end_time,
                remark=entity.remark,
                creator=entity.creator,
                create_time=entity.create_time,
                last_update_time=entity.last_update_time,
                tenant_id=entity.tenant_id,
                items=None
            ))

        return data, totals

    async def get_by_id(self, id: int, current_user: Optional[CurrentUser] = None) -> Optional[InboundPickPutawayViewModel]:
        query = select(InboundPickPutaway).where(InboundPickPutaway.id == id)
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

        return InboundPickPutawayViewModel(
            id=entity.id,
            pick_putaway_no=entity.pick_putaway_no,
            pick_putaway_status=entity.pick_putaway_status,
            order_id=entity.order_id,
            order_no=entity.order_no,
            supplier_id=entity.supplier_id,
            supplier_name=entity.supplier_name,
            warehouse_id=entity.warehouse_id,
            warehouse_name=warehouse_name,
            goods_owner_id=entity.goods_owner_id,
            goods_owner_name=entity.goods_owner_name,
            total_qty=entity.total_qty,
            putaway_qty=entity.putaway_qty,
            total_weight=float(entity.total_weight),
            total_volume=float(entity.total_volume),
            putaway_person_id=entity.putaway_person_id,
            putaway_person=entity.putaway_person,
            putaway_start_time=entity.putaway_start_time,
            putaway_end_time=entity.putaway_end_time,
            remark=entity.remark,
            creator=entity.creator,
            create_time=entity.create_time,
            last_update_time=entity.last_update_time,
            tenant_id=entity.tenant_id,
            items=items
        )

    async def _get_items_by_pick_putaway_id(self, pick_putaway_id: int) -> List[InboundPickPutawayItemViewModel]:
        query = select(InboundPickPutawayItem).where(InboundPickPutawayItem.pick_putaway_id == pick_putaway_id)
        result = await self._db_session.execute(query)
        entities = result.scalars().all()

        items = []
        for entity in entities:
            items.append(InboundPickPutawayItemViewModel(
                id=entity.id,
                pick_putaway_id=entity.pick_putaway_id,
                order_item_id=entity.order_item_id,
                spu_id=entity.spu_id,
                spu_code=entity.spu_code,
                spu_name=entity.spu_name,
                sku_id=entity.sku_id,
                sku_code=entity.sku_code,
                sku_name=entity.sku_name,
                qty=entity.qty,
                putaway_qty=entity.putaway_qty,
                weight=float(entity.weight),
                volume=float(entity.volume),
                price=float(entity.price),
                expiry_date=entity.expiry_date,
                batch_no=entity.batch_no,
                production_date=entity.production_date,
                goods_location_id=entity.goods_location_id,
                goods_location_code=entity.warehouse_location_name,
                putaway_person_id=entity.putaway_person_id,
                putaway_person=entity.putaway_person,
                putaway_time=entity.putaway_time,
                series_number=entity.series_number,
                tenant_id=entity.tenant_id
            ))

        return items

    async def create(self, data: InboundPickPutawayCreate, current_user: CurrentUser) -> Tuple[int, str]:
        import json
        
        query = select(InboundOrder).where(InboundOrder.id.in_(data.inbound_order_ids))
        result = await self._db_session.execute(query)
        orders = result.scalars().all()

        if not orders:
            return 0, "入库订单不存在"

        for order in orders:
            if order.order_status != 0:
                return 0, f"订单{order.order_no}已处理，无法生成上架单"

        all_order_items = []
        order_map = {}
        for order in orders:
            query = select(InboundOrderItem).where(InboundOrderItem.order_id == order.id)
            result = await self._db_session.execute(query)
            order_items = result.scalars().all()
            
            if not order_items:
                return 0, f"订单{order.order_no}明细不存在"
            
            for item in order_items:
                item_dict = {
                    'order_id': order.id,
                    'order_no': order.order_no,
                    'order_item_id': item.id,
                    'spu_id': item.spu_id,
                    'spu_code': item.spu_code,
                    'spu_name': item.spu_name,
                    'sku_id': item.sku_id,
                    'sku_code': item.sku_code,
                    'sku_name': item.sku_name,
                    'qty': item.qty,
                    'weight': item.weight,
                    'volume': item.volume,
                    'price': item.price,
                    'expiry_date': item.expiry_date,
                    'batch_no': item.batch_no or '',
                    'production_date': item.production_date or 0,
                    'create_time': order.create_time
                }
                all_order_items.append(item_dict)
                order_map[order.id] = order

        merged_items = {}
        for item in all_order_items:
            key = f"{item['sku_id']}_{item['batch_no']}_{item['production_date']}"
            if key not in merged_items:
                merged_items[key] = {
                    'order_item_ids': [],
                    'spu_id': item['spu_id'],
                    'spu_code': item['spu_code'],
                    'spu_name': item['spu_name'],
                    'sku_id': item['sku_id'],
                    'sku_code': item['sku_code'],
                    'sku_name': item['sku_name'],
                    'qty': 0,
                    'weight': 0,
                    'volume': 0,
                    'price': item['price'],
                    'expiry_date': item['expiry_date'],
                    'batch_no': item['batch_no'],
                    'production_date': item['production_date']
                }
            
            merged_items[key]['order_item_ids'].append(item['order_item_id'])
            merged_items[key]['qty'] += item['qty']
            merged_items[key]['weight'] += item['weight']
            merged_items[key]['volume'] += item['volume']

        import uuid
        pick_putaway_no = f"PUT{datetime.now().strftime('%Y%m%d%H%M%S')}{str(uuid.uuid4())[:8].upper()}"

        first_order = orders[0]
        order_nos = [order.order_no for order in orders]
        
        total_qty = sum(item['qty'] for item in merged_items.values())
        total_weight = sum(item['weight'] for item in merged_items.values())
        total_volume = sum(item['volume'] for item in merged_items.values())

        entity = await self.create_with_tenant(
            current_user.tenant_id,
            pick_putaway_no=pick_putaway_no,
            pick_putaway_status=0,
            order_id=first_order.id,
            order_no=first_order.order_no,
            order_nos=json.dumps(order_nos, ensure_ascii=False),
            supplier_id=first_order.supplier_id,
            supplier_name=first_order.supplier_name,
            warehouse_id=first_order.warehouse_id,
            goods_owner_id=first_order.goods_owner_id,
            goods_owner_name=first_order.goods_owner_name,
            total_qty=total_qty,
            putaway_qty=0,
            total_weight=total_weight,
            total_volume=total_volume,
            putaway_person_id=0,
            putaway_person='',
            putaway_start_time=0,
            putaway_end_time=0,
            remark=data.remark,
            creator=current_user.user_name,
            create_time=int(datetime.now().timestamp()),
            last_update_time=int(datetime.now().timestamp())
        )

        for item_data in merged_items.values():
            item_entity = InboundPickPutawayItem(
                pick_putaway_id=entity.id,
                order_item_id=item_data['order_item_ids'][0],
                order_item_ids=json.dumps(item_data['order_item_ids'], ensure_ascii=False),
                spu_id=item_data['spu_id'],
                spu_code=item_data['spu_code'],
                spu_name=item_data['spu_name'],
                sku_id=item_data['sku_id'],
                sku_code=item_data['sku_code'],
                sku_name=item_data['sku_name'],
                qty=item_data['qty'],
                putaway_qty=0,
                weight=item_data['weight'],
                volume=item_data['volume'],
                price=item_data['price'],
                expiry_date=item_data['expiry_date'],
                batch_no=item_data['batch_no'],
                production_date=item_data['production_date'],
                goods_location_id=0,
                putaway_person_id=0,
                putaway_person='',
                putaway_time=0,
                series_number='',
                tenant_id=current_user.tenant_id
            )
            self._db_session.add(item_entity)

        for order in orders:
            order.order_status = 1
            order.pick_putaway_no = pick_putaway_no
            order.last_update_time = int(datetime.now().timestamp())

        await self._db_session.commit()

        if entity.id > 0:
            return entity.id, "保存成功"
        else:
            return 0, "保存失败"

    async def update(self, data: InboundPickPutawayUpdate, current_user: CurrentUser) -> Tuple[bool, str]:
        entity = await self.get_by_id(data.id)

        if entity is None:
            return False, "记录不存在"

        if data.pick_putaway_status is not None:
            if entity.pick_putaway_status == 3:
                return False, "已生成入库单，无法修改"
        
        update_data = {}
        if data.pick_putaway_status is not None:
            update_data["pick_putaway_status"] = data.pick_putaway_status
        if data.putaway_person_id is not None:
            update_data["putaway_person_id"] = data.putaway_person_id
        if data.putaway_person is not None:
            update_data["putaway_person"] = data.putaway_person
        if data.remark is not None:
            update_data["remark"] = data.remark
        
        update_data["last_update_time"] = int(datetime.now().timestamp())
        
        await self.update_with_tenant(data.id, current_user.tenant_id, **update_data)

        return True, "保存成功"

    async def select_location(self, data: InboundPickPutawayItemSelectLocation, current_user: CurrentUser) -> Tuple[bool, str]:
        query = select(InboundPickPutawayItem).where(InboundPickPutawayItem.id == data.id)
        result = await self._db_session.execute(query)
        item = result.scalar_one_or_none()

        if item is None:
            return False, "记录不存在"

        query = select(WarehouseLocation).where(WarehouseLocation.id == data.goods_location_id)
        result = await self._db_session.execute(query)
        location = result.scalar_one_or_none()

        if location is None:
            return False, "库位不存在"

        warehouse_id = 0
        warehouse_name = ""
        warehouse_area_id = 0
        warehouse_area_name = ""
        warehouse_location_name = location.node_name
        
        if location.parent_id > 0:
            area_query = select(WarehouseLocation).where(WarehouseLocation.id == location.parent_id)
            area_result = await self._db_session.execute(area_query)
            area = area_result.scalar_one_or_none()
            
            if area:
                warehouse_area_name = area.node_name
                warehouse_area_id = area.parent_id
                
                if area.parent_id > 0:
                    warehouse_query = select(WarehouseLocation).where(WarehouseLocation.id == area.parent_id)
                    warehouse_result = await self._db_session.execute(warehouse_query)
                    warehouse = warehouse_result.scalar_one_or_none()
                    
                    if warehouse:
                        warehouse_name = warehouse.node_name
                        warehouse_id = warehouse.id

        item.goods_location_id = data.goods_location_id
        item.warehouse_id = warehouse_id
        item.warehouse_name = warehouse_name
        item.warehouse_area_id = warehouse_area_id
        item.warehouse_area_name = warehouse_area_name
        item.warehouse_location_name = warehouse_location_name
        item.last_update_time = int(datetime.now().timestamp())

        await self._db_session.commit()

        return True, "库位选择成功"

    async def update_item(self, data: InboundPickPutawayItemUpdate) -> Tuple[bool, str]:
        query = select(InboundPickPutawayItem).where(InboundPickPutawayItem.id == data.id)
        result = await self._db_session.execute(query)
        item = result.scalar_one_or_none()

        if item is None:
            return False, "记录不存在"

        if data.putaway_qty > item.qty:
            return False, "上架数量不能超过订单数量"

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

        item.putaway_qty = data.putaway_qty
        item.putaway_person_id = data.putaway_person_id
        item.putaway_person = data.putaway_person
        item.putaway_time = data.putaway_time
        item.goods_location_id = data.goods_location_id
        item.warehouse_id = warehouse_id
        item.warehouse_name = warehouse_name
        item.warehouse_area_id = warehouse_area_id
        item.warehouse_area_name = warehouse_area_name
        item.warehouse_location_name = warehouse_location_name
        item.last_update_time = int(datetime.now().timestamp())

        query = select(InboundPickPutaway).where(InboundPickPutaway.id == item.pick_putaway_id)
        result = await self._db_session.execute(query)
        pick_putaway = result.scalar_one_or_none()

        if pick_putaway:
            query = select(func.sum(InboundPickPutawayItem.putaway_qty)).where(
                InboundPickPutawayItem.pick_putaway_id == item.pick_putaway_id
            )
            result = await self._db_session.execute(query)
            total_putaway = result.scalar() or 0
            pick_putaway.putaway_qty = total_putaway
            pick_putaway.last_update_time = int(datetime.now().timestamp())

        await self._db_session.commit()

        return True, "保存成功"

    async def start_putaway(self, id: int, putaway_person_id: int, putaway_person: str, current_user: CurrentUser) -> Tuple[bool, str]:
        entity = await self.get_by_id(id)

        if entity is None:
            return False, "记录不存在"

        if entity.pick_putaway_status != 0:
            return False, "上架单状态不正确"

        await self.update_with_tenant(
            id,
            entity.tenant_id,
            pick_putaway_status=1,
            putaway_person_id=putaway_person_id,
            putaway_person=putaway_person,
            putaway_start_time=int(datetime.now().timestamp()),
            last_update_time=int(datetime.now().timestamp())
        )

        return True, "开始上架成功"

    async def complete_putaway(self, id: int, current_user: CurrentUser) -> Tuple[bool, str]:
        import json
        from app.models.entities.inbound_receipt import InboundReceipt
        from app.models.entities.inbound_receipt_item import InboundReceiptItem
        
        entity = await self.get_by_id(id)

        if entity is None:
            return False, "记录不存在"

        if entity.pick_putaway_status != 1:
            return False, "上架单状态不正确"

        if entity.putaway_qty < entity.total_qty:
            return False, "上架数量不足，无法完成上架"

        query = select(InboundPickPutawayItem).where(InboundPickPutawayItem.pick_putaway_id == id)
        result = await self._db_session.execute(query)
        pick_putaway_items = result.scalars().all()

        order_nos = json.loads(entity.order_nos) if entity.order_nos else [entity.order_no]
        
        query = select(InboundOrder).where(InboundOrder.order_no.in_(order_nos))
        result = await self._db_session.execute(query)
        orders = result.scalars().all()
        
        orders_sorted = sorted(orders, key=lambda x: x.create_time)
        
        for order in orders_sorted:
            query = select(InboundOrderItem).where(InboundOrderItem.order_id == order.id)
            result = await self._db_session.execute(query)
            order_items = result.scalars().all()
            
            order_item_map = {item.id: item for item in order_items}
            
            receipt_items = []
            total_qty = 0
            total_weight = 0
            total_volume = 0
            
            for pick_item in pick_putaway_items:
                order_item_ids = json.loads(pick_item.order_item_ids) if pick_item.order_item_ids else [pick_item.order_item_id]
                
                for order_item_id in order_item_ids:
                    if order_item_id in order_item_map:
                        order_item = order_item_map[order_item_id]
                        
                        qty_ratio = order_item.qty / pick_item.qty
                        item_qty = pick_item.putaway_qty * qty_ratio
                        item_weight = float(pick_item.weight) * qty_ratio
                        item_volume = float(pick_item.volume) * qty_ratio
                        
                        receipt_item = InboundReceiptItem(
                            receipt_id=0,
                            order_item_id=order_item.id,
                            spu_id=pick_item.spu_id,
                            spu_code=pick_item.spu_code,
                            spu_name=pick_item.spu_name,
                            sku_id=pick_item.sku_id,
                            sku_code=pick_item.sku_code,
                            sku_name=pick_item.sku_name,
                            qty=int(item_qty),
                            actual_qty=int(item_qty),
                            weight=item_weight,
                            actual_weight=item_weight,
                            volume=item_volume,
                            actual_volume=item_volume,
                            price=pick_item.price,
                            expiry_date=pick_item.expiry_date,
                            batch_no=pick_item.batch_no,
                            production_date=pick_item.production_date,
                            goods_location_id=pick_item.goods_location_id,
                            warehouse_id=pick_item.warehouse_id,
                            warehouse_name=pick_item.warehouse_name,
                            warehouse_area_id=pick_item.warehouse_area_id,
                            warehouse_area_name=pick_item.warehouse_area_name,
                            warehouse_location_name=pick_item.warehouse_location_name,
                            tenant_id=current_user.tenant_id
                        )
                        receipt_items.append(receipt_item)
                        
                        total_qty += int(item_qty)
                        total_weight += item_weight
                        total_volume += item_volume
            
            if receipt_items:
                import uuid
                receipt_no = f"REC{datetime.now().strftime('%Y%m%d%H%M%S')}{str(uuid.uuid4())[:8].upper()}"
                
                receipt = InboundReceipt(
                    receipt_no=receipt_no,
                    receipt_status=0,
                    pick_putaway_id=entity.id,
                    order_id=order.id,
                    order_no=order.order_no,
                    supplier_id=order.supplier_id,
                    supplier_name=order.supplier_name,
                    warehouse_id=order.warehouse_id,
                    goods_owner_id=order.goods_owner_id,
                    goods_owner_name=order.goods_owner_name,
                    total_qty=total_qty,
                    actual_qty=total_qty,
                    total_weight=total_weight,
                    actual_weight=total_weight,
                    total_volume=total_volume,
                    actual_volume=total_volume,
                    arrival_time=0,
                    unload_time=0,
                    unload_person_id=0,
                    unload_person='',
                    inbound_time=0,
                    inbound_person='',
                    remark='',
                    creator=current_user.user_name,
                    create_time=int(datetime.now().timestamp()),
                    last_update_time=int(datetime.now().timestamp()),
                    tenant_id=current_user.tenant_id
                )
                
                self._db_session.add(receipt)
                await self._db_session.flush()
                
                for receipt_item in receipt_items:
                    receipt_item.receipt_id = receipt.id
                    self._db_session.add(receipt_item)

        await self.update_with_tenant(
            id,
            entity.tenant_id,
            pick_putaway_status=3,
            putaway_end_time=int(datetime.now().timestamp()),
            last_update_time=int(datetime.now().timestamp())
        )

        return True, "完成上架成功"

    async def delete(self, id: int, current_user: CurrentUser) -> Tuple[bool, str]:
        import json
        
        entity = await self.get_by_id(id)

        if entity is None:
            return False, "记录不存在"

        if entity.pick_putaway_status != 0:
            return False, "上架单已处理，无法删除"

        order_nos = json.loads(entity.order_nos) if entity.order_nos else [entity.order_no]
        
        query = select(InboundOrder).where(InboundOrder.order_no.in_(order_nos))
        result = await self._db_session.execute(query)
        orders = result.scalars().all()

        for order in orders:
            order.order_status = 0
            order.pick_putaway_no = ''
            order.last_update_time = int(datetime.now().timestamp())

        await self._db_session.delete(entity)
        await self._db_session.commit()

        return True, "删除成功"
