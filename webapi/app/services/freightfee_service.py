from datetime import datetime
from typing import List, Tuple, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.entities.freightfee import Freightfee
from app.schemas.freightfee import FreightfeeCreate, FreightfeeUpdate, FreightfeeViewModel
from app.core.current_user import CurrentUser


class FreightfeeService:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def search(
        self,
        page_index: int = 1,
        page_size: int = 10,
        carrier: Optional[str] = None,
        departure_city: Optional[str] = None,
        arrival_city: Optional[str] = None,
        current_user: Optional[CurrentUser] = None
    ) -> Tuple[List[FreightfeeViewModel], int]:
        query = select(Freightfee)
        query = query.where(Freightfee.tenant_id == current_user.tenant_id if current_user else 1)

        if carrier:
            query = query.where(Freightfee.carrier.like(f'%{carrier}%'))
        if departure_city:
            query = query.where(Freightfee.departure_city.like(f'%{departure_city}%'))
        if arrival_city:
            query = query.where(Freightfee.arrival_city.like(f'%{arrival_city}%'))

        total_query = select(Freightfee.id).where(query.whereclause)
        total_result = await self.db_session.execute(total_query)
        totals = len(total_result.scalars().all())

        query = query.order_by(Freightfee.create_time.desc())
        query = query.offset((page_index - 1) * page_size).limit(page_size)

        result = await self.db_session.execute(query)
        entities = result.scalars().all()

        data = [
            FreightfeeViewModel(
                id=entity.id,
                carrier=entity.carrier,
                departure_city=entity.departure_city,
                arrival_city=entity.arrival_city,
                price_per_weight=float(entity.price_per_weight),
                price_per_volume=float(entity.price_per_volume),
                min_payment=float(entity.min_payment),
                creator=entity.creator,
                create_time=int(entity.create_time) if entity.create_time else 0,
                last_update_time=int(entity.last_update_time) if entity.last_update_time else 0,
                is_valid=entity.is_valid,
                tenant_id=entity.tenant_id
            )
            for entity in entities
        ]

        return data, totals

    async def get_by_id(self, id: int) -> Optional[FreightfeeViewModel]:
        query = select(Freightfee).where(Freightfee.id == id)

        result = await self.db_session.execute(query)
        entity = result.scalar_one_or_none()

        if entity is None:
            return None

        return FreightfeeViewModel(
            id=entity.id,
            carrier=entity.carrier,
            departure_city=entity.departure_city,
            arrival_city=entity.arrival_city,
            price_per_weight=float(entity.price_per_weight),
            price_per_volume=float(entity.price_per_volume),
            min_payment=float(entity.min_payment),
            creator=entity.creator,
            create_time=int(entity.create_time) if entity.create_time else 0,
            last_update_time=int(entity.last_update_time) if entity.last_update_time else 0,
            is_valid=entity.is_valid,
            tenant_id=entity.tenant_id
        )

    async def create(self, data: FreightfeeCreate, current_user: CurrentUser) -> Tuple[int, str]:
        entity = Freightfee(
            carrier=data.carrier,
            departure_city=data.departure_city,
            arrival_city=data.arrival_city,
            price_per_weight=data.price_per_weight,
            price_per_volume=data.price_per_volume,
            min_payment=data.min_payment,
            creator=current_user.user_name if current_user else '',
            create_time=int(datetime.now().timestamp()),
            last_update_time=int(datetime.now().timestamp()),
            is_valid=True,
            tenant_id=current_user.tenant_id if current_user else 1
        )

        self.db_session.add(entity)
        await self.db_session.commit()

        if entity.id > 0:
            return entity.id, "保存成功"
        else:
            return 0, "保存失败"

    async def update(self, data: FreightfeeUpdate) -> Tuple[bool, str]:
        query = select(Freightfee).where(Freightfee.id == data.id)
        result = await self.db_session.execute(query)
        entity = result.scalar_one_or_none()

        if entity is None:
            return False, "记录不存在"

        entity.carrier = data.carrier
        entity.departure_city = data.departure_city
        entity.arrival_city = data.arrival_city
        entity.price_per_weight = data.price_per_weight
        entity.price_per_volume = data.price_per_volume
        entity.min_payment = data.min_payment
        entity.is_valid = data.is_valid
        entity.last_update_time = int(datetime.now().timestamp())

        await self.db_session.commit()

        return True, "保存成功"

    async def delete(self, id: int) -> Tuple[bool, str]:
        query = select(Freightfee).where(Freightfee.id == id)
        result = await self.db_session.execute(query)
        entity = result.scalar_one_or_none()

        if entity is None:
            return False, "记录不存在"

        await self.db_session.delete(entity)
        await self.db_session.commit()

        return True, "删除成功"
