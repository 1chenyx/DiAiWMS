from datetime import datetime
from typing import List, Tuple, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.entities.print_solution import PrintSolution
from app.schemas.print_solution import PrintSolutionCreate, PrintSolutionUpdate, PrintSolutionViewModel
from app.core.current_user import CurrentUser


class PrintSolutionService:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def search(
        self,
        page_index: int = 1,
        page_size: int = 10,
        vue_path: Optional[str] = None,
        solution_name: Optional[str] = None,
        current_user: Optional[CurrentUser] = None
    ) -> Tuple[List[PrintSolutionViewModel], int]:
        query = select(PrintSolution)
        query = query.where(PrintSolution.tenant_id == current_user.tenant_id if current_user else 1)

        if vue_path:
            query = query.where(PrintSolution.vue_path.like(f'%{vue_path}%'))
        if solution_name:
            query = query.where(PrintSolution.solution_name.like(f'%{solution_name}%'))

        total_query = select(PrintSolution.id).where(query.whereclause)
        total_result = await self.db_session.execute(total_query)
        totals = len(total_result.scalars().all())

        query = query.order_by(PrintSolution.last_update_time.desc())
        query = query.offset((page_index - 1) * page_size).limit(page_size)

        result = await self.db_session.execute(query)
        entities = result.scalars().all()

        data = [
            PrintSolutionViewModel(
                id=entity.id,
                vue_path=entity.vue_path,
                tab_page=entity.tab_page,
                solution_name=entity.solution_name,
                config_json=entity.config_json,
                report_length=float(entity.report_length),
                report_width=float(entity.report_width),
                report_direction=entity.report_direction,
                last_update_time=int(entity.last_update_time) if entity.last_update_time else 0,
                tenant_id=entity.tenant_id
            )
            for entity in entities
        ]

        return data, totals

    async def get_by_id(self, id: int) -> Optional[PrintSolutionViewModel]:
        query = select(PrintSolution).where(PrintSolution.id == id)

        result = await self.db_session.execute(query)
        entity = result.scalar_one_or_none()

        if entity is None:
            return None

        return PrintSolutionViewModel(
            id=entity.id,
            vue_path=entity.vue_path,
            tab_page=entity.tab_page,
            solution_name=entity.solution_name,
            config_json=entity.config_json,
            report_length=float(entity.report_length),
            report_width=float(entity.report_width),
            report_direction=entity.report_direction,
            last_update_time=int(entity.last_update_time) if entity.last_update_time else 0,
            tenant_id=entity.tenant_id
        )

    async def create(self, data: PrintSolutionCreate, current_user: CurrentUser) -> Tuple[int, str]:
        entity = PrintSolution(
            vue_path=data.vue_path,
            tab_page=data.tab_page,
            solution_name=data.solution_name,
            config_json=data.config_json,
            report_length=data.report_length,
            report_width=data.report_width,
            report_direction=data.report_direction,
            last_update_time=int(datetime.now().timestamp()),
            tenant_id=current_user.tenant_id if current_user else 1
        )

        self.db_session.add(entity)
        await self.db_session.commit()

        if entity.id > 0:
            return entity.id, "保存成功"
        else:
            return 0, "保存失败"

    async def update(self, data: PrintSolutionUpdate) -> Tuple[bool, str]:
        query = select(PrintSolution).where(PrintSolution.id == data.id)
        result = await self.db_session.execute(query)
        entity = result.scalar_one_or_none()

        if entity is None:
            return False, "记录不存在"

        entity.vue_path = data.vue_path
        entity.tab_page = data.tab_page
        entity.solution_name = data.solution_name
        entity.config_json = data.config_json
        entity.report_length = data.report_length
        entity.report_width = data.report_width
        entity.report_direction = data.report_direction
        entity.last_update_time = int(datetime.now().timestamp())

        await self.db_session.commit()

        return True, "保存成功"

    async def delete(self, id: int) -> Tuple[bool, str]:
        query = select(PrintSolution).where(PrintSolution.id == id)
        result = await self.db_session.execute(query)
        entity = result.scalar_one_or_none()

        if entity is None:
            return False, "记录不存在"

        await self.db_session.delete(entity)
        await self.db_session.commit()

        return True, "删除成功"
