from datetime import datetime
from typing import List, Tuple, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.entities.freightfee import Freightfee
from app.schemas.freightfee import FreightfeeCreate, FreightfeeUpdate, FreightfeeViewModel
from app.core.current_user import CurrentUser
from app.repositories.freightfee_repository import FreightFeeRepository
from app.services.base_service import TenantAwareService


class FreightfeeService(TenantAwareService[FreightFeeRepository, Freightfee]):
    def __init__(self, db_session: AsyncSession):
        repository = FreightFeeRepository(db_session)
        super().__init__(repository)
        self._db_session = db_session

    async def search(
        self,
        page_index: int = 1,
        page_size: int = 10,
        carrier: Optional[str] = None,
        departure_city: Optional[str] = None,
        arrival_city: Optional[str] = None,
        current_user: Optional[CurrentUser] = None
    ) -> Tuple[List[FreightfeeViewModel], int]:
        filters = {}
        if carrier:
            filters["carrier"] = f"%{carrier}%"
        if departure_city:
            filters["departure_city"] = f"%{departure_city}%"
        if arrival_city:
            filters["arrival_city"] = f"%{arrival_city}%"
        
        entities, totals = await self.page_query_by_tenant(
            page_index=page_index,
            page_size=page_size,
            tenant_id=current_user.tenant_id if current_user else "1",
            filters=filters
        )

        result_data = [
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

        return result_data, totals

    async def get_by_id(self, id: int) -> Optional[FreightfeeViewModel]:
        query = select(Freightfee).where(Freightfee.id == id)

        result = await self._db_session.execute(query)
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
        entity = await self.create_with_tenant(
            current_user.tenant_id if current_user else "1",
            carrier=data.carrier,
            departure_city=data.departure_city,
            arrival_city=data.arrival_city,
            price_per_weight=data.price_per_weight,
            price_per_volume=data.price_per_volume,
            min_payment=data.min_payment,
            creator=current_user.user_name if current_user else '',
            create_time=int(datetime.now().timestamp()),
            last_update_time=int(datetime.now().timestamp()),
            is_valid=True
        )

        if entity.id > 0:
            return entity.id, "保存成功"
        else:
            return 0, "保存失败"

    async def update(self, data: FreightfeeUpdate, current_user: CurrentUser) -> Tuple[bool, str]:
        entity = await self.get_by_id(data.id)

        if entity is None:
            return False, "记录不存在"

        update_data = {
            "carrier": data.carrier,
            "departure_city": data.departure_city,
            "arrival_city": data.arrival_city,
            "price_per_weight": data.price_per_weight,
            "price_per_volume": data.price_per_volume,
            "min_payment": data.min_payment,
            "is_valid": data.is_valid,
            "last_update_time": int(datetime.now().timestamp())
        }

        await self.update_with_tenant(data.id, current_user.tenant_id if current_user else "1", **update_data)

        return True, "保存成功"

    async def delete(self, id: int) -> Tuple[bool, str]:
        query = select(Freightfee).where(Freightfee.id == id)
        result = await self._db_session.execute(query)
        entity = result.scalar_one_or_none()

        if entity is None:
            return False, "记录不存在"

        await self._db_session.delete(entity)
        await self._db_session.commit()

        return True, "删除成功"
