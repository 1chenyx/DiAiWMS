from datetime import datetime
from typing import List, Tuple, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.entities.user_role import UserRole
from app.schemas.user_role import UserRoleCreate, UserRoleUpdate, UserRoleViewModel
from app.core.current_user import CurrentUser
from app.repositories.user_role_repository import UserRoleRepository
from app.services.base_service import TenantAwareService


class UserRoleService(TenantAwareService[UserRoleRepository, UserRole]):
    def __init__(self, db_session: AsyncSession):
        repository = UserRoleRepository(db_session)
        super().__init__(repository)
        self._db_session = db_session

    async def search(
        self,
        page_index: int = 1,
        page_size: int = 10,
        role_name: Optional[str] = None,
        current_user: Optional[CurrentUser] = None
    ) -> Tuple[List[UserRoleViewModel], int]:
        filters = {}
        if role_name:
            filters["role_name"] = f"%{role_name}%"
        
        entities, totals = await self.page_query_by_tenant(
            page_index=page_index,
            page_size=page_size,
            tenant_id=current_user.tenant_id if current_user else "",
            filters=filters
        )

        data = [
            UserRoleViewModel(
                id=entity.id,
                role_name=entity.role_name,
                tenant_id=entity.tenant_id,
                is_valid=entity.is_valid,
                create_time=entity.create_time,
                last_update_time=entity.last_update_time
            )
            for entity in entities
        ]

        return data, totals

    async def get_by_id(self, id: int) -> Optional[UserRoleViewModel]:
        query = select(UserRole).where(UserRole.id == id)

        result = await self._db_session.execute(query)
        entity = result.scalar_one_or_none()

        if entity is None:
            return None

        return UserRoleViewModel(
            id=entity.id,
            role_name=entity.role_name,
            tenant_id=entity.tenant_id,
            is_valid=entity.is_valid,
            create_time=entity.create_time,
            last_update_time=entity.last_update_time
        )

    async def create(self, data: UserRoleCreate, current_user: CurrentUser) -> Tuple[int, str]:
        entity = await self.create_with_tenant(
            current_user.tenant_id,
            role_name=data.role_name,
            is_valid=True,
            create_time=int(datetime.now().timestamp()),
            last_update_time=int(datetime.now().timestamp())
        )

        if entity.id > 0:
            return entity.id, "保存成功"
        else:
            return 0, "保存失败"

    async def update(self, data: UserRoleUpdate, current_user: CurrentUser) -> Tuple[bool, str]:
        entity = await self.get_by_id(data.id)

        if entity is None:
            return False, "记录不存在"

        await self.update_with_tenant(
            data.id,
            entity.tenant_id,
            role_name=data.role_name,
            is_valid=data.is_valid,
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
