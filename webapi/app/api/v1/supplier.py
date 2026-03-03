from fastapi import APIRouter, Depends, Query
from app.services.supplier_service import SupplierService
from app.schemas.supplier import SupplierCreate, SupplierUpdate, SupplierViewModel
from app.api.service_dependencies import get_service_dependency
from app.api.responses import success_response, error_response
from app.api.dependencies import get_current_user
from app.core.current_user import CurrentUser

router = APIRouter()


@router.post("/supplier/list")
async def search_supplier(
    page_index: int = Query(1, ge=1, description='页码'),
    page_size: int = Query(10, ge=1, le=100, description='每页数量'),
    supplier_name: str = Query(None, description='供应商名称'),
    is_valid: bool = Query(None, description='是否有效'),
    service: SupplierService = Depends(get_service_dependency(SupplierService)),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    分页查询供应商列表
    
    Args:
        page_index: 页码,从1开始
        page_size: 每页数量
        supplier_name: 供应商名称(模糊查询)
        is_valid: 是否有效
        service: 供应商服务
        current_user: 当前用户
        
    Returns:
        供应商列表和总数
    """
    data, totals = await service.search(
        page_index=page_index,
        page_size=page_size,
        supplier_name=supplier_name,
        is_valid=is_valid,
        current_user=current_user
    )
    
    return success_response({
        'rows': data,
        'totals': totals
    })


@router.get("/supplier/all")
async def get_all_suppliers(
    service: SupplierService = Depends(get_service_dependency(SupplierService)),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    获取所有供应商列表
    
    Args:
        service: 供应商服务
        current_user: 当前用户
        
    Returns:
        供应商列表
    """
    data = await service.get_all(current_user)
    
    return success_response(data)


@router.get("/supplier")
async def get_supplier(
    id: int = Query(..., description='供应商ID'),
    service: SupplierService = Depends(get_service_dependency(SupplierService))
):
    """
    根据ID获取供应商信息
    
    Args:
        id: 供应商ID
        service: 供应商服务
        
    Returns:
        供应商信息
    """
    result = await service.get_by_id(id)
    
    if result is None:
        return error_response("记录不存在")
    
    return success_response(result)


@router.post("/supplier")
async def create_supplier(
    data: SupplierCreate,
    service: SupplierService = Depends(get_service_dependency(SupplierService)),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    创建供应商
    
    Args:
        data: 供应商创建数据
        service: 供应商服务
        current_user: 当前用户
        
    Returns:
        创建的供应商信息
    """
    supplier_id, msg = await service.create(data, current_user)
    
    if supplier_id == 0:
        return error_response(msg)
    
    result = await service.get_by_id(supplier_id)
    return success_response(result)


@router.post("/supplier/update")
async def update_supplier(
    data: SupplierUpdate,
    service: SupplierService = Depends(get_service_dependency(SupplierService))
):
    """
    更新供应商信息
    
    Args:
        data: 供应商更新数据
        service: 供应商服务
        
    Returns:
        更新后的供应商信息
    """
    flag, msg = await service.update(data)
    
    if not flag:
        return error_response(msg)
    
    result = await service.get_by_id(data.id)
    return success_response(result)


@router.post("/supplier/delete")
async def delete_supplier(
    id: int = Query(..., description='供应商ID'),
    service: SupplierService = Depends(get_service_dependency(SupplierService))
):
    """
    删除供应商
    
    Args:
        id: 供应商ID
        service: 供应商服务
        
    Returns:
        删除结果
    """
    flag, msg = await service.delete(id)
    
    if not flag:
        return error_response(msg)
    
    return success_response(msg)
