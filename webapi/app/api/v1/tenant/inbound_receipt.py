from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies import get_db_by_tenant, get_current_user
from app.services.inbound_receipt_service import InboundReceiptService
from app.schemas.inbound_receipt import (
    InboundReceiptCreate,
    InboundReceiptUpdate,
    InboundReceiptViewModel
)
from app.core.response import success_response, error_response
from app.core.current_user import CurrentUser

router = APIRouter()


@router.post("/inbound-receipt/list")
async def search_inbound_receipt(
    page_index: int = Query(1, ge=1, description='页码'),
    page_size: int = Query(10, ge=1, le=100, description='每页数量'),
    receipt_no: str = Query(None, description='入库单号'),
    receipt_status: int = Query(None, description='入库单状态'),
    order_no: str = Query(None, description='入库订单号'),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    分页查询入库单列表
    
    Args:
        page_index: 页码,从1开始
        page_size: 每页数量
        receipt_no: 入库单号(模糊查询)
        receipt_status: 入库单状态
        order_no: 入库订单号(模糊查询)
        current_user: 当前登录用户
        db: 数据库会话
        
    Returns:
        入库单列表和总数
    """
    service = InboundReceiptService(db)
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


@router.get("/inbound-receipt")
async def get_inbound_receipt(
    id: int = Query(..., description='入库单ID'),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    根据ID获取入库单信息
    
    Args:
        id: 入库单ID
        current_user: 当前登录用户
        db: 数据库会话
        
    Returns:
        入库单信息
    """
    service = InboundReceiptService(db)
    result = await service.get_by_id(id, current_user)
    
    if result is None:
        return error_response("记录不存在")
    
    return success_response(result)


@router.post("/inbound-receipt")
async def create_inbound_receipt(
    data: InboundReceiptCreate,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    创建入库单（从拣货上架单生成）
    
    Args:
        data: 入库单创建数据
        current_user: 当前登录用户
        db: 数据库会话
        
    Returns:
        创建的入库单信息
    """
    service = InboundReceiptService(db)
    receipt_id, msg = await service.create(data, current_user)
    
    if receipt_id == 0:
        return error_response(msg)
    
    result = await service.get_by_id(receipt_id, current_user)
    return success_response(result)


@router.post("/inbound-receipt/update")
async def update_inbound_receipt(
    data: InboundReceiptUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    更新入库单信息
    
    Args:
        data: 入库单更新数据
        current_user: 当前登录用户
        db: 数据库会话
        
    Returns:
        更新后的入库单信息
    """
    service = InboundReceiptService(db)
    flag, msg = await service.update(data, current_user)
    
    if not flag:
        return error_response(msg)
    
    result = await service.get_by_id(data.id, current_user)
    return success_response(result)


@router.post("/inbound-receipt/complete-inbound")
async def complete_inbound(
    id: int = Query(..., description='入库单ID'),
    inbound_person: str = Query(..., description='入库人'),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    完成入库（增加库存）
    
    Args:
        id: 入库单ID
        inbound_person: 入库人
        current_user: 当前登录用户
        db: 数据库会话
        
    Returns:
        操作结果
    """
    service = InboundReceiptService(db)
    flag, msg = await service.complete_inbound(id, inbound_person, current_user)
    
    if not flag:
        return error_response(msg)
    
    return success_response(msg)


@router.post("/inbound-receipt/delete")
async def delete_inbound_receipt(
    id: int = Query(..., description='入库单ID'),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    删除入库单
    
    Args:
        id: 入库单ID
        current_user: 当前登录用户
        db: 数据库会话
        
    Returns:
        删除结果
    """
    service = InboundReceiptService(db)
    flag, msg = await service.delete(id, current_user)
    
    if not flag:
        return error_response(msg)
    
    return success_response(msg)
