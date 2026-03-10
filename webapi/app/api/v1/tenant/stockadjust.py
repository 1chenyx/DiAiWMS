from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.dependencies import get_db_by_tenant
from app.services.stockadjust_service import StockadjustService
from app.schemas.stockadjust import StockadjustCreate, StockadjustUpdate, StockadjustViewModel
from app.core.response import success_response, error_response
from app.core.current_user import CurrentUser
from app.core.dependencies import get_current_user

router = APIRouter()


@router.post("/stockadjust/list")
async def search_stockadjust(
    page_index: int = Query(1, ge=1, description='页码'),
    page_size: int = Query(10, ge=1, le=100, description='每页数量'),
    job_code: str = Query(None, description='作业编号'),
    db: AsyncSession = Depends(get_db_by_tenant),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    分页查询库存调整列表
    
    Args:
        page_index: 页码,从1开始
        page_size: 每页数量
        job_code: 作业编号(模糊查询)
        db: 数据库会话
        current_user: 当前登录用户
        
    Returns:
        库存调整列表和总数
    """
    service = StockadjustService(db)
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


@router.get("/stockadjust")
async def get_stockadjust(
    id: int = Query(..., description='库存调整ID'),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    根据ID获取库存调整信息
    
    Args:
        id: 库存调整ID
        db: 数据库会话
        
    Returns:
        库存调整信息
    """
    service = StockadjustService(db)
    result = await service.get_by_id(id)
    
    if result is None:
        return error_response("记录不存在")
    
    return success_response(result)


@router.post("/stockadjust")
async def create_stockadjust(
    data: StockadjustCreate,
    db: AsyncSession = Depends(get_db_by_tenant),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    创建库存调整
    
    Args:
        data: 库存调整创建数据
        db: 数据库会话
        current_user: 当前登录用户
        
    Returns:
        创建的库存调整信息
    """
    service = StockadjustService(db)
    stockadjust_id, msg = await service.create(data, current_user)
    
    if stockadjust_id == 0:
        return error_response(msg)
    
    result = await service.get_by_id(stockadjust_id)
    return success_response(result)


@router.post("/stockadjust/update")
async def update_stockadjust(
    data: StockadjustUpdate,
    db: AsyncSession = Depends(get_db_by_tenant),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    更新库存调整信息
    
    Args:
        data: 库存调整更新数据
        db: 数据库会话
        current_user: 当前登录用户
        
    Returns:
        更新后的库存调整信息
    """
    service = StockadjustService(db)
    flag, msg = await service.update(data, current_user)
    
    if not flag:
        return error_response(msg)
    
    result = await service.get_by_id(data.id)
    return success_response(result)


@router.post("/stockadjust/delete")
async def delete_stockadjust(
    id: int = Query(..., description='库存调整ID'),
    db: AsyncSession = Depends(get_db_by_tenant),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    删除库存调整
    
    Args:
        id: 库存调整ID
        db: 数据库会话
        current_user: 当前登录用户
        
    Returns:
        删除结果
    """
    service = StockadjustService(db)
    flag, msg = await service.delete(id, current_user)
    
    if not flag:
        return error_response(msg)
    
    return success_response(msg)
