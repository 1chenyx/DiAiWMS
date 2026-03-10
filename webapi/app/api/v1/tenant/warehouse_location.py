from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.schemas.warehouse_location import (
    WarehouseLocationViewModel,
    WarehouseLocationCreateViewModel,
    WarehouseLocationUpdateViewModel,
    WarehouseLocationTreeNode
)
from app.services.warehouse_location_service import WarehouseLocationService
from app.api.dependencies import get_db_by_tenant, get_current_user
from app.api.responses import success_response, error_response
from app.core.current_user import CurrentUser

router = APIRouter()


@router.get("/warehouselocation", response_model=WarehouseLocationViewModel)
async def get_warehouse_location(
    id: int = Query(..., description="仓库位置ID"),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    根据ID获取仓库位置信息
    
    Args:
        id: 仓库位置ID
        current_user: 当前登录用户
        db: 数据库会话
        
    Returns:
        仓库位置信息
    """
    service = WarehouseLocationService(db)
    result = await service.get_by_id(id, current_user)
    
    if result is None:
        return error_response("记录不存在")
    
    return success_response(result)


@router.get("/warehouselocation/tree", response_model=list[WarehouseLocationTreeNode])
async def get_warehouse_location_tree(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    获取完整的仓库位置树形结构
    
    Args:
        current_user: 当前登录用户
        db: 数据库会话
        
    Returns:
        树形结构列表
    """
    service = WarehouseLocationService(db)
    result = await service.get_tree(current_user)
    
    return success_response(result)


@router.get("/warehouselocation/tree-by-warehouse", response_model=WarehouseLocationTreeNode)
async def get_warehouse_location_tree_by_warehouse(
    warehouse_id: int = Query(..., description="仓库ID"),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    根据仓库ID获取该仓库的库区、库位树形结构
    
    Args:
        warehouse_id: 仓库ID
        current_user: 当前登录用户
        db: 数据库会话
        
    Returns:
        树形结构节点
    """
    service = WarehouseLocationService(db)
    result = await service.get_tree_by_warehouse_id(warehouse_id, current_user)
    
    if result is None:
        return error_response("仓库不存在或不是仓库类型")
    
    return success_response(result)


@router.get("/warehouselocation/children", response_model=list[WarehouseLocationViewModel])
async def get_warehouse_location_children(
    parent_id: int = Query(..., description="父节点ID"),
    node_type: Optional[int] = Query(None, description="节点类型: 1-仓库, 2-库区, 3-库位"),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    获取指定父节点的子节点
    
    Args:
        parent_id: 父节点ID
        node_type: 节点类型 (可选)
        current_user: 当前登录用户
        db: 数据库会话
        
    Returns:
        子节点列表
    """
    service = WarehouseLocationService(db)
    result = await service.get_children(parent_id, node_type, current_user)
    
    return success_response(result)


@router.get("/warehouselocation/list", response_model=list[WarehouseLocationViewModel])
async def get_warehouse_location_list(
    node_type: Optional[int] = Query(None, description="节点类型: 1-仓库, 2-库区, 3-库位"),
    parent_id: Optional[int] = Query(None, description="父节点ID"),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    获取仓库位置列表
    
    Args:
        node_type: 节点类型 (可选)
        parent_id: 父节点ID (可选)
        current_user: 当前登录用户
        db: 数据库会话
        
    Returns:
        仓库位置列表
    """
    service = WarehouseLocationService(db)
    result = await service.get_all(node_type, parent_id, current_user)
    
    return success_response(result)


@router.get("/warehouselocation/page")
async def get_warehouse_location_page(
    page_index: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    node_name: Optional[str] = Query(None, description="节点名称"),
    node_type: Optional[int] = Query(None, description="节点类型: 1-仓库, 2-库区, 3-库位"),
    parent_id: Optional[int] = Query(None, description="父节点ID"),
    is_valid: Optional[bool] = Query(None, description="是否有效"),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    分页查询仓库位置列表
    
    Args:
        page_index: 页码,从1开始
        page_size: 每页数量
        node_name: 节点名称(模糊查询)
        node_type: 节点类型
        parent_id: 父节点ID
        is_valid: 是否有效
        current_user: 当前登录用户
        db: 数据库会话
        
    Returns:
        仓库位置列表和总数
    """
    service = WarehouseLocationService(db)
    
    search_params = {}
    if node_name:
        search_params["node_name"] = node_name
    if node_type:
        search_params["node_type"] = node_type
    if parent_id:
        search_params["parent_id"] = parent_id
    if is_valid is not None:
        search_params["is_valid"] = is_valid
    
    data, totals = await service.page_search(page_index, page_size, search_params, current_user)
    
    return success_response({
        "data": data,
        "totals": totals,
        "page_index": page_index,
        "page_size": page_size
    })


@router.get("/warehouselocation/select-items")
async def get_warehouse_location_select_items(
    node_type: int = Query(..., description="节点类型: 1-仓库, 2-库区, 3-库位"),
    parent_id: int = Query(..., description="父节点ID"),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    获取指定类型的有效节点列表，用于下拉选择
    
    Args:
        node_type: 节点类型
        parent_id: 父节点ID
        current_user: 当前登录用户
        db: 数据库会话
        
    Returns:
        节点字典列表
    """
    service = WarehouseLocationService(db)
    result = await service.get_select_items(node_type, parent_id, current_user)
    
    return success_response(result)


@router.post("/warehouselocation", response_model=WarehouseLocationViewModel)
async def create_warehouse_location(
    view_model: WarehouseLocationCreateViewModel,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    创建仓库位置
    
    Args:
        view_model: 仓库位置创建数据
        current_user: 当前登录用户
        db: 数据库会话
        
    Returns:
        创建的仓库位置信息
    """
    service = WarehouseLocationService(db)
    id, msg = await service.add(view_model, current_user)
    
    if id == 0:
        return error_response(msg)
    
    result = await service.get_by_id(id, current_user)
    return success_response(result)


@router.post("/warehouselocation/update", response_model=WarehouseLocationViewModel)
async def update_warehouse_location(
    view_model: WarehouseLocationUpdateViewModel,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    更新仓库位置信息
    
    Args:
        view_model: 仓库位置更新数据
        current_user: 当前登录用户
        db: 数据库会话
        
    Returns:
        更新后的仓库位置信息
    """
    service = WarehouseLocationService(db)
    flag, msg = await service.update(view_model.id, view_model, current_user)
    
    if not flag:
        return error_response(msg)
    
    result = await service.get_by_id(view_model.id, current_user)
    return success_response(result)


@router.post("/warehouselocation/delete")
async def delete_warehouse_location(
    id: int = Query(..., description="仓库位置ID"),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    删除仓库位置
    
    Args:
        id: 仓库位置ID
        db: 数据库会话
        
    Returns:
        删除结果
    """
    service = WarehouseLocationService(db)
    flag, msg = await service.delete(id)
    
    if not flag:
        return error_response(msg)
    
    return success_response({"id": id})
