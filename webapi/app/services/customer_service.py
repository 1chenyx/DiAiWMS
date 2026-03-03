from datetime import datetime
from typing import List, Tuple, Optional
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.entities.customer import Customer
from app.models.entities.outbound_order import OutboundOrder
from app.schemas.customer import CustomerCreate, CustomerUpdate, CustomerViewModel
from app.core.current_user import CurrentUser
from app.repositories.customer_repository import CustomerRepository
from app.services.base_service import TenantAwareService


class CustomerService(TenantAwareService[CustomerRepository, Customer]):
    """
    客户服务类
    """

    def __init__(self, db_session: AsyncSession):
        repository = CustomerRepository(db_session)
        super().__init__(repository)
        self._db_session = db_session

    async def search(
        self,
        page_index: int = 1,
        page_size: int = 10,
        customer_name: Optional[str] = None,
        current_user: Optional[CurrentUser] = None
    ) -> Tuple[List[CustomerViewModel], int]:
        entities, totals = await self._repository.search_by_tenant(
            page_index, page_size, current_user.tenant_id, customer_name
        )

        data = [
            CustomerViewModel(
                id=entity.id,
                customer_name=entity.customer_name,
                city=entity.city,
                address=entity.address,
                manager=entity.manager,
                email=entity.email,
                contact_tel=entity.contact_tel,
                creator=entity.creator,
                create_time=entity.create_time,
                last_update_time=entity.last_update_time,
                is_valid=entity.is_valid
            )
            for entity in entities
        ]

        return data, totals

    async def get_all(self, current_user: CurrentUser) -> List[CustomerViewModel]:
        entities = await self._repository.get_all(filters={"tenant_id": current_user.tenant_id})

        return [
            CustomerViewModel(
                id=entity.id,
                customer_name=entity.customer_name,
                city=entity.city,
                address=entity.address,
                manager=entity.manager,
                email=entity.email,
                contact_tel=entity.contact_tel,
                creator=entity.creator,
                create_time=entity.create_time,
                last_update_time=entity.last_update_time,
                is_valid=entity.is_valid
            )
            for entity in entities
        ]

    async def get_by_id(self, id: int) -> Optional[CustomerViewModel]:
        entity = await self._repository.get_by_id(id)

        if entity is None:
            return None

        return CustomerViewModel(
            id=entity.id,
            customer_name=entity.customer_name,
            city=entity.city,
            address=entity.address,
            manager=entity.manager,
            email=entity.email,
            contact_tel=entity.contact_tel,
            creator=entity.creator,
            create_time=entity.create_time,
            last_update_time=entity.last_update_time,
            is_valid=entity.is_valid
        )

    async def create(self, data: CustomerCreate, current_user: CurrentUser) -> Tuple[int, str]:
        existing = await self._repository.exists_by_fields({
            "tenant_id": current_user.tenant_id,
            "customer_name": data.customer_name
        })

        if existing:
            return 0, f"客户名称 {data.customer_name} 已存在"

        entity = await self._repository.create(
            customer_name=data.customer_name,
            city=data.city,
            address=data.address,
            manager=data.manager,
            email=data.email,
            contact_tel=data.contact_tel,
            creator=current_user.user_name,
            create_time=int(datetime.now().timestamp()),
            last_update_time=int(datetime.now().timestamp()),
            is_valid=True,
            tenant_id=current_user.tenant_id
        )

        if entity.id > 0:
            return entity.id, "保存成功"
        else:
            return 0, "保存失败"

    async def update(self, data: CustomerUpdate) -> Tuple[bool, str]:
        entity = await self._repository.get_by_id(data.id)

        if entity is None:
            return False, "记录不存在"

        existing = await self._repository.exists_by_fields({
            "tenant_id": entity.tenant_id,
            "customer_name": data.customer_name
        }, exclude_id=data.id)

        if existing:
            return False, f"客户名称 {data.customer_name} 已存在"

        await self._repository.update(
            data.id,
            customer_name=data.customer_name,
            city=data.city,
            address=data.address,
            manager=data.manager,
            email=data.email,
            contact_tel=data.contact_tel,
            last_update_time=int(datetime.now().timestamp())
        )

        return True, "保存成功"

    async def delete(self, id: int) -> Tuple[bool, str]:
        query = select(OutboundOrder).where(OutboundOrder.customer_id == id)
        result = await self._db_session.execute(query)
        existing = result.scalar_one_or_none()

        if existing:
            return False, "存在引用，无法删除"

        result = await self._repository.delete(id)

        if not result:
            return False, "记录不存在"

        return True, "删除成功"
