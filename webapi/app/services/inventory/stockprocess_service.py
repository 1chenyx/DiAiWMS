from datetime import datetime
from typing import List, Tuple, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.entities.inventory.stockprocess import Stockprocess
from app.models.entities.inventory.stockprocessdetail import Stockprocessdetail
from app.schemas.inventory.stockprocess import StockprocessCreate, StockprocessUpdate, StockprocessViewModel
from app.core.current_user import CurrentUser
from app.repositories.inventory.stockprocess_repository import StockprocessRepository
from app.services.base_service import TenantAwareService


class StockprocessService(TenantAwareService[StockprocessRepository, Stockprocess]):
    def __init__(self, db_session: AsyncSession):
        repository = StockprocessRepository(db_session)
        super().__init__(repository)
        self._db_session = db_session

    async def search(
        self,
        page_index: int = 1,
        page_size: int = 10,
        job_code: Optional[str] = None,
        current_user: Optional[CurrentUser] = None
    ) -> Tuple[List[StockprocessViewModel], int]:
        filters = {}
        if job_code:
            filters["job_code"] = f"%{job_code}%"
        
        entities, totals = await self.page_query_by_tenant(
            page_index=page_index,
            page_size=page_size,
            tenant_id=current_user.tenant_id if current_user else "",
            filters=filters
        )

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

        result = await self._db_session.execute(query)
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
        entity = await self.create_with_tenant(
            current_user.tenant_id,
            job_code=data.job_code,
            job_type=data.job_type,
            process_status=False,
            processor='',
            process_time=0,
            creator=current_user.user_name,
            create_time=int(datetime.now().timestamp()),
            last_update_time=int(datetime.now().timestamp())
        )

        if entity.id > 0:
            return entity.id, "保存成功"
        else:
            return 0, "保存失败"

    async def update(self, data: StockprocessUpdate, current_user: CurrentUser) -> Tuple[bool, str]:
        entity = await self.get_by_id(data.id)

        if entity is None:
            return False, "记录不存在"

        await self.update_with_tenant(
            data.id,
            entity.tenant_id,
            job_code=data.job_code,
            job_type=data.job_type,
            last_update_time=int(datetime.now().timestamp())
        )

        return True, "保存成功"

    async def delete(self, id: int, current_user: CurrentUser) -> Tuple[bool, str]:
        entity = await self.get_by_id(id)

        if entity is None:
            return False, "记录不存在"

        if entity.process_status:
            return False, "已加工，无法删除"

        await self._db_session.delete(entity)
        await self._db_session.commit()

        return True, "删除成功"
