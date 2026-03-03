from datetime import datetime
from typing import List, Tuple, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.entities.stockprocess import Stockprocess
from app.models.entities.stockprocessdetail import Stockprocessdetail
from app.schemas.stockprocess import StockprocessCreate, StockprocessUpdate, StockprocessViewModel
from app.core.current_user import CurrentUser


class StockprocessService:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def search(
        self,
        page_index: int = 1,
        page_size: int = 10,
        job_code: Optional[str] = None,
        current_user: Optional[CurrentUser] = None
    ) -> Tuple[List[StockprocessViewModel], int]:
        query = select(Stockprocess)
        query = query.where(Stockprocess.tenant_id == current_user.tenant_id if current_user else 1)

        if job_code:
            query = query.where(Stockprocess.job_code.like(f'%{job_code}%'))

        total_query = select(Stockprocess.id).where(query.whereclause)
        total_result = await self.db_session.execute(total_query)
        totals = len(total_result.scalars().all())

        query = query.order_by(Stockprocess.create_time.desc())
        query = query.offset((page_index - 1) * page_size).limit(page_size)

        result = await self.db_session.execute(query)
        entities = result.scalars().all()

        data = [
            StockprocessViewModel(
                id=entity.id,
                job_code=entity.job_code,
                job_type=entity.job_type,
                process_status=entity.process_status,
                processor=entity.processor,
                process_time=entity.process_time,
                creator=entity.creator,
                create_time=entity.create_time,
                last_update_time=entity.last_update_time,
                tenant_id=entity.tenant_id
            )
            for entity in entities
        ]

        return data, totals

    async def get_by_id(self, id: int) -> Optional[StockprocessViewModel]:
        query = select(Stockprocess).where(Stockprocess.id == id)

        result = await self.db_session.execute(query)
        entity = result.scalar_one_or_none()

        if entity is None:
            return None

        return StockprocessViewModel(
            id=entity.id,
            job_code=entity.job_code,
            job_type=entity.job_type,
            process_status=entity.process_status,
            processor=entity.processor,
            process_time=entity.process_time,
            creator=entity.creator,
            create_time=entity.create_time,
            last_update_time=entity.last_update_time,
            tenant_id=entity.tenant_id
        )

    async def create(self, data: StockprocessCreate, current_user: CurrentUser) -> Tuple[int, str]:
        entity = Stockprocess(
            job_code=data.job_code,
            job_type=data.job_type,
            process_status=False,
            processor='',
            process_time=0,
            creator=current_user.user_name,
            create_time=int(datetime.now().timestamp()),
            last_update_time=int(datetime.now().timestamp()),
            tenant_id=current_user.tenant_id
        )

        self.db_session.add(entity)
        await self.db_session.commit()

        if entity.id > 0:
            return entity.id, "保存成功"
        else:
            return 0, "保存失败"

    async def update(self, data: StockprocessUpdate) -> Tuple[bool, str]:
        query = select(Stockprocess).where(Stockprocess.id == data.id)
        result = await self.db_session.execute(query)
        entity = result.scalar_one_or_none()

        if entity is None:
            return False, "记录不存在"

        entity.job_code = data.job_code
        entity.job_type = data.job_type
        entity.last_update_time = int(datetime.now().timestamp())

        await self.db_session.commit()

        return True, "保存成功"

    async def delete(self, id: int) -> Tuple[bool, str]:
        query = select(Stockprocess).where(Stockprocess.id == id)
        result = await self.db_session.execute(query)
        entity = result.scalar_one_or_none()

        if entity is None:
            return False, "记录不存在"

        if entity.process_status:
            return False, "已加工，无法删除"

        await self.db_session.delete(entity)
        await self.db_session.commit()

        return True, "删除成功"
