from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies import get_db_by_tenant, get_current_user
from app.services.inbound_pick_putaway_service import InboundPickPutawayService
from app.schemas.inbound_pick_putaway import (
    InboundPickPutawayCreate,
    InboundPickPutawayUpdate,
    InboundPickPutawayItemUpdate,
    InboundPickPutawayItemSelectLocation,
    InboundPickPutawayViewModel
)
from app.core.response import success_response, error_response
from app.core.current_user import CurrentUser

router = APIRouter()


@router.post("/inbound-pick-putaway/list")
async def search_inbound_pick_putaway(
    page_index: int = Query(1, ge=1, description='页码'),
    page_size: int = Query(10, ge=1, le=100, description='每页数量'),
    pick_putaway_no: str = Query(None, description='拣货上架单号'),
    pick_putaway_status: int = Query(None, description='拣货上架状态'),
    order_no: str = Query(None, description='入库订单号'),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    分页查询入库拣货上架单列表
    
    Args:
        page_index: 页码,从1开始
        page_size: 每页数量
        pick_putaway_no: 拣货上架单号(模糊查询)
        pick_putaway_status: 拣货上架状态
        order_no: 入库订单号(模糊查询)
        current_user: 当前登录用户
        db: 数据库会话
        
    Returns:
        拣货上架单列表和总数
    """
    service = InboundPickPutawayService(db)
    data, totals = await service.search(
        page_index=page_index,
        page_size=page_size,
        pick_putaway_no=pick_putaway_no,
        pick_putaway_status=pick_putaway_status,
        order_no=order_no,
        current_user=current_user
    )
    
    return success_response({
        'rows': data,
        'totals': totals
    })


@router.get("/inbound-pick-putaway")
async def get_inbound_pick_putaway(
    id: int = Query(..., description='拣货上架单ID'),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    根据ID获取拣货上架单信息
    
    Args:
        id: 拣货上架单ID
        current_user: 当前登录用户
        db: 数据库会话
        
    Returns:
        拣货上架单信息
    """
    service = InboundPickPutawayService(db)
    result = await service.get_by_id(id, current_user)
    
    if result is None:
        return error_response("记录不存在")
    
    return success_response(result)


@router.post("/inbound-pick-putaway")
async def create_inbound_pick_putaway(
    data: InboundPickPutawayCreate,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    创建拣货上架单（从入库订单生成）
    
    Args:
        data: 拣货上架单创建数据
        current_user: 当前登录用户
        db: 数据库会话
        
    Returns:
        创建的拣货上架单信息
    """
    service = InboundPickPutawayService(db)
    pick_putaway_id, msg = await service.create(data, current_user)
    
    if pick_putaway_id == 0:
        return error_response(msg)
    
    result = await service.get_by_id(pick_putaway_id, current_user)
    return success_response(result)


@router.post("/inbound-pick-putaway/update")
async def update_inbound_pick_putaway(
    data: InboundPickPutawayUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    更新拣货上架单信息
    
    Args:
        data: 拣货上架单更新数据
        current_user: 当前登录用户
        db: 数据库会话
        
    Returns:
        更新后的拣货上架单信息
    """
    service = InboundPickPutawayService(db)
    flag, msg = await service.update(data, current_user)
    
    if not flag:
        return error_response(msg)
    
    result = await service.get_by_id(data.id, current_user)
    return success_response(result)


@router.post("/inbound-pick-putaway/item/select-location")
async def select_location_for_item(
    data: InboundPickPutawayItemSelectLocation,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    选择库位（强制选择库位）
    
    Args:
        data: 拣货上架单明细选择库位数据
        current_user: 当前登录用户
        db: 数据库会话
        
    Returns:
        操作结果
    """
    service = InboundPickPutawayService(db)
    flag, msg = await service.select_location(data, current_user)
    
    if not flag:
        return error_response(msg)
    
    return success_response(msg)


@router.post("/inbound-pick-putaway/item/update")
async def update_inbound_pick_putaway_item(
    data: InboundPickPutawayItemUpdate,
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    更新拣货上架单明细信息（上架操作）
    
    Args:
        data: 拣货上架单明细更新数据
        db: 数据库会话
        
    Returns:
        更新结果
    """
    service = InboundPickPutawayService(db)
    flag, msg = await service.update_item(data)
    
    if not flag:
        return error_response(msg)
    
    return success_response(msg)


@router.post("/inbound-pick-putaway/start-putaway")
async def start_putaway(
    id: int = Query(..., description='拣货上架单ID'),
    putaway_person_id: int = Query(..., description='上架人ID'),
    putaway_person: str = Query(..., description='上架人'),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    开始上架
    
    Args:
        id: 拣货上架单ID
        putaway_person_id: 上架人ID
        putaway_person: 上架人
        current_user: 当前登录用户
        db: 数据库会话
        
    Returns:
        操作结果
    """
    service = InboundPickPutawayService(db)
    flag, msg = await service.start_putaway(id, putaway_person_id, putaway_person, current_user)
    
    if not flag:
        return error_response(msg)
    
    return success_response(msg)


@router.post("/inbound-pick-putaway/complete-putaway")
async def complete_putaway(
    id: int = Query(..., description='拣货上架单ID'),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    完成上架
    
    Args:
        id: 拣货上架单ID
        current_user: 当前登录用户
        db: 数据库会话
        
    Returns:
        操作结果
    """
    service = InboundPickPutawayService(db)
    flag, msg = await service.complete_putaway(id, current_user)
    
    if not flag:
        return error_response(msg)
    
    return success_response(msg)


@router.post("/inbound-pick-putaway/delete")
async def delete_inbound_pick_putaway(
    id: int = Query(..., description='拣货上架单ID'),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    删除拣货上架单
    
    Args:
        id: 拣货上架单ID
        current_user: 当前登录用户
        db: 数据库会话
        
    Returns:
        删除结果
    """
    service = InboundPickPutawayService(db)
    flag, msg = await service.delete(id, current_user)
    
    if not flag:
        return error_response(msg)
    
    return success_response(msg)
