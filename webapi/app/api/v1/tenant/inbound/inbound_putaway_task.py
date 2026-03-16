from fastapi import APIRouter, Depends, Query
from app.core.user import get_current_user, CurrentUser
from app.services.inbound.inbound_putaway_task_service import InboundPutawayTaskService
from app.schemas.inbound.inbound_putaway_task import InboundPutawayTaskCreate
from app.initializer import g

_tag = "入库管理-上架任务"
router = APIRouter(prefix="/inbound-putaway-task")

@router.post("/create")
async def create_putaway_task(
    data: InboundPutawayTaskCreate,
    current_user: CurrentUser = Depends(get_current_user)
):
    service = InboundPutawayTaskService(g.db_async_session)
    task_id, message = await service.create_task(data, current_user)
    return {"id": task_id, "message": message}

@router.get("/list")
async def get_putaway_tasks(
    pick_putaway_item_id: int = Query(..., description="拣货上架明细ID"),
    current_user: CurrentUser = Depends(get_current_user)
):
    service = InboundPutawayTaskService(g.db_async_session)
    tasks = await service.get_tasks_by_pick_putaway_item_id(pick_putaway_item_id)
    return {"rows": tasks}
