from fastapi import APIRouter, Depends, Query
from app.services.inbound.inbound_order_service import InboundOrderService
from app.schemas.inbound.inbound_order import (
    InboundOrderCreate,
    InboundOrderUpdate,
    InboundOrderViewModel
)
from app.api.service_dependencies import get_service_dependency
from app.api.responses import success_response, error_response
from app.api.dependencies import get_current_user
from app.core.current_user import CurrentUser

_tag = "入库管理-入库订单"
router = APIRouter()


@router.post("/inbound-order/list")
async def search_inbound_order(
    page_index: int = Query(1, ge=1, description='页码'),
    page_size: int = Query(10, ge=1, le=100, description='每页数量'),
    order_no: str = Query(None, description='入库订单号'),
    order_status: int = Query(None, description='订单状态'),
    supplier_id: int = Query(None, description='供应商ID'),
    service: InboundOrderService = Depends(get_service_dependency(InboundOrderService)),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    分页查询入库订单列表
    
    Args:
        page_index: 页码,从1开始
        page_size: 每页数量
        order_no: 入库订单号(模糊查询)
        order_status: 订单状态
        supplier_id: 供应商ID
        service: 入库订单服务
        current_user: 当前用户
        
    Returns:
        入库订单列表和总数
    """
    data, totals = await service.search(
        page_index=page_index,
        page_size=page_size,
        order_no=order_no,
        order_status=order_status,
        supplier_id=supplier_id,
        current_user=current_user
    )
    
    return success_response({
        'rows': data,
        'totals': totals
    })


@router.get("/inbound-order")
async def get_inbound_order(
    id: int = Query(..., description='入库订单ID'),
    service: InboundOrderService = Depends(get_service_dependency(InboundOrderService))
):
    """
    根据ID获取入库订单信息
    
    Args:
        id: 入库订单ID
        service: 入库订单服务
        
    Returns:
        入库订单信息
    """
    result = await service.get_by_id(id)
    
    if result is None:
        return error_response("记录不存在")
    
    return success_response(result)


@router.post("/inbound-order")
async def create_inbound_order(
    data: InboundOrderCreate,
    service: InboundOrderService = Depends(get_service_dependency(InboundOrderService)),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    创建入库订单
    
    Args:
        data: 入库订单创建数据
        service: 入库订单服务
        current_user: 当前用户
        
    Returns:
        创建的入库订单信息
    """
    order_id, msg = await service.create(data, current_user)
    
    if order_id == 0:
        return error_response(msg)
    
    result = await service.get_by_id(order_id)
    return success_response(result)


@router.post("/inbound-order/update")
async def update_inbound_order(
    data: InboundOrderUpdate,
    service: InboundOrderService = Depends(get_service_dependency(InboundOrderService))
):
    """
    更新入库订单信息
    
    Args:
        data: 入库订单更新数据
        service: 入库订单服务
        
    Returns:
        更新后的入库订单信息
    """
    flag, msg = await service.update(data)
    
    if not flag:
        return error_response(msg)
    
    result = await service.get_by_id(data.id)
    return success_response(result)


@router.post("/inbound-order/delete")
async def delete_inbound_order(
    id: int = Query(..., description='入库订单ID'),
    service: InboundOrderService = Depends(get_service_dependency(InboundOrderService))
):
    """
    删除入库订单
    
    Args:
        id: 入库订单ID
        service: 入库订单服务
        
    Returns:
        删除结果
    """
    flag, msg = await service.delete(id)
    
    if not flag:
        return error_response(msg)
    
    return success_response(msg)
