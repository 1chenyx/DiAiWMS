from datetime import datetime
from typing import List, Tuple, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from app.models.entities.goods_owner import GoodsOwner
from app.schemas.goods_owner import GoodsOwnerCreate, GoodsOwnerUpdate, GoodsOwnerViewModel
from app.core.current_user import CurrentUser
from app.repositories.goods_owner_repository import GoodsOwnerRepository
from app.services.base_service import TenantAwareService


class GoodsOwnerService(TenantAwareService[GoodsOwnerRepository, GoodsOwner]):
    def __init__(self, db_session: AsyncSession):
        repository = GoodsOwnerRepository(db_session)
        super().__init__(repository)
        self._db_session = db_session

    async def search(
        self,
        page_index: int = 1,
        page_size: int = 10,
        goods_owner_name: Optional[str] = None,
        current_user: Optional[CurrentUser] = None
    ) -> Tuple[List[GoodsOwnerViewModel], int]:
        entities, totals = await self._repository.search_by_tenant(
            page_index, page_size, current_user.tenant_id, goods_owner_name
        )

        data = [
            GoodsOwnerViewModel(
                id=entity.id,
                goods_owner_name=entity.goods_owner_name,
                city=entity.city,
                address=entity.address,
                manager=entity.manager,
                contact_tel=entity.contact_tel,
                creator=entity.creator,
                create_time=entity.create_time,
                last_update_time=entity.last_update_time,
                is_valid=entity.is_valid
            )
            for entity in entities
        ]

        return data, totals

    async def get_all(self, current_user: CurrentUser) -> List[GoodsOwnerViewModel]:
        entities = await self._repository.get_by_tenant(current_user.tenant_id)

        return [
            GoodsOwnerViewModel(
                id=entity.id,
                goods_owner_name=entity.goods_owner_name,
                city=entity.city,
                address=entity.address,
                manager=entity.manager,
                contact_tel=entity.contact_tel,
                creator=entity.creator,
                create_time=entity.create_time,
                last_update_time=entity.last_update_time,
                is_valid=entity.is_valid
            )
            for entity in entities
        ]

    async def get_by_id(self, id: int) -> Optional[GoodsOwnerViewModel]:
        entity = await self._repository.get_by_id(id)

        if entity is None:
            return None

        return GoodsOwnerViewModel(
            id=entity.id,
            goods_owner_name=entity.goods_owner_name,
            city=entity.city,
            address=entity.address,
            manager=entity.manager,
            contact_tel=entity.contact_tel,
            creator=entity.creator,
            create_time=entity.create_time,
            last_update_time=entity.last_update_time,
            is_valid=entity.is_valid
        )

    async def create(self, data: GoodsOwnerCreate, current_user: CurrentUser) -> Tuple[int, str]:
        existing = await self._repository.exists_by_fields({
            "tenant_id": current_user.tenant_id,
            "goods_owner_name": data.goods_owner_name
        })

        if existing:
            return 0, f"货主名称 {data.goods_owner_name} 已存在"

        entity = await self._repository.create(
            goods_owner_name=data.goods_owner_name,
            city=data.city,
            address=data.address,
            manager=data.manager,
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

    async def update(self, data: GoodsOwnerUpdate) -> Tuple[bool, str]:
        entity = await self._repository.get_by_id(data.id)

        if entity is None:
            return False, "记录不存在"

        existing = await self._repository.exists_by_fields({
            "tenant_id": entity.tenant_id,
            "goods_owner_name": data.goods_owner_name
        }, exclude_id=data.id)

        if existing:
            return False, f"货主名称 {data.goods_owner_name} 已存在"

        await self._repository.update(
            data.id,
            goods_owner_name=data.goods_owner_name,
            city=data.city,
            address=data.address,
            manager=data.manager,
            contact_tel=data.contact_tel,
            last_update_time=int(datetime.now().timestamp())
        )

        return True, "保存成功"

    async def delete(self, id: int) -> Tuple[bool, str]:
        entity = await self._repository.get_by_id(id)

        if entity is None:
            return False, "记录不存在"

        result = await self._repository.delete(id)

        if not result:
            return False, "删除失败"

        return True, "删除成功"
