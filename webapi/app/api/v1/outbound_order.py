from fastapi import APIRouter, Depends, Query
from app.services.outbound_order_service import OutboundOrderService
from app.schemas.outbound_order import (
    OutboundOrderCreate,
    OutboundOrderUpdate,
    OutboundOrderViewModel,
    OutboundOrderPageParams
)
from app.api.service_dependencies import get_service_dependency
from app.api.responses import success_response, error_response
from app.api.dependencies import get_current_user
from app.core.current_user import CurrentUser

router = APIRouter()


@router.post("/outbound-order/list")
async def search_outbound_order(
    page_index: int = Query(1, ge=1, description='页码'),
    page_size: int = Query(10, ge=1, le=100, description='每页数量'),
    order_no: str = Query(None, description='出库订单号'),
    order_status: int = Query(None, description='订单状态'),
    customer_id: int = Query(None, description='客户ID'),
    service: OutboundOrderService = Depends(get_service_dependency(OutboundOrderService)),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    分页查询出库订单列表
    
    Args:
        page_index: 页码,从1开始
        page_size: 每页数量
        order_no: 出库订单号(模糊查询)
        order_status: 订单状态
        customer_id: 客户ID
        service: 出库订单服务
        current_user: 当前用户
        
    Returns:
        出库订单列表和总数
    """
    data, totals = await service.search(
        page_index=page_index,
        page_size=page_size,
        order_no=order_no,
        order_status=order_status,
        customer_id=customer_id,
        current_user=current_user
    )
    
    return success_response({
        'rows': data,
        'totals': totals
    })


@router.get("/outbound-order")
async def get_outbound_order(
    id: int = Query(..., description='出库订单ID'),
    service: OutboundOrderService = Depends(get_service_dependency(OutboundOrderService))
):
    """
    根据ID获取出库订单信息
    
    Args:
        id: 出库订单ID
        service: 出库订单服务
        
    Returns:
        出库订单信息
    """
    result = await service.get_by_id(id)
    
    if result is None:
        return error_response("记录不存在")
    
    return success_response(result)


@router.post("/outbound-order")
async def create_outbound_order(
    data: OutboundOrderCreate,
    service: OutboundOrderService = Depends(get_service_dependency(OutboundOrderService)),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    创建出库订单
    
    Args:
        data: 出库订单创建数据
        service: 出库订单服务
        current_user: 当前用户
        
    Returns:
        创建的出库订单信息
    """
    order_id, msg = await service.create(data, current_user)
    
    if order_id == 0:
        return error_response(msg)
    
    result = await service.get_by_id(order_id)
    return success_response(result)


@router.post("/outbound-order/update")
async def update_outbound_order(
    data: OutboundOrderUpdate,
    service: OutboundOrderService = Depends(get_service_dependency(OutboundOrderService))
):
    """
    更新出库订单信息
    
    Args:
        data: 出库订单更新数据
        service: 出库订单服务
        
    Returns:
        更新后的出库订单信息
    """
    flag, msg = await service.update(data)
    
    if not flag:
        return error_response(msg)
    
    result = await service.get_by_id(data.id)
    return success_response(result)


@router.post("/outbound-order/delete")
async def delete_outbound_order(
    id: int = Query(..., description='出库订单ID'),
    service: OutboundOrderService = Depends(get_service_dependency(OutboundOrderService))
):
    """
    删除出库订单
    
    Args:
        id: 出库订单ID
        service: 出库订单服务
        
    Returns:
        删除结果
    """
    flag, msg = await service.delete(id)
    
    if not flag:
        return error_response(msg)
    
    return success_response(msg)
