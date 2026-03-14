from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.dependencies import get_db_by_tenant
from app.services.inventory.stockmove_service import StockmoveService
from app.schemas.inventory.stockmove import StockmoveCreate, StockmoveUpdate, StockmoveViewModel
from app.core.response import success_response, error_response
from app.core.current_user import CurrentUser
from app.core.dependencies import get_current_user

_tag = "库存管理-库存移动"
router = APIRouter()


@router.post("/stockmove/list")
async def search_stockmove(
    page_index: int = Query(1, ge=1, description='页码'),
    page_size: int = Query(10, ge=1, le=100, description='每页数量'),
    job_code: str = Query(None, description='作业编号'),
    db: AsyncSession = Depends(get_db_by_tenant),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    分页查询库存移动列表
    
    Args:
        page_index: 页码,从1开始
        page_size: 每页数量
        job_code: 作业编号(模糊查询)
        db: 数据库会话
        current_user: 当前登录用户
        
    Returns:
        库存移动列表和总数
    """
    service = StockmoveService(db)
    data, totals = await service.search(
        page_index=page_index,
        page_size=page_size,
        job_code=job_code,
        current_user=current_user
    )
    
    return success_response({
        'rows': data,
        'totals': totals
    })


@router.get("/stockmove")
async def get_stockmove(
    id: int = Query(..., description='库存移动ID'),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    根据ID获取库存移动信息
    
    Args:
        id: 库存移动ID
        db: 数据库会话
        
    Returns:
        库存移动信息
    """
    service = StockmoveService(db)
    result = await service.get_by_id(id)
    
    if result is None:
        return error_response("记录不存在")
    
    return success_response(result)


@router.post("/stockmove")
async def create_stockmove(
    data: StockmoveCreate,
    db: AsyncSession = Depends(get_db_by_tenant),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    创建库存移动
    
    Args:
        data: 库存移动创建数据
        db: 数据库会话
        current_user: 当前登录用户
        
    Returns:
        创建的库存移动信息
    """
    service = StockmoveService(db)
    stockmove_id, msg = await service.create(data, current_user)
    
    if stockmove_id == 0:
        return error_response(msg)
    
    result = await service.get_by_id(stockmove_id)
    return success_response(result)


@router.post("/stockmove/update")
async def update_stockmove(
    data: StockmoveUpdate,
    db: AsyncSession = Depends(get_db_by_tenant),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    更新库存移动信息
    
    Args:
        data: 库存移动更新数据
        db: 数据库会话
        current_user: 当前登录用户
        
    Returns:
        更新后的库存移动信息
    """
    service = StockmoveService(db)
    flag, msg = await service.update(data, current_user)
    
    if not flag:
        return error_response(msg)
    
    result = await service.get_by_id(data.id)
    return success_response(result)


@router.post("/stockmove/delete")
async def delete_stockmove(
    id: int = Query(..., description='库存移动ID'),
    db: AsyncSession = Depends(get_db_by_tenant),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    删除库存移动
    
    Args:
        id: 库存移动ID
        db: 数据库会话
        current_user: 当前登录用户
        
    Returns:
        删除结果
    """
    service = StockmoveService(db)
    flag, msg = await service.delete(id, current_user)
    
    if not flag:
        return error_response(msg)
    
    return success_response(msg)
