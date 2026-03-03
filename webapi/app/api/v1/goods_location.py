from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.schemas.goods_location import GoodsLocationViewModel, GoodsLocationCreateViewModel, GoodsLocationUpdateViewModel
from app.services.goods_location_service import GoodsLocationService
from app.core.database import get_db
from app.api.dependencies import get_db_by_tenant
from app.api.responses import success_response, error_response

_active = False
router = APIRouter()


@router.get("/goodslocation", response_model=GoodsLocationViewModel)
async def get_goods_location(
    id: int = Query(..., description="货位ID"),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    根据ID获取货位信息
    
    Args:
        id: 货位ID
        db: 数据库会话
        
    Returns:
        货位信息
    """
    service = GoodsLocationService(db)
    result = await service.get_by_id(id)
    
    if result is None:
        return error_response("货位不存在")
    
    return success_response(result)


@router.get("/goodslocation/list")
async def get_goods_location_list(
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    获取货位列表
    
    Args:
        db: 数据库会话
        
    Returns:
        货位列表
    """
    from app.core.current_user import CurrentUser
    
    current_user = CurrentUser()
    service = GoodsLocationService(db)
    result = await service.get_all(current_user)
    
    return success_response(result)


@router.get("/goodslocation/page")
async def get_goods_location_page(
    page_index: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    location_name: Optional[str] = Query(None, description="货位名称"),
    warehouse_id: Optional[int] = Query(None, description="仓库ID"),
    warehouse_area_id: Optional[int] = Query(None, description="库区ID"),
    is_valid: Optional[bool] = Query(None, description="是否有效"),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    分页查询货位列表
    
    Args:
        page_index: 页码,从1开始
        page_size: 每页数量
        location_name: 货位名称(模糊查询)
        warehouse_id: 仓库ID
        warehouse_area_id: 库区ID
        is_valid: 是否有效
        db: 数据库会话
        
    Returns:
        货位列表和总数
    """
    from app.core.current_user import CurrentUser
    
    current_user = CurrentUser()
    service = GoodsLocationService(db)
    
    search_params = {}
    if location_name:
        search_params["location_name"] = location_name
    if warehouse_id:
        search_params["warehouse_id"] = warehouse_id
    if warehouse_area_id:
        search_params["warehouse_area_id"] = warehouse_area_id
    if is_valid is not None:
        search_params["is_valid"] = is_valid
    
    data, totals = await service.page_search(page_index, page_size, search_params, current_user)
    
    return success_response({
        "data": data,
        "totals": totals,
        "page_index": page_index,
        "page_size": page_size
    })


@router.get("/goodslocation/by-warehousearea")
async def get_goodslocation_by_warehouse_area_id(
    warehouse_area_id: int = Query(..., description="库区ID"),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    from app.core.current_user import CurrentUser
    
    current_user = CurrentUser()
    service = GoodsLocationService(db)
    result = await service.get_goodslocation_by_warehouse_area_id(warehouse_area_id, current_user)
    
    return success_response(result)


@router.post("/goodslocation", response_model=GoodsLocationViewModel)
async def create_goods_location(
    view_model: GoodsLocationCreateViewModel,
    db: AsyncSession = Depends(get_db_by_tenant)
):
    from app.core.current_user import CurrentUser
    
    current_user = CurrentUser()
    service = GoodsLocationService(db)
    id, msg = await service.add(view_model, current_user)
    
    if id == 0:
        return error_response(msg)
    
    result = await service.get_by_id(id)
    return success_response(result)


@router.post("/goodslocation/update", response_model=GoodsLocationViewModel)
async def update_goods_location(
    view_model: GoodsLocationUpdateViewModel,
    db: AsyncSession = Depends(get_db_by_tenant)
):
    from app.core.current_user import CurrentUser
    
    current_user = CurrentUser()
    service = GoodsLocationService(db)
    flag, msg = await service.update(view_model.id, view_model, current_user)
    
    if not flag:
        return error_response(msg)
    
    result = await service.get_by_id(view_model.id)
    return success_response(result)


@router.post("/goodslocation/delete")
async def delete_goods_location(
    id: int = Query(..., description="货位ID"),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    service = GoodsLocationService(db)
    flag, msg = await service.delete(id)
    
    if not flag:
        return error_response(msg)
    
    return success_response({"id": id})
