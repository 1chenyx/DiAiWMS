from datetime import datetime
from typing import List, Tuple, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.entities.action_log import ActionLog
from app.schemas.action_log import ActionLogCreate, ActionLogUpdate, ActionLogViewModel
from app.core.current_user import CurrentUser


class ActionLogService:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def search(
        self,
        page_index: int = 1,
        page_size: int = 10,
        vue_path: Optional[str] = None,
        user_name: Optional[str] = None,
        current_user: Optional[CurrentUser] = None
    ) -> Tuple[List[ActionLogViewModel], int]:
        query = select(ActionLog)
        query = query.where(ActionLog.tenant_id == current_user.tenant_id if current_user else 1)

        if vue_path:
            query = query.where(ActionLog.vue_path.like(f'%{vue_path}%'))
        if user_name:
            query = query.where(ActionLog.user_name.like(f'%{user_name}%'))

        total_query = select(ActionLog.id).where(query.whereclause)
        total_result = await self.db_session.execute(total_query)
        totals = len(total_result.scalars().all())

        query = query.order_by(ActionLog.action_time.desc())
        query = query.offset((page_index - 1) * page_size).limit(page_size)

        result = await self.db_session.execute(query)
        entities = result.scalars().all()

        data = [
            ActionLogViewModel(
                id=entity.id,
                vue_path=entity.vue_path,
                user_name=entity.user_name,
                action_content=entity.action_content,
                action_time=int(entity.action_time) if entity.action_time else 0,
                tenant_id=entity.tenant_id
            )
            for entity in entities
        ]

        return data, totals

    async def get_by_id(self, id: int) -> Optional[ActionLogViewModel]:
        query = select(ActionLog).where(ActionLog.id == id)

        result = await self.db_session.execute(query)
        entity = result.scalar_one_or_none()

        if entity is None:
            return None

        return ActionLogViewModel(
            id=entity.id,
            vue_path=entity.vue_path,
            user_name=entity.user_name,
            action_content=entity.action_content,
            action_time=int(entity.action_time) if entity.action_time else 0,
            tenant_id=entity.tenant_id
        )

    async def create(self, data: ActionLogCreate, current_user: CurrentUser) -> Tuple[int, str]:
        entity = ActionLog(
            vue_path=data.vue_path,
            user_name=data.user_name,
            action_content=data.action_content,
            action_time=int(datetime.now().timestamp()),
            tenant_id=current_user.tenant_id
        )

        self.db_session.add(entity)
        await self.db_session.commit()

        if entity.id > 0:
            return entity.id, "保存成功"
        else:
            return 0, "保存失败"

    async def update(self, data: ActionLogUpdate) -> Tuple[bool, str]:
        query = select(ActionLog).where(ActionLog.id == data.id)
        result = await self.db_session.execute(query)
        entity = result.scalar_one_or_none()

        if entity is None:
            return False, "记录不存在"

        entity.vue_path = data.vue_path
        entity.user_name = data.user_name
        entity.action_content = data.action_content

        await self.db_session.commit()

        return True, "保存成功"

    async def delete(self, id: int) -> Tuple[bool, str]:
        query = select(ActionLog).where(ActionLog.id == id)
        result = await self.db_session.execute(query)
        entity = result.scalar_one_or_none()

        if entity is None:
            return False, "记录不存在"

        await self.db_session.delete(entity)
        await self.db_session.commit()

        return True, "删除成功"
