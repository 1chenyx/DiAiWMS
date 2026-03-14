from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies import get_db_by_tenant, get_current_user
from app.services.outbound.outbound_pick_putaway_service import OutboundPickPutawayService
from app.schemas.outbound.outbound_pick_putaway import (
    OutboundPickPutawayCreate,
    OutboundPickPutawayUpdate,
    OutboundPickPutawayItemUpdate,
    OutboundPickPutawayViewModel
)
from app.core.response import success_response, error_response
from app.core.current_user import CurrentUser

_tag = "出库管理-拣货作业"
router = APIRouter()


@router.post("/outbound-pick-putaway/list")
async def search_outbound_pick_putaway(
    page_index: int = Query(1, ge=1, description='页码'),
    page_size: int = Query(10, ge=1, le=100, description='每页数量'),
    pick_putaway_no: str = Query(None, description='拣货上架单号'),
    pick_putaway_status: int = Query(None, description='拣货上架状态'),
    order_no: str = Query(None, description='出库订单号'),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    分页查询出库拣货上架单列表
    
    Args:
        page_index: 页码,从1开始
        page_size: 每页数量
        pick_putaway_no: 拣货上架单号(模糊查询)
        pick_putaway_status: 拣货上架状态
        order_no: 出库订单号(模糊查询)
        current_user: 当前登录用户
        db: 数据库会话
        
    Returns:
        拣货上架单列表和总数
    """
    service = OutboundPickPutawayService(db)
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


@router.get("/outbound-pick-putaway")
async def get_outbound_pick_putaway(
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
    service = OutboundPickPutawayService(db)
    result = await service.get_by_id(id, current_user)
    
    if result is None:
        return error_response("记录不存在")
    
    return success_response(result)


@router.post("/outbound-pick-putaway")
async def create_outbound_pick_putaway(
    data: OutboundPickPutawayCreate,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    创建拣货上架单（从出库订单生成）
    
    Args:
        data: 拣货上架单创建数据
        current_user: 当前登录用户
        db: 数据库会话
        
    Returns:
        创建的拣货上架单信息
    """
    service = OutboundPickPutawayService(db)
    pick_putaway_id, msg = await service.create(data, current_user)
    
    if pick_putaway_id == 0:
        return error_response(msg)
    
    result = await service.get_by_id(pick_putaway_id, current_user)
    return success_response(result)


@router.post("/outbound-pick-putaway/update")
async def update_outbound_pick_putaway(
    data: OutboundPickPutawayUpdate,
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
    service = OutboundPickPutawayService(db)
    flag, msg = await service.update(data, current_user)
    
    if not flag:
        return error_response(msg)
    
    result = await service.get_by_id(data.id, current_user)
    return success_response(result)


@router.post("/outbound-pick-putaway/item/update")
async def update_outbound_pick_putaway_item(
    data: OutboundPickPutawayItemUpdate,
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    更新拣货上架单明细信息（拣货操作）
    
    Args:
        data: 拣货上架单明细更新数据
        db: 数据库会话
        
    Returns:
        更新结果
    """
    service = OutboundPickPutawayService(db)
    flag, msg = await service.update_item(data)
    
    if not flag:
        return error_response(msg)
    
    return success_response(msg)


@router.post("/outbound-pick-putaway/start-pick")
async def start_pick(
    id: int = Query(..., description='拣货上架单ID'),
    picker_id: int = Query(..., description='拣货人ID'),
    picker: str = Query(..., description='拣货人'),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    开始拣货
    
    Args:
        id: 拣货上架单ID
        picker_id: 拣货人ID
        picker: 拣货人
        current_user: 当前登录用户
        db: 数据库会话
        
    Returns:
        操作结果
    """
    service = OutboundPickPutawayService(db)
    flag, msg = await service.start_pick(id, picker_id, picker, current_user)
    
    if not flag:
        return error_response(msg)
    
    return success_response(msg)


@router.post("/outbound-pick-putaway/complete-pick")
async def complete_pick(
    id: int = Query(..., description='拣货上架单ID'),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    完成拣货
    
    Args:
        id: 拣货上架单ID
        current_user: 当前登录用户
        db: 数据库会话
        
    Returns:
        操作结果
    """
    service = OutboundPickPutawayService(db)
    flag, msg = await service.complete_pick(id, current_user)
    
    if not flag:
        return error_response(msg)
    
    return success_response(msg)


@router.post("/outbound-pick-putaway/delete")
async def delete_outbound_pick_putaway(
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
    service = OutboundPickPutawayService(db)
    flag, msg = await service.delete(id, current_user)
    
    if not flag:
        return error_response(msg)
    
    return success_response(msg)
