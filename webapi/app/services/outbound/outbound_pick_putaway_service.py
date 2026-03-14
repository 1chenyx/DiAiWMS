from datetime import datetime
from typing import List, Tuple, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from app.models.entities.outbound.outbound_pick_putaway import OutboundPickPutaway
from app.models.entities.outbound.outbound_pick_putaway_item import OutboundPickPutawayItem
from app.models.entities.outbound.outbound_order import OutboundOrder
from app.models.entities.outbound.outbound_order_item import OutboundOrderItem
from app.models.entities.inventory.stock import Stock
from app.models.entities.base.sku import Sku
from app.models.entities.base.spu import Spu
from app.models.entities.base.warehouse_location import WarehouseLocation
from app.schemas.outbound.outbound_pick_putaway import (
    OutboundPickPutawayCreate,
    OutboundPickPutawayUpdate,
    OutboundPickPutawayItemUpdate,
    OutboundPickPutawayViewModel,
    OutboundPickPutawayItemViewModel
)
from app.core.current_user import CurrentUser
from app.repositories.outbound.outbound_pick_putaway_repository import OutboundPickPutawayRepository
from app.services.base_service import TenantAwareService
from app.services.outbound.pick_guide_rule_engine import PickGuideRuleEngine, PickRuleConfig, PickStrategyType, LocationSortType


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
                order_ids=entity.order_ids,
                order_no=entity.order_no,
                order_nos=entity.order_nos,
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
            order_ids=entity.order_ids,
            order_no=entity.order_no,
            order_nos=entity.order_nos,
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
                goods_location_code = location.node_name if location else None

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
                batch_no=entity.batch_no,
                production_date=entity.production_date,
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
        # 验证订单是否存在且状态正确
        query = select(OutboundOrder).where(OutboundOrder.id.in_(data.order_ids))
        result = await self._db_session.execute(query)
        orders = result.scalars().all()

        if not orders:
            return 0, "出库订单不存在"

        for order in orders:
            if order.order_status != 0:
                return 0, f"订单 {order.order_no} 已处理，无法生成拣货单"

        # 获取所有订单明细
        all_order_items = []
        order_map = {}
        for order in orders:
            query = select(OutboundOrderItem).where(OutboundOrderItem.order_id == order.id)
            result = await self._db_session.execute(query)
            order_items = result.scalars().all()
            
            if not order_items:
                return 0, f"订单 {order.order_no} 明细不存在"
            
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
                    'weight': float(item.weight),
                    'volume': float(item.volume),
                    'price': float(item.price),
                    'expiry_date': item.expiry_date,
                    'batch_no': item.batch_no or '',
                    'production_date': item.production_date or 0
                }
                all_order_items.append(item_dict)
                order_map[order.id] = order

        # 检查库存是否充足
        for item in all_order_items:
            query = select(func.sum(Stock.qty)).where(
                Stock.sku_id == item['sku_id'],
                Stock.tenant_id == current_user.tenant_id
            )
            result = await self._db_session.execute(query)
            available_stock = result.scalar() or 0

            if available_stock < item['qty']:
                return 0, f"商品 {item['sku_code']} 库存不足，可用库存: {available_stock}，需要: {item['qty']}"

        # 获取可用库存
        sku_ids = list(set(item['sku_id'] for item in all_order_items))
        query = select(Stock).where(
            Stock.sku_id.in_(sku_ids),
            Stock.tenant_id == current_user.tenant_id,
            Stock.qty > 0
        )
        result = await self._db_session.execute(query)
        stocks = result.scalars().all()

        # 转换库存为字典列表
        stock_list = []
        for stock in stocks:
            stock_list.append({
                'sku_id': stock.sku_id,
                'goods_location_id': stock.goods_location_id,
                'qty': stock.qty,
                'warehouse_location_name': stock.warehouse_location_name,
                'warehouse_area_id': stock.warehouse_area_id,
                'warehouse_area_name': stock.warehouse_area_name,
                'batch_no': stock.batch_no,
                'production_date': stock.production_date,
                'expiry_date': stock.expiry_date,
                'putaway_date': stock.putaway_date
            })

        # 使用规则引擎生成拣货指引
        rule_engine = PickGuideRuleEngine(PickRuleConfig(
            pick_strategy=PickStrategyType.FIFO,
            location_sort=LocationSortType.PATH_OPTIMIZE,
            enable_batch_split=True,
            enable_location_split=True,
            enable_same_sku_merge=True
        ))

        pick_guides = rule_engine.generate_pick_guide(all_order_items, stock_list)

        # 创建拣货单
        import uuid
        pick_putaway_no = f"PICK{datetime.now().strftime('%Y%m%d%H%M%S')}{str(uuid.uuid4())[:8].upper()}"
        main_order = orders[0]

        # 计算汇总信息
        total_qty = sum(item['qty'] for item in all_order_items)
        total_weight = sum(item['weight'] for item in all_order_items)
        total_volume = sum(item['volume'] for item in all_order_items)

        entity = await self.create_with_tenant(
            current_user.tenant_id,
            pick_putaway_no=pick_putaway_no,
            pick_putaway_status=0,
            order_id=main_order.id,
            order_ids=','.join(str(order.id) for order in orders),
            order_no=main_order.order_no,
            order_nos=','.join(order.order_no for order in orders),
            customer_id=main_order.customer_id,
            customer_name=main_order.customer_name,
            warehouse_id=main_order.warehouse_id,
            goods_owner_id=main_order.goods_owner_id,
            goods_owner_name=main_order.goods_owner_name,
            total_qty=total_qty,
            picked_qty=0,
            total_weight=total_weight,
            total_volume=total_volume,
            picker_id=0,
            picker='',
            pick_start_time=0,
            pick_end_time=0,
            remark=data.remark,
            creator=current_user.user_name,
            create_time=int(datetime.now().timestamp()),
            last_update_time=int(datetime.now().timestamp())
        )

        # 创建拣货单明细（根据拣货指引）
        for guide in pick_guides:
            item_entity = OutboundPickPutawayItem(
                pick_putaway_id=entity.id,
                order_item_id=0,  # 拣货指引可能包含多个订单的明细
                spu_id=guide['spu_id'],
                spu_code=guide['spu_code'],
                spu_name=guide['spu_name'],
                sku_id=guide['sku_id'],
                sku_code=guide['sku_code'],
                sku_name=guide['sku_name'],
                qty=guide['qty'],
                picked_qty=0,
                weight=0,
                volume=0,
                price=0,
                expiry_date=guide['expiry_date'],
                batch_no=guide['batch_no'],
                production_date=guide['production_date'],
                goods_location_id=guide['goods_location_id'],
                picker_id=0,
                picker='',
                pick_time=0,
                series_number='',
                tenant_id=current_user.tenant_id
            )
            self._db_session.add(item_entity)

        # 更新所有订单状态
        for order in orders:
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
