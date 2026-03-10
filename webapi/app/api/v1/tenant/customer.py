from fastapi import APIRouter, Depends, Query
from app.services.customer_service import CustomerService
from app.schemas.customer import CustomerCreate, CustomerUpdate, CustomerViewModel
from app.api.service_dependencies import get_service_dependency
from app.api.responses import success_response, error_response
from app.api.dependencies import get_current_user
from app.core.current_user import CurrentUser

router = APIRouter()


@router.post("/customer/list")
async def search_customer(
    page_index: int = Query(1, ge=1, description='页码'),
    page_size: int = Query(10, ge=1, le=100, description='每页数量'),
    customer_name: str = Query(None, description='客户名称'),
    service: CustomerService = Depends(get_service_dependency(CustomerService)),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    分页查询客户列表
    
    Args:
        page_index: 页码,从1开始
        page_size: 每页数量
        customer_name: 客户名称(模糊查询)
        service: 客户服务
        current_user: 当前用户
        
    Returns:
        客户列表和总数
    """
    data, totals = await service.search(
        page_index=page_index,
        page_size=page_size,
        customer_name=customer_name,
        current_user=current_user
    )
    
    return success_response({
        'rows': data,
        'totals': totals
    })


@router.get("/customer/all")
async def get_all_customers(
    service: CustomerService = Depends(get_service_dependency(CustomerService)),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    获取所有客户列表
    
    Args:
        service: 客户服务
        current_user: 当前用户
        
    Returns:
        客户列表
    """
    data = await service.get_all(current_user)
    
    return success_response(data)


@router.get("/customer")
async def get_customer(
    id: int = Query(..., description='客户ID'),
    current_user: CurrentUser = Depends(get_current_user),
    service: CustomerService = Depends(get_service_dependency(CustomerService))
):
    """
    根据ID获取客户信息
    
    Args:
        id: 客户ID
        current_user: 当前用户
        service: 客户服务
        
    Returns:
        客户信息
    """
    result = await service.get_by_id(id, current_user)
    
    if result is None:
        return error_response("记录不存在")
    
    return success_response(result)


@router.post("/customer")
async def create_customer(
    data: CustomerCreate,
    service: CustomerService = Depends(get_service_dependency(CustomerService)),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    创建客户
    
    Args:
        data: 客户创建数据
        service: 客户服务
        current_user: 当前用户
        
    Returns:
        创建的客户信息
    """
    customer_id, msg = await service.create(data, current_user)
    
    if customer_id == 0:
        return error_response(msg)
    
    result = await service.get_by_id(customer_id)
    return success_response(result)


@router.post("/customer/update")
async def update_customer(
    data: CustomerUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    service: CustomerService = Depends(get_service_dependency(CustomerService))
):
    """
    更新客户信息
    
    Args:
        data: 客户更新数据
        current_user: 当前用户
        service: 客户服务
        
    Returns:
        更新后的客户信息
    """
    flag, msg = await service.update(data, current_user)
    
    if not flag:
        return error_response(msg)
    
    result = await service.get_by_id(data.id, current_user)
    return success_response(result)


@router.post("/customer/delete")
async def delete_customer(
    id: int = Query(..., description='客户ID'),
    current_user: CurrentUser = Depends(get_current_user),
    service: CustomerService = Depends(get_service_dependency(CustomerService))
):
    """
    删除客户
    
    Args:
        id: 客户ID
        current_user: 当前用户
        service: 客户服务
        
    Returns:
        删除结果
    """
    flag, msg = await service.delete(id, current_user)
    
    if not flag:
        return error_response(msg)
    
    return success_response(msg)
