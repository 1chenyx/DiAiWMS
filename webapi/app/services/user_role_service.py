from datetime import datetime
from typing import List, Tuple, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.entities.user_role import UserRole
from app.schemas.user_role import UserRoleCreate, UserRoleUpdate, UserRoleViewModel
from app.core.current_user import CurrentUser


class UserRoleService:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def search(
        self,
        page_index: int = 1,
        page_size: int = 10,
        role_name: Optional[str] = None,
        current_user: Optional[CurrentUser] = None
    ) -> Tuple[List[UserRoleViewModel], int]:
        query = select(UserRole)
        query = query.where(UserRole.tenant_id == current_user.tenant_id if current_user else 1)

        if role_name:
            query = query.where(UserRole.role_name.like(f'%{role_name}%'))

        total_query = select(UserRole.id).where(query.whereclause)
        total_result = await self.db_session.execute(total_query)
        totals = len(total_result.scalars().all())

        query = query.order_by(UserRole.create_time.desc())
        query = query.offset((page_index - 1) * page_size).limit(page_size)

        result = await self.db_session.execute(query)
        entities = result.scalars().all()

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

        result = await self.db_session.execute(query)
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
        entity = UserRole(
            role_name=data.role_name,
            tenant_id=current_user.tenant_id,
            is_valid=True,
            create_time=int(datetime.now().timestamp()),
            last_update_time=int(datetime.now().timestamp())
        )

        self.db_session.add(entity)
        await self.db_session.commit()

        if entity.id > 0:
            return entity.id, "保存成功"
        else:
            return 0, "保存失败"

    async def update(self, data: UserRoleUpdate) -> Tuple[bool, str]:
        query = select(UserRole).where(UserRole.id == data.id)
        result = await self.db_session.execute(query)
        entity = result.scalar_one_or_none()

        if entity is None:
            return False, "记录不存在"

        entity.role_name = data.role_name
        entity.is_valid = data.is_valid
        entity.last_update_time = int(datetime.now().timestamp())

        await self.db_session.commit()

        return True, "保存成功"

    async def delete(self, id: int) -> Tuple[bool, str]:
        query = select(UserRole).where(UserRole.id == id)
        result = await self.db_session.execute(query)
        entity = result.scalar_one_or_none()

        if entity is None:
            return False, "记录不存在"

        await self.db_session.delete(entity)
        await self.db_session.commit()

        return True, "删除成功"
