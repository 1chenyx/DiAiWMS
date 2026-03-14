from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.schemas.inventory.stock import StockViewModel, StockCreateViewModel, StockUpdateViewModel
from app.services.inventory.stock_service import StockService
from app.core.database import get_db
from app.api.dependencies import get_db_by_tenant, get_current_user
from app.api.responses import success_response, error_response
from app.core.current_user import CurrentUser

_tag = "库存管理-库存查询"
router = APIRouter()


@router.get("/stock", response_model=StockViewModel)
async def get_stock(
    id: int = Query(..., description="库存ID"),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    根据ID获取库存信息
    
    Args:
        id: 库存ID
        current_user: 当前登录用户
        db: 数据库会话
        
    Returns:
        库存信息
    """
    service = StockService(db)
    result = await service.get_by_id(id, current_user)
    
    if result is None:
        return error_response("库存不存在")
    
    return success_response(result)


@router.get("/stock/list")
async def get_stock_list(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    获取所有库存列表
    
    Args:
        current_user: 当前登录用户
        db: 数据库会话
        
    Returns:
        库存列表
    """
    service = StockService(db)
    result = await service.get_all(current_user)
    
    return success_response(result)


@router.get("/stock/page")
async def get_stock_page(
    page_index: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    sku_id: Optional[int] = Query(None, description="SKU ID"),
    goods_location_id: Optional[int] = Query(None, description="货位ID"),
    is_freeze: Optional[bool] = Query(None, description="是否冻结"),
    goods_owner_id: Optional[int] = Query(None, description="货主ID"),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    分页查询库存列表
    
    Args:
        page_index: 页码,从1开始
        page_size: 每页数量
        sku_id: SKU ID
        goods_location_id: 货位ID
        is_freeze: 是否冻结
        goods_owner_id: 货主ID
        current_user: 当前登录用户
        db: 数据库会话
        
    Returns:
        库存列表和总数
    """
    service = StockService(db)
    
    search_params = {}
    if sku_id:
        search_params["sku_id"] = sku_id
    if goods_location_id:
        search_params["goods_location_id"] = goods_location_id
    if is_freeze is not None:
        search_params["is_freeze"] = is_freeze
    if goods_owner_id:
        search_params["goods_owner_id"] = goods_owner_id
    
    data, totals = await service.page_search(page_index, page_size, search_params, current_user)
    
    return success_response({
        "data": data,
        "totals": totals,
        "page_index": page_index,
        "page_size": page_size
    })


@router.post("/stock", response_model=StockViewModel)
async def create_stock(
    view_model: StockCreateViewModel,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    service = StockService(db)
    id, msg = await service.add(view_model, current_user)
    
    if id == 0:
        return error_response(msg)
    
    result = await service.get_by_id(id, current_user)
    return success_response(result)


@router.post("/stock/update", response_model=StockViewModel)
async def update_stock(
    view_model: StockUpdateViewModel,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    service = StockService(db)
    flag, msg = await service.update(view_model.id, view_model, current_user)
    
    if not flag:
        return error_response(msg)
    
    result = await service.get_by_id(view_model.id, current_user)
    return success_response(result)


@router.post("/stock/delete")
async def delete_stock(
    id: int = Query(..., description="库存ID"),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    service = StockService(db)
    flag, msg = await service.delete(id)
    
    if not flag:
        return error_response(msg)
    
    return success_response({"id": id})


@router.post("/stock/{id}/update-qty")
async def update_stock_qty(
    id: int,
    qty_change: int = Query(..., description="数量变化（正数增加，负数减少）"),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    service = StockService(db)
    flag, msg = await service.update_qty(id, qty_change)
    
    if not flag:
        return error_response(msg)
    
    result = await service.get_by_id(id)
    return success_response(result)
