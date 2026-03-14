from datetime import datetime
from typing import List, Tuple, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.entities.inventory.stocktaking import Stocktaking
from app.models.entities.base.sku import Sku
from app.models.entities.base.goods_location import GoodsLocation
from app.schemas.inventory.stocktaking import StocktakingCreate, StocktakingUpdate, StocktakingViewModel
from app.core.current_user import CurrentUser
from app.repositories.inventory.stocktaking_repository import StocktakingRepository
from app.services.base_service import TenantAwareService


class StocktakingService(TenantAwareService[StocktakingRepository, Stocktaking]):
    def __init__(self, db_session: AsyncSession):
        repository = StocktakingRepository(db_session)
        super().__init__(repository)
        self._db_session = db_session

    async def search(
        self,
        page_index: int = 1,
        page_size: int = 10,
        job_code: Optional[str] = None,
        current_user: Optional[CurrentUser] = None
    ) -> Tuple[List[StocktakingViewModel], int]:
        query = select(Stocktaking).join(Sku, Stocktaking.sku_id == Sku.id)
        query = query.join(GoodsLocation, Stocktaking.goods_location_id == GoodsLocation.id)
        query = query.where(Stocktaking.tenant_id == current_user.tenant_id if current_user else 1)

        if job_code:
            query = query.where(Stocktaking.job_code.like(f'%{job_code}%'))

        total_query = select(Stocktaking.id).where(query.whereclause)
        total_result = await self._db_session.execute(total_query)
        totals = len(total_result.scalars().all())

        query = query.order_by(Stocktaking.create_time.desc())
        query = query.offset((page_index - 1) * page_size).limit(page_size)

        result = await self._db_session.execute(query)
        entities = result.scalars().all()

        data = [
            StocktakingViewModel(
                id=entity.id,
                job_code=entity.job_code,
                job_status=entity.job_status,
                sku_id=entity.sku_id,
                goods_owner_id=entity.goods_owner_id,
                goods_location_id=entity.goods_location_id,
                series_number=entity.series_number,
                expiry_date=entity.expiry_date,
                price=entity.price,
                putaway_date=entity.putaway_date,
                book_qty=entity.book_qty,
                counted_qty=entity.counted_qty,
                difference_qty=entity.difference_qty,
                creator=entity.creator,
                create_time=entity.create_time,
                last_update_time=entity.last_update_time,
                tenant_id=entity.tenant_id,
                handler=entity.handler,
                handle_time=entity.handle_time,
                sku_code=entity.sku.sku_code if entity.sku else '',
                sku_name=entity.sku.sku_name if entity.sku else '',
                location_code=entity.goods_location.node_name if entity.goods_location else ''
            )
            for entity in entities
        ]

        return data, totals

    async def get_by_id(self, id: int) -> Optional[StocktakingViewModel]:
        query = select(Stocktaking).join(Sku, Stocktaking.sku_id == Sku.id)
        query = query.join(GoodsLocation, Stocktaking.goods_location_id == GoodsLocation.id)
        query = query.where(Stocktaking.id == id)

        result = await self._db_session.execute(query)
        entity = result.scalar_one_or_none()

        if entity is None:
            return None

        return StocktakingViewModel(
            id=entity.id,
            job_code=entity.job_code,
            job_status=entity.job_status,
            sku_id=entity.sku_id,
            goods_owner_id=entity.goods_owner_id,
            goods_location_id=entity.goods_location_id,
            series_number=entity.series_number,
            expiry_date=entity.expiry_date,
            price=entity.price,
            putaway_date=entity.putaway_date,
            book_qty=entity.book_qty,
            counted_qty=entity.counted_qty,
            difference_qty=entity.difference_qty,
            creator=entity.creator,
            create_time=entity.create_time,
            last_update_time=entity.last_update_time,
            tenant_id=entity.tenant_id,
            handler=entity.handler,
            handle_time=entity.handle_time,
            sku_code=entity.sku.sku_code if entity.sku else '',
            sku_name=entity.sku.sku_name if entity.sku else '',
            location_code=entity.goods_location.node_name if entity.goods_location else ''
        )

    async def create(self, data: StocktakingCreate, current_user: CurrentUser) -> Tuple[int, str]:
        entity = await self.create_with_tenant(
            current_user.tenant_id,
            job_code=data.job_code,
            job_status=False,
            sku_id=data.sku_id,
            goods_owner_id=data.goods_owner_id,
            goods_location_id=data.goods_location_id,
            series_number=data.series_number,
            expiry_date=data.expiry_date,
            price=data.price,
            putaway_date=data.putaway_date,
            book_qty=data.book_qty,
            counted_qty=0,
            difference_qty=0,
            creator=current_user.user_name,
            create_time=int(datetime.now().timestamp()),
            last_update_time=int(datetime.now().timestamp()),
            handler='',
            handle_time=0
        )

        if entity.id > 0:
            return entity.id, "保存成功"
        else:
            return 0, "保存失败"

    async def update(self, data: StocktakingUpdate, current_user: CurrentUser) -> Tuple[bool, str]:
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
            series_number=data.series_number,
            expiry_date=data.expiry_date,
            price=data.price,
            putaway_date=data.putaway_date,
            book_qty=data.book_qty,
            counted_qty=data.counted_qty,
            difference_qty=data.counted_qty - data.book_qty,
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
