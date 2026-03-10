from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from app.schemas.warehouse import WarehouseViewModel, WarehouseCreateViewModel, WarehouseUpdateViewModel
from app.services.warehouse_service import WarehouseService
from app.api.service_dependencies import get_service_dependency
from app.api.responses import success_response, error_response
from app.api.dependencies import get_current_user
from app.core.current_user import CurrentUser

router = APIRouter()


@router.get("/warehouse", response_model=WarehouseViewModel)
async def get_warehouse(
    id: int = Query(..., description="仓库ID"),
    current_user: CurrentUser = Depends(get_current_user),
    service: WarehouseService = Depends(get_service_dependency(WarehouseService))
):
    """
    根据ID获取仓库信息
    
    Args:
        id: 仓库ID
        current_user: 当前用户
        service: 仓库服务
        
    Returns:
        仓库信息
    """
    result = await service.get_by_id(id, current_user)
    
    if result is None:
        return error_response("仓库不存在")
    
    return success_response(result)


@router.get("/warehouse/list", response_model=List[WarehouseViewModel])
async def get_warehouse_list(
    service: WarehouseService = Depends(get_service_dependency(WarehouseService)),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    获取所有仓库列表
    
    Args:
        service: 仓库服务
        current_user: 当前用户
        
    Returns:
        仓库列表
    """
    result = await service.get_all(current_user)
    
    return success_response(result)


@router.get("/warehouse/page")
async def get_warehouse_page(
    page_index: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    warehouse_name: Optional[str] = Query(None, description="仓库名称"),
    city: Optional[str] = Query(None, description="城市"),
    is_valid: Optional[bool] = Query(None, description="是否有效"),
    service: WarehouseService = Depends(get_service_dependency(WarehouseService)),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    分页查询仓库列表
    
    Args:
        page_index: 页码,从1开始
        page_size: 每页数量
        warehouse_name: 仓库名称(模糊查询)
        city: 城市(模糊查询)
        is_valid: 是否有效
        service: 仓库服务
        current_user: 当前用户
        
    Returns:
        仓库列表和总数
    """
    search_params = {}
    if warehouse_name:
        search_params["warehouse_name"] = warehouse_name
    if city:
        search_params["city"] = city
    if is_valid is not None:
        search_params["is_valid"] = is_valid
    
    data, totals = await service.page_search(page_index, page_size, search_params, current_user)
    
    return success_response({
        "data": data,
        "totals": totals,
        "page_index": page_index,
        "page_size": page_size
    })


@router.get("/warehouse/select-items")
async def get_warehouse_select_items(
    service: WarehouseService = Depends(get_service_dependency(WarehouseService)),
    current_user: CurrentUser = Depends(get_current_user)
):
    result = await service.get_select_items(current_user)
    
    return success_response(result)


@router.post("/warehouse", response_model=WarehouseViewModel)
async def create_warehouse(
    view_model: WarehouseCreateViewModel,
    service: WarehouseService = Depends(get_service_dependency(WarehouseService)),
    current_user: CurrentUser = Depends(get_current_user)
):
    id, msg = await service.add(view_model, current_user)
    
    if id == 0:
        return error_response(msg)
    
    result = await service.get_by_id(id)
    return success_response(result)


@router.post("/warehouse/update", response_model=WarehouseViewModel)
async def update_warehouse(
    view_model: WarehouseUpdateViewModel,
    service: WarehouseService = Depends(get_service_dependency(WarehouseService)),
    current_user: CurrentUser = Depends(get_current_user)
):
    warehouse_id, msg = await service.update(view_model.id, view_model, current_user)
    
    if warehouse_id == 0:
        return error_response(msg)
    
    result = await service.get_by_id(view_model.id)
    return success_response(result)


@router.post("/warehouse/delete")
async def delete_warehouse(
    id: int = Query(..., description="仓库ID"),
    current_user: CurrentUser = Depends(get_current_user),
    service: WarehouseService = Depends(get_service_dependency(WarehouseService))
):
    warehouse_id, msg = await service.delete(id, current_user)
    
    if warehouse_id == 0:
        return error_response(msg)
    
    return success_response({"id": id})
