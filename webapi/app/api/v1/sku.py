from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.schemas.sku import SkuViewModel, SkuCreateViewModel, SkuUpdateViewModel
from app.services.sku_service import SkuService
from app.core.database import get_db
from app.api.dependencies import get_db_by_tenant
from app.api.responses import success_response, error_response

router = APIRouter()


@router.get("/sku", response_model=SkuViewModel)
async def get_sku(
    id: int = Query(..., description="SKU ID"),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    根据ID获取SKU信息
    
    Args:
        id: SKU ID
        db: 数据库会话
        
    Returns:
        SKU信息
    """
    service = SkuService(db)
    result = await service.get_by_id(id)
    
    if result is None:
        return error_response("SKU不存在")
    
    return success_response(result)


@router.get("/sku/list")
async def get_sku_list(
    spu_id: int = Query(0, description="SPU ID"),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    获取SKU列表
    
    Args:
        spu_id: SPU ID
        db: 数据库会话
        
    Returns:
        SKU列表
    """
    service = SkuService(db)
    result = await service.get_all(spu_id)
    
    return success_response(result)


@router.get("/sku/page")
async def get_sku_page(
    page_index: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    sku_code: Optional[str] = Query(None, description="SKU编码"),
    sku_name: Optional[str] = Query(None, description="SKU名称"),
    spu_id: Optional[int] = Query(None, description="SPU ID"),
    bar_code: Optional[str] = Query(None, description="条码"),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    分页查询SKU列表
    
    Args:
        page_index: 页码,从1开始
        page_size: 每页数量
        sku_code: SKU编码(模糊查询)
        sku_name: SKU名称(模糊查询)
        spu_id: SPU ID
        bar_code: 条码(模糊查询)
        db: 数据库会话
        
    Returns:
        SKU列表和总数
    """
    service = SkuService(db)
    
    search_params = {}
    if sku_code:
        search_params["sku_code"] = sku_code
    if sku_name:
        search_params["sku_name"] = sku_name
    if spu_id:
        search_params["spu_id"] = spu_id
    if bar_code:
        search_params["bar_code"] = bar_code
    
    data, totals = await service.page_search(page_index, page_size, search_params)
    
    return success_response({
        "data": data,
        "totals": totals,
        "page_index": page_index,
        "page_size": page_size
    })


@router.post("/sku", response_model=SkuViewModel)
async def create_sku(
    view_model: SkuCreateViewModel,
    db: AsyncSession = Depends(get_db_by_tenant)
):
    service = SkuService(db)
    id, msg = await service.add(view_model)
    
    if id == 0:
        return error_response(msg)
    
    result = await service.get_by_id(id)
    return success_response(result)


@router.post("/sku/update", response_model=SkuViewModel)
async def update_sku(
    view_model: SkuUpdateViewModel,
    db: AsyncSession = Depends(get_db_by_tenant)
):
    service = SkuService(db)
    flag, msg = await service.update(view_model.id, view_model)
    
    if not flag:
        return error_response(msg)
    
    result = await service.get_by_id(view_model.id)
    return success_response(result)


@router.post("/sku/delete")
async def delete_sku(
    id: int = Query(..., description="SKU ID"),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    service = SkuService(db)
    flag, msg = await service.delete(id)
    
    if not flag:
        return error_response(msg)
    
    return success_response({"id": id})
