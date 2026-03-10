from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies import get_db_by_tenant, get_current_user
from app.services.outbound_receipt_service import OutboundReceiptService
from app.schemas.outbound_receipt import (
    OutboundReceiptCreate,
    OutboundReceiptUpdate,
    OutboundReceiptViewModel
)
from app.core.response import success_response, error_response
from app.core.current_user import CurrentUser

router = APIRouter()


@router.post("/outbound-receipt/list")
async def search_outbound_receipt(
    page_index: int = Query(1, ge=1, description='页码'),
    page_size: int = Query(10, ge=1, le=100, description='每页数量'),
    receipt_no: str = Query(None, description='出库单号'),
    receipt_status: int = Query(None, description='出库单状态'),
    order_no: str = Query(None, description='出库订单号'),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    分页查询出库单列表
    
    Args:
        page_index: 页码,从1开始
        page_size: 每页数量
        receipt_no: 出库单号(模糊查询)
        receipt_status: 出库单状态
        order_no: 出库订单号(模糊查询)
        current_user: 当前登录用户
        db: 数据库会话
        
    Returns:
        出库单列表和总数
    """
    service = OutboundReceiptService(db)
    data, totals = await service.search(
        page_index=page_index,
        page_size=page_size,
        receipt_no=receipt_no,
        receipt_status=receipt_status,
        order_no=order_no,
        current_user=current_user
    )
    
    return success_response({
        'rows': data,
        'totals': totals
    })


@router.get("/outbound-receipt")
async def get_outbound_receipt(
    id: int = Query(..., description='出库单ID'),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    根据ID获取出库单信息
    
    Args:
        id: 出库单ID
        current_user: 当前登录用户
        db: 数据库会话
        
    Returns:
        出库单信息
    """
    service = OutboundReceiptService(db)
    result = await service.get_by_id(id, current_user)
    
    if result is None:
        return error_response("记录不存在")
    
    return success_response(result)


@router.post("/outbound-receipt")
async def create_outbound_receipt(
    data: OutboundReceiptCreate,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    创建出库单（从拣货上架单生成）
    
    Args:
        data: 出库单创建数据
        current_user: 当前登录用户
        db: 数据库会话
        
    Returns:
        创建的出库单信息
    """
    service = OutboundReceiptService(db)
    receipt_id, msg = await service.create(data, current_user)
    
    if receipt_id == 0:
        return error_response(msg)
    
    result = await service.get_by_id(receipt_id, current_user)
    return success_response(result)


@router.post("/outbound-receipt/update")
async def update_outbound_receipt(
    data: OutboundReceiptUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    更新出库单信息
    
    Args:
        data: 出库单更新数据
        current_user: 当前登录用户
        db: 数据库会话
        
    Returns:
        更新后的出库单信息
    """
    service = OutboundReceiptService(db)
    flag, msg = await service.update(data, current_user)
    
    if not flag:
        return error_response(msg)
    
    result = await service.get_by_id(data.id, current_user)
    return success_response(result)


@router.post("/outbound-receipt/complete-outbound")
async def complete_outbound(
    id: int = Query(..., description='出库单ID'),
    outbound_person: str = Query(..., description='出库人'),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    完成出库（扣减库存）
    
    Args:
        id: 出库单ID
        outbound_person: 出库人
        current_user: 当前登录用户
        db: 数据库会话
        
    Returns:
        操作结果
    """
    service = OutboundReceiptService(db)
    flag, msg = await service.complete_outbound(id, outbound_person, current_user)
    
    if not flag:
        return error_response(msg)
    
    return success_response(msg)


@router.post("/outbound-receipt/delete")
async def delete_outbound_receipt(
    id: int = Query(..., description='出库单ID'),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    删除出库单
    
    Args:
        id: 出库单ID
        current_user: 当前登录用户
        db: 数据库会话
        
    Returns:
        删除结果
    """
    service = OutboundReceiptService(db)
    flag, msg = await service.delete(id, current_user)
    
    if not flag:
        return error_response(msg)
    
    return success_response(msg)
