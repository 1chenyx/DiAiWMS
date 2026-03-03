from datetime import datetime
from typing import List, Tuple, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.entities.tenant import Tenant
from app.schemas.tenant import TenantCreateViewModel, TenantUpdateViewModel, TenantViewModel
from app.core.current_user import CurrentUser
from app.repositories.tenant_repository import TenantRepository
from app.services.base_service import BaseService


class TenantService(BaseService[TenantRepository, Tenant]):
    """
    租户服务类
    
    提供租户相关的业务逻辑处理,包括租户查询、创建、更新、删除等操作
    """
    def __init__(self, db_session: AsyncSession):
        repository = TenantRepository(db_session)
        super().__init__(repository)
        self._db_session = db_session

    async def search(
        self,
        page_index: int = 1,
        page_size: int = 10,
        tenant_name: Optional[str] = None,
        tenant_code: Optional[str] = None,
        current_user: Optional[CurrentUser] = None
    ) -> Tuple[List[TenantViewModel], int]:
        entities, totals = await self._repository.search(
            page_index, page_size, tenant_name, tenant_code
        )

        data = [
            TenantViewModel(
                id=entity.id,
                tenant_name=entity.tenant_name,
                tenant_code=entity.tenant_code,
                contact_person=entity.contact_person,
                contact_phone=entity.contact_phone,
                contact_email=entity.contact_email,
                address=entity.address,
                description=entity.description,
                is_valid=entity.is_valid,
                creator=entity.creator,
                create_time=entity.create_time,
                last_update_time=entity.last_update_time
            )
            for entity in entities
        ]

        return data, totals

    async def get_by_id(self, id: int) -> Optional[TenantViewModel]:
        entity = await self._repository.get_by_id(id)

        if entity is None:
            return None

        return TenantViewModel(
            id=entity.id,
            tenant_name=entity.tenant_name,
            tenant_code=entity.tenant_code,
            contact_person=entity.contact_person,
            contact_phone=entity.contact_phone,
            contact_email=entity.contact_email,
            address=entity.address,
            description=entity.description,
            is_valid=entity.is_valid,
            creator=entity.creator,
            create_time=entity.create_time,
            last_update_time=entity.last_update_time
        )

    async def create(self, data: TenantCreateViewModel, current_user: CurrentUser) -> Tuple[int, str]:
        entity = await self._repository.create(
            tenant_name=data.tenant_name,
            tenant_code=data.tenant_code,
            contact_person=data.contact_person,
            contact_phone=data.contact_phone,
            contact_email=data.contact_email,
            address=data.address,
            description=data.description,
            is_valid=True,
            creator=current_user.user_name,
            create_time=int(datetime.now().timestamp()),
            last_update_time=int(datetime.now().timestamp())
        )

        if entity.id > 0:
            return entity.id, "保存成功"
        else:
            return 0, "保存失败"

    async def update(self, data: TenantUpdateViewModel) -> Tuple[bool, str]:
        entity = await self._repository.get_by_id(data.id)

        if entity is None:
            return False, "记录不存在"

        await self._repository.update(
            data.id,
            tenant_name=data.tenant_name,
            tenant_code=data.tenant_code,
            contact_person=data.contact_person,
            contact_phone=data.contact_phone,
            contact_email=data.contact_email,
            address=data.address,
            description=data.description,
            is_valid=data.is_valid,
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
