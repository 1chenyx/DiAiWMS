from datetime import datetime
from typing import List, Tuple, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.entities.rolemenu import Rolemenu
from app.models.entities.user_role import UserRole
from app.models.entities.menu import Menu
from app.schemas.rolemenu import RolemenuCreate, RolemenuUpdate, RolemenuViewModel
from app.core.current_user import CurrentUser


class RolemenuService:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def search(
        self,
        page_index: int = 1,
        page_size: int = 10,
        userrole_id: Optional[int] = None,
        current_user: Optional[CurrentUser] = None
    ) -> Tuple[List[RolemenuViewModel], int]:
        query = select(Rolemenu).join(UserRole, Rolemenu.userrole_id == UserRole.id)
        query = query.where(Rolemenu.tenant_id == current_user.tenant_id if current_user else 1)

        if userrole_id:
            query = query.where(Rolemenu.userrole_id == userrole_id)

        total_query = select(Rolemenu.id).where(query.whereclause)
        total_result = await self.db_session.execute(total_query)
        totals = len(total_result.scalars().all())

        query = query.order_by(Rolemenu.create_time.desc())
        query = query.offset((page_index - 1) * page_size).limit(page_size)

        result = await self.db_session.execute(query)
        entities = result.scalars().all()

        data = [
            RolemenuViewModel(
                id=entity.id,
                userrole_id=entity.userrole_id,
                menu_id=entity.menu_id,
                authority=entity.authority,
                create_time=entity.create_time,
                last_update_time=entity.last_update_time,
                tenant_id=entity.tenant_id,
                menu_actions_authority=entity.menu_actions_authority,
                role_name=entity.user_role.role_name if entity.user_role else ''
            )
            for entity in entities
        ]

        return data, totals

    async def get_by_id(self, id: int) -> Optional[RolemenuViewModel]:
        query = select(Rolemenu).join(UserRole, Rolemenu.userrole_id == UserRole.id)
        query = query.where(Rolemenu.id == id)

        result = await self.db_session.execute(query)
        entity = result.scalar_one_or_none()

        if entity is None:
            return None

        return RolemenuViewModel(
            id=entity.id,
            userrole_id=entity.userrole_id,
            menu_id=entity.menu_id,
            authority=entity.authority,
            create_time=entity.create_time,
            last_update_time=entity.last_update_time,
            tenant_id=entity.tenant_id,
            menu_actions_authority=entity.menu_actions_authority,
            role_name=entity.user_role.role_name if entity.user_role else ''
        )

    async def create(self, data: RolemenuCreate, current_user: CurrentUser) -> Tuple[int, str]:
        entity = Rolemenu(
            userrole_id=data.userrole_id,
            menu_id=data.menu_id,
            authority=data.authority,
            create_time=int(datetime.now().timestamp()),
            last_update_time=int(datetime.now().timestamp()),
            tenant_id=current_user.tenant_id,
            menu_actions_authority=data.menu_actions_authority
        )

        self.db_session.add(entity)
        await self.db_session.commit()

        if entity.id > 0:
            return entity.id, "保存成功"
        else:
            return 0, "保存失败"

    async def update(self, data: RolemenuUpdate) -> Tuple[bool, str]:
        query = select(Rolemenu).where(Rolemenu.id == data.id)
        result = await self.db_session.execute(query)
        entity = result.scalar_one_or_none()

        if entity is None:
            return False, "记录不存在"

        entity.userrole_id = data.userrole_id
        entity.menu_id = data.menu_id
        entity.authority = data.authority
        entity.menu_actions_authority = data.menu_actions_authority
        entity.last_update_time = int(datetime.now().timestamp())

        await self.db_session.commit()

        return True, "保存成功"

    async def delete(self, id: int) -> Tuple[bool, str]:
        query = select(Rolemenu).where(Rolemenu.id == id)
        result = await self.db_session.execute(query)
        entity = result.scalar_one_or_none()

        if entity is None:
            return False, "记录不存在"

        await self.db_session.delete(entity)
        await self.db_session.commit()

        return True, "删除成功"
