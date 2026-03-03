from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.schemas.spu import SpuViewModel, SpuCreateViewModel, SpuUpdateViewModel
from app.services.spu_service import SpuService
from app.api.dependencies import get_db_by_tenant, get_current_user
from app.api.responses import success_response, error_response
from app.api.service_dependencies import get_service_dependency
from app.core.current_user import CurrentUser

router = APIRouter()


@router.get("/spu", response_model=SpuViewModel)
async def get_spu(
    id: int = Query(..., description="SPU ID"),
    service: SpuService = Depends(get_service_dependency(SpuService))
):
    """
    根据ID获取SPU信息
    
    Args:
        id: SPU ID
        service: SPU服务
        
    Returns:
        SPU信息
    """
    result = await service.get_by_id(id)
    
    if result is None:
        return error_response("SPU不存在")
    
    return success_response(result)


@router.get("/spu/list")
async def get_spu_list(
    current_user: CurrentUser = Depends(get_current_user),
    service: SpuService = Depends(get_service_dependency(SpuService))
):
    """
    获取SPU列表
    
    Args:
        current_user: 当前登录用户
        service: SPU服务
        
    Returns:
        SPU列表
    """
    result = await service.get_all(current_user)
    
    return success_response(result)


@router.get("/spu/page")
async def get_spu_page(
    page_index: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    spu_code: Optional[str] = Query(None, description="SPU编码"),
    spu_name: Optional[str] = Query(None, description="SPU名称"),
    category_id: Optional[int] = Query(None, description="分类ID"),
    is_valid: Optional[bool] = Query(None, description="是否有效"),
    current_user: CurrentUser = Depends(get_current_user),
    service: SpuService = Depends(get_service_dependency(SpuService))
):
    """
    分页查询SPU列表
    
    Args:
        page_index: 页码,从1开始
        page_size: 每页数量
        spu_code: SPU编码(模糊查询)
        spu_name: SPU名称(模糊查询)
        category_id: 分类ID
        is_valid: 是否有效
        current_user: 当前登录用户
        service: SPU服务
        
    Returns:
        SPU列表和总数
    """
    search_params = {}
    if spu_code:
        search_params["spu_code"] = spu_code
    if spu_name:
        search_params["spu_name"] = spu_name
    if category_id:
        search_params["category_id"] = category_id
    if is_valid is not None:
        search_params["is_valid"] = is_valid
    
    data, totals = await service.page_search(page_index, page_size, search_params, current_user)
    
    return success_response({
        "data": data,
        "totals": totals,
        "page_index": page_index,
        "page_size": page_size
    })


@router.post("/spu", response_model=SpuViewModel)
async def create_spu(
    view_model: SpuCreateViewModel,
    current_user: CurrentUser = Depends(get_current_user),
    service: SpuService = Depends(get_service_dependency(SpuService))
):
    id, msg = await service.add(view_model, current_user)
    
    if id == 0:
        return error_response(msg)
    
    result = await service.get_by_id(id)
    return success_response(result)


@router.post("/spu/update", response_model=SpuViewModel)
async def update_spu(
    view_model: SpuUpdateViewModel,
    current_user: CurrentUser = Depends(get_current_user),
    service: SpuService = Depends(get_service_dependency(SpuService))
):
    flag, msg = await service.update(view_model.id, view_model, current_user)
    
    if not flag:
        return error_response(msg)
    
    result = await service.get_by_id(view_model.id)
    return success_response(result)


@router.post("/spu/delete")
async def delete_spu(
    id: int = Query(..., description="SPU ID"),
    service: SpuService = Depends(get_service_dependency(SpuService))
):
    flag, msg = await service.delete(id)
    
    if not flag:
        return error_response(msg)
    
    return success_response({"id": id})
