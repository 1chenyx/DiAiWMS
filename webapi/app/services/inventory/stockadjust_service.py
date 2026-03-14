from datetime import datetime
from typing import List, Tuple, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.entities.inventory.stockadjust import Stockadjust
from app.models.entities.base.sku import Sku
from app.models.entities.base.goods_location import GoodsLocation
from app.schemas.inventory.stockadjust import StockadjustCreate, StockadjustUpdate, StockadjustViewModel
from app.core.current_user import CurrentUser
from app.repositories.inventory.stockadjust_repository import StockadjustRepository
from app.services.base_service import TenantAwareService


class StockadjustService(TenantAwareService[StockadjustRepository, Stockadjust]):
    def __init__(self, db_session: AsyncSession):
        repository = StockadjustRepository(db_session)
        super().__init__(repository)
        self._db_session = db_session

    async def search(
        self,
        page_index: int = 1,
        page_size: int = 10,
        job_code: Optional[str] = None,
        current_user: Optional[CurrentUser] = None
    ) -> Tuple[List[StockadjustViewModel], int]:
        query = select(Stockadjust).join(Sku, Stockadjust.sku_id == Sku.id)
        query = query.join(GoodsLocation, Stockadjust.goods_location_id == GoodsLocation.id)
        query = query.where(Stockadjust.tenant_id == current_user.tenant_id if current_user else 1)

        if job_code:
            query = query.where(Stockadjust.job_code.like(f'%{job_code}%'))

        total_query = select(Stockadjust.id).where(query.whereclause)
        total_result = await self._db_session.execute(total_query)
        totals = len(total_result.scalars().all())

        query = query.order_by(Stockadjust.create_time.desc())
        query = query.offset((page_index - 1) * page_size).limit(page_size)

        result = await self._db_session.execute(query)
        entities = result.scalars().all()

        data = [
            StockadjustViewModel(
                id=entity.id,
                job_code=entity.job_code,
                sku_id=entity.sku_id,
                goods_owner_id=entity.goods_owner_id,
                goods_location_id=entity.goods_location_id,
                qty=entity.qty,
                creator=entity.creator,
                create_time=entity.create_time,
                last_update_time=entity.last_update_time,
                tenant_id=entity.tenant_id,
                is_update_stock=entity.is_update_stock,
                job_type=entity.job_type,
                source_table_id=entity.source_table_id,
                series_number=entity.series_number,
                expiry_date=entity.expiry_date,
                price=entity.price,
                putaway_date=entity.putaway_date,
                sku_code=entity.sku.sku_code if entity.sku else '',
                sku_name=entity.sku.sku_name if entity.sku else '',
                location_code=entity.goods_location.node_name if entity.goods_location else ''
            )
            for entity in entities
        ]

        return data, totals

    async def get_by_id(self, id: int) -> Optional[StockadjustViewModel]:
        query = select(Stockadjust).join(Sku, Stockadjust.sku_id == Sku.id)
        query = query.join(GoodsLocation, Stockadjust.goods_location_id == GoodsLocation.id)
        query = query.where(Stockadjust.id == id)

        result = await self._db_session.execute(query)
        entity = result.scalar_one_or_none()

        if entity is None:
            return None

        return StockadjustViewModel(
            id=entity.id,
            job_code=entity.job_code,
            sku_id=entity.sku_id,
            goods_owner_id=entity.goods_owner_id,
            goods_location_id=entity.goods_location_id,
            qty=entity.qty,
            creator=entity.creator,
            create_time=entity.create_time,
            last_update_time=entity.last_update_time,
            tenant_id=entity.tenant_id,
            is_update_stock=entity.is_update_stock,
            job_type=entity.job_type,
            source_table_id=entity.source_table_id,
            series_number=entity.series_number,
            expiry_date=entity.expiry_date,
            price=entity.price,
            putaway_date=entity.putaway_date,
            sku_code=entity.sku.sku_code if entity.sku else '',
            sku_name=entity.sku.sku_name if entity.sku else '',
            location_code=entity.goods_location.node_name if entity.goods_location else ''
        )

    async def create(self, data: StockadjustCreate, current_user: CurrentUser) -> Tuple[int, str]:
        entity = await self.create_with_tenant(
            current_user.tenant_id,
            job_code=data.job_code,
            sku_id=data.sku_id,
            goods_owner_id=data.goods_owner_id,
            goods_location_id=data.goods_location_id,
            qty=data.qty,
            creator=current_user.user_name,
            create_time=int(datetime.now().timestamp()),
            last_update_time=int(datetime.now().timestamp()),
            is_update_stock=False,
            job_type=data.job_type,
            source_table_id=data.source_table_id,
            series_number=data.series_number,
            expiry_date=data.expiry_date,
            price=data.price,
            putaway_date=data.putaway_date
        )

        if entity.id > 0:
            return entity.id, "保存成功"
        else:
            return 0, "保存失败"

    async def update(self, data: StockadjustUpdate, current_user: CurrentUser) -> Tuple[bool, str]:
        entity = await self.get_by_id(data.id)

        if entity is None:
            return False, "记录不存在"

        await self.update_with_tenant(
            data.id,
            entity.tenant_id,
            job_code=data.job_code,
            sku_id=data.sku_id,
            goods_owner_id=data.goods_owner_id,
            goods_location_id=data.goods_location_id,
            qty=data.qty,
            job_type=data.job_type,
            source_table_id=data.source_table_id,
            series_number=data.series_number,
            expiry_date=data.expiry_date,
            price=data.price,
            putaway_date=data.putaway_date,
            last_update_time=int(datetime.now().timestamp())
        )

        return True, "保存成功"

    async def delete(self, id: int, current_user: CurrentUser) -> Tuple[bool, str]:
        entity = await self.get_by_id(id)

        if entity is None:
            return False, "记录不存在"

        await self._db_session.delete(entity)
        await self._db_session.commit()

        return True, "删除成功"
