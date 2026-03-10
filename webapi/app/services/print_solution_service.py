from datetime import datetime
from typing import List, Tuple, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.entities.print_solution import PrintSolution
from app.schemas.print_solution import PrintSolutionCreate, PrintSolutionUpdate, PrintSolutionViewModel
from app.core.current_user import CurrentUser
from app.repositories.print_solution_repository import PrintSolutionRepository
from app.services.base_service import TenantAwareService


class PrintSolutionService(TenantAwareService[PrintSolutionRepository, PrintSolution]):
    def __init__(self, db_session: AsyncSession):
        repository = PrintSolutionRepository(db_session)
        super().__init__(repository)
        self._db_session = db_session

    async def search(
        self,
        page_index: int = 1,
        page_size: int = 10,
        vue_path: Optional[str] = None,
        solution_name: Optional[str] = None,
        current_user: Optional[CurrentUser] = None
    ) -> Tuple[List[PrintSolutionViewModel], int]:
        filters = {}
        if vue_path:
            filters["vue_path"] = f"%{vue_path}%"
        if solution_name:
            filters["solution_name"] = f"%{solution_name}%"
        
        entities, totals = await self.page_query_by_tenant(
            page_index=page_index,
            page_size=page_size,
            tenant_id=current_user.tenant_id if current_user else "",
            filters=filters
        )

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

        result = await self._db_session.execute(query)
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
        entity = await self.create_with_tenant(
            current_user.tenant_id if current_user else "",
            vue_path=data.vue_path,
            tab_page=data.tab_page,
            solution_name=data.solution_name,
            config_json=data.config_json,
            report_length=data.report_length,
            report_width=data.report_width,
            report_direction=data.report_direction,
            last_update_time=int(datetime.now().timestamp())
        )

        if entity.id > 0:
            return entity.id, "保存成功"
        else:
            return 0, "保存失败"

    async def update(self, data: PrintSolutionUpdate, current_user: CurrentUser) -> Tuple[bool, str]:
        entity = await self.get_by_id(data.id)

        if entity is None:
            return False, "记录不存在"

        await self.update_with_tenant(
            data.id,
            entity.tenant_id,
            vue_path=data.vue_path,
            tab_page=data.tab_page,
            solution_name=data.solution_name,
            config_json=data.config_json,
            report_length=data.report_length,
            report_width=data.report_width,
            report_direction=data.report_direction,
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
