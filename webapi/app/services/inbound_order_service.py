from datetime import datetime
from typing import List, Tuple, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.entities.inbound_order import InboundOrder
from app.models.entities.inbound_order_item import InboundOrderItem
from app.models.entities.sku import Sku
from app.models.entities.spu import Spu
from app.models.entities.warehouse_location import WarehouseLocation
from app.models.entities.supplier import Supplier
from app.models.entities.goods_owner import GoodsOwner
from app.schemas.inbound_order import (
    InboundOrderCreate,
    InboundOrderUpdate,
    InboundOrderViewModel,
    InboundOrderItemViewModel
)
from app.core.current_user import CurrentUser
from app.repositories.inbound_order_repository import InboundOrderRepository
from app.services.base_service import TenantAwareService


class InboundOrderService(TenantAwareService[InboundOrderRepository, InboundOrder]):
    def __init__(self, db_session: AsyncSession):
        repository = InboundOrderRepository(db_session)
        super().__init__(repository)
        self._db_session = db_session

    async def search(
        self,
        page_index: int = 1,
        page_size: int = 10,
        order_no: Optional[str] = None,
        order_status: Optional[int] = None,
        supplier_id: Optional[int] = None,
        current_user: Optional[CurrentUser] = None
    ) -> Tuple[List[InboundOrderViewModel], int]:
        search_params = {}
        if order_no:
            search_params["inbound_order_code"] = order_no
        if order_status is not None:
            search_params["order_status"] = order_status
        if supplier_id is not None:
            search_params["supplier_id"] = supplier_id
        
        entities, totals = await self._repository.search_by_tenant(
            page_index, page_size, current_user.tenant_id, search_params
        )

        data = []
        for entity in entities:
            data.append(InboundOrderViewModel(
                id=entity.id,
                order_no=entity.order_no,
                order_status=entity.order_status,
                supplier_id=entity.supplier_id,
                supplier_name=entity.supplier_name,
                warehouse_id=entity.warehouse_id,
                warehouse_name=entity.warehouse_name,
                goods_owner_id=entity.goods_owner_id,
                goods_owner_name=entity.goods_owner_name,
                total_qty=entity.total_qty,
                total_weight=float(entity.total_weight),
                total_volume=float(entity.total_volume),
                estimated_arrival_time=entity.estimated_arrival_time,
                remark=entity.remark,
                creator=entity.creator,
                create_time=entity.create_time,
                last_update_time=entity.last_update_time,
                tenant_id=entity.tenant_id,
                items=None
            ))

        return data, totals

    async def get_by_id(self, id: int) -> Optional[InboundOrderViewModel]:
        entity = await self._repository.get_by_id(id)

        if entity is None:
            return None

        items = await self._get_items_by_order_id(id)

        return InboundOrderViewModel(
            id=entity.id,
            order_no=entity.order_no,
            order_status=entity.order_status,
            supplier_id=entity.supplier_id,
            supplier_name=entity.supplier_name,
            warehouse_id=entity.warehouse_id,
            warehouse_name=entity.warehouse_name,
            goods_owner_id=entity.goods_owner_id,
            goods_owner_name=entity.goods_owner_name,
            total_qty=entity.total_qty,
            total_weight=float(entity.total_weight),
            total_volume=float(entity.total_volume),
            estimated_arrival_time=entity.estimated_arrival_time,
            remark=entity.remark,
            creator=entity.creator,
            create_time=entity.create_time,
            last_update_time=entity.last_update_time,
            tenant_id=entity.tenant_id,
            items=items
        )

    async def _get_items_by_order_id(self, order_id: int) -> List[InboundOrderItemViewModel]:
        query = select(InboundOrderItem, Sku, Spu).join(Sku, InboundOrderItem.sku_id == Sku.id)
        query = query.join(Spu, Sku.spu_id == Spu.id)
        query = query.where(InboundOrderItem.order_id == order_id)
        result = await self._db_session.execute(query)
        rows = result.all()

        items = []
        for row in rows:
            entity, sku, spu = row
            items.append(InboundOrderItemViewModel(
                id=entity.id,
                order_id=entity.order_id,
                spu_id=entity.spu_id,
                spu_code=spu.spu_code if spu else None,
                spu_name=spu.spu_name if spu else None,
                sku_id=entity.sku_id,
                sku_code=sku.sku_code if sku else None,
                sku_name=sku.sku_name if sku else None,
                qty=entity.qty,
                weight=float(entity.weight),
                volume=float(entity.volume),
                price=float(entity.price),
                expiry_date=entity.expiry_date,
                tenant_id=entity.tenant_id
            ))

        return items

    async def create(self, data: InboundOrderCreate, current_user: CurrentUser) -> Tuple[int, str]:
        query = select(Supplier).where(Supplier.id == data.supplier_id)
        result = await self._db_session.execute(query)
        supplier = result.scalar_one_or_none()

        if supplier is None:
            return 0, "供应商不存在"

        supplier_name = data.supplier_name if data.supplier_name else supplier.supplier_name

        query = select(WarehouseLocation).where(
            WarehouseLocation.id == data.warehouse_id,
            WarehouseLocation.node_type == 1
        )
        result = await self._db_session.execute(query)
        warehouse = result.scalar_one_or_none()

        if warehouse is None:
            return 0, "仓库不存在"

        warehouse_name = warehouse.node_name

        goods_owner_name = data.goods_owner_name
        if data.goods_owner_id > 0:
            query = select(GoodsOwner).where(GoodsOwner.id == data.goods_owner_id)
            result = await self._db_session.execute(query)
            goods_owner = result.scalar_one_or_none()

            if goods_owner is None:
                return 0, "货主不存在"
            
            if not goods_owner_name:
                goods_owner_name = goods_owner.goods_owner_name

        import uuid
        order_no = f"IN{datetime.now().strftime('%Y%m%d%H%M%S')}{str(uuid.uuid4())[:8].upper()}"

        total_qty = 0
        total_weight = 0
        total_volume = 0

        for item in data.items:
            query = select(Spu).where(Spu.id == item.spu_id)
            result = await self._db_session.execute(query)
            spu = result.scalar_one_or_none()

            if spu is None:
                return 0, f"SPU ID {item.spu_id} 不存在"

            sku = await self.get_one_entity_by_tenant(
                Sku,
                current_user.tenant_id,
                filters={"id": item.sku_id}
            )

            if sku is None:
                return 0, f"SKU ID {item.sku_id} 不存在"

            total_qty += item.qty
            total_weight += item.weight
            total_volume += item.volume

        entity = await self.create_with_tenant(
            current_user.tenant_id,
            order_no=order_no,
            order_status=0,
            supplier_id=data.supplier_id,
            supplier_name=supplier_name,
            warehouse_id=data.warehouse_id,
            warehouse_name=warehouse_name,
            goods_owner_id=data.goods_owner_id,
            goods_owner_name=goods_owner_name or '',
            total_qty=total_qty,
            total_weight=total_weight,
            total_volume=total_volume,
            estimated_arrival_time=data.estimated_arrival_time or int(datetime.now().timestamp()),
            remark=data.remark,
            creator=current_user.user_name,
            create_time=int(datetime.now().timestamp()),
            last_update_time=int(datetime.now().timestamp())
        )

        for item in data.items:
            item_price = item.price
            if item_price is None:
                sku = await self.get_one_entity_by_tenant(
                    Sku,
                    current_user.tenant_id,
                    filters={"id": item.sku_id}
                )
                item_price = sku.price if sku else 0

            query = select(Spu).where(Spu.id == item.spu_id)
            result = await self._db_session.execute(query)
            spu = result.scalar_one_or_none()

            query = select(Sku).where(Sku.id == item.sku_id)
            result = await self._db_session.execute(query)
            sku = result.scalar_one_or_none()

            item_entity = InboundOrderItem(
                order_id=entity.id,
                spu_id=item.spu_id,
                spu_code=spu.spu_code if spu else '',
                spu_name=spu.spu_name if spu else '',
                sku_id=item.sku_id,
                sku_code=sku.sku_code if sku else '',
                sku_name=sku.sku_name if sku else '',
                qty=item.qty,
                weight=item.weight,
                volume=item.volume,
                price=item_price,
                expiry_date=item.expiry_date,
                batch_no=item.batch_no or '',
                production_date=item.production_date or 0,
                tenant_id=current_user.tenant_id
            )
            self._db_session.add(item_entity)

        await self._db_session.commit()

        if entity.id > 0:
            return entity.id, "保存成功"
        else:
            return 0, "保存失败"

    async def update(self, data: InboundOrderUpdate) -> Tuple[bool, str]:
        entity = await self._repository.get_by_id(data.id)

        if entity is None:
            return False, "记录不存在"

        if entity.order_status != 0:
            return False, "订单已处理，无法修改"

        update_data = {}
        if data.supplier_id is not None:
            update_data["supplier_id"] = data.supplier_id
        if data.supplier_name is not None:
            update_data["supplier_name"] = data.supplier_name
        if data.warehouse_id is not None:
            update_data["warehouse_id"] = data.warehouse_id
            query = select(WarehouseLocation).where(
                WarehouseLocation.id == data.warehouse_id,
                WarehouseLocation.node_type == 1
            )
            result = await self._db_session.execute(query)
            warehouse = result.scalar_one_or_none()
            if warehouse:
                update_data["warehouse_name"] = warehouse.node_name
        if data.goods_owner_id is not None:
            update_data["goods_owner_id"] = data.goods_owner_id
        if data.goods_owner_name is not None:
            update_data["goods_owner_name"] = data.goods_owner_name
        if data.estimated_arrival_time is not None:
            update_data["estimated_arrival_time"] = data.estimated_arrival_time
        if data.remark is not None:
            update_data["remark"] = data.remark

        update_data["last_update_time"] = int(datetime.now().timestamp())

        if update_data:
            await self.update_with_tenant(data.id, entity.tenant_id, **update_data)

        return True, "保存成功"

    async def delete(self, id: int) -> Tuple[bool, str]:
        entity = await self._repository.get_by_id(id)

        if entity is None:
            return False, "记录不存在"

        if entity.order_status != 0:
            return False, "订单已处理，无法删除"

        result = await self._repository.delete(id)

        if not result:
            return False, "删除失败"

        return True, "删除成功"
