from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.schemas.base.warehouse_area import WarehouseAreaViewModel, WarehouseAreaCreateViewModel, WarehouseAreaUpdateViewModel
from app.services.base.warehouse_area_service import WarehouseAreaService
from app.core.database import get_db
from app.api.dependencies import get_db_by_tenant, get_current_user
from app.api.responses import success_response, error_response
from app.core.current_user import CurrentUser

_tag = "基础数据-库区管理"
router = APIRouter()


@router.get("/warehousearea", response_model=WarehouseAreaViewModel)
async def get_warehouse_area(
    id: int = Query(..., description="库区ID"),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    根据ID获取库区信息
    
    Args:
        id: 库区ID
        current_user: 当前登录用户
        db: 数据库会话
        
    Returns:
        库区信息
    """
    service = WarehouseAreaService(db)
    result = await service.get_by_id(id, current_user)
    
    if result is None:
        return error_response("库区不存在")
    
    return success_response(result)


@router.get("/warehousearea/list")
async def get_warehouse_area_list(
    warehouse_id: int = Query(0, description="仓库ID"),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    获取库区列表
    
    Args:
        warehouse_id: 仓库ID
        current_user: 当前登录用户
        db: 数据库会话
        
    Returns:
        库区列表
    """
    service = WarehouseAreaService(db)
    result = await service.get_all(warehouse_id, current_user)
    
    return success_response(result)


@router.get("/warehousearea/page")
async def get_warehouse_area_page(
    page_index: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    area_name: Optional[str] = Query(None, description="区域名称"),
    warehouse_id: Optional[int] = Query(None, description="仓库ID"),
    is_valid: Optional[bool] = Query(None, description="是否有效"),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    分页查询库区列表
    
    Args:
        page_index: 页码,从1开始
        page_size: 每页数量
        area_name: 区域名称(模糊查询)
        warehouse_id: 仓库ID
        is_valid: 是否有效
        current_user: 当前登录用户
        db: 数据库会话
        
    Returns:
        库区列表和总数
    """
    service = WarehouseAreaService(db)
    
    search_params = {}
    if area_name:
        search_params["area_name"] = area_name
    if warehouse_id:
        search_params["warehouse_id"] = warehouse_id
    if is_valid is not None:
        search_params["is_valid"] = is_valid
    
    data, totals = await service.page_search(page_index, page_size, search_params, current_user)
    
    return success_response({
        "data": data,
        "totals": totals,
        "page_index": page_index,
        "page_size": page_size
    })


@router.get("/warehousearea/by-warehouse")
async def get_warehousearea_by_warehouse_id(
    warehouse_id: int = Query(..., description="仓库ID"),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    根据仓库ID获取库区列表
    
    Args:
        warehouse_id: 仓库ID
        current_user: 当前登录用户
        db: 数据库会话
        
    Returns:
        库区列表
    """
    service = WarehouseAreaService(db)
    result = await service.get_warehousearea_by_warehouse_id(warehouse_id, current_user)
    
    return success_response(result)


@router.post("/warehousearea", response_model=WarehouseAreaViewModel)
async def create_warehouse_area(
    view_model: WarehouseAreaCreateViewModel,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    创建库区
    
    Args:
        view_model: 库区创建数据
        current_user: 当前登录用户
        db: 数据库会话
        
    Returns:
        创建的库区信息
    """
    service = WarehouseAreaService(db)
    id, msg = await service.add(view_model, current_user)
    
    if id == 0:
        return error_response(msg)
    
    result = await service.get_by_id(id, current_user)
    return success_response(result)


@router.post("/warehousearea/update", response_model=WarehouseAreaViewModel)
async def update_warehouse_area(
    view_model: WarehouseAreaUpdateViewModel,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    更新库区信息
    
    Args:
        view_model: 库区更新数据
        current_user: 当前登录用户
        db: 数据库会话
        
    Returns:
        更新后的库区信息
    """
    service = WarehouseAreaService(db)
    flag, msg = await service.update(view_model.id, view_model, current_user)
    
    if not flag:
        return error_response(msg)
    
    result = await service.get_by_id(view_model.id, current_user)
    return success_response(result)


@router.post("/warehousearea/delete")
async def delete_warehouse_area(
    id: int = Query(..., description="库区ID"),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    删除库区
    
    Args:
        id: 库区ID
        current_user: 当前登录用户
        db: 数据库会话
        
    Returns:
        删除结果
    """
    service = WarehouseAreaService(db)
    flag, msg = await service.delete(id, current_user)
    
    if not flag:
        return error_response(msg)
    
    return success_response({"id": id})
