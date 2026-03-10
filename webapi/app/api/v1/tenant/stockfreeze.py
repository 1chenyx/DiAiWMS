from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.dependencies import get_db_by_tenant
from app.services.stockfreeze_service import StockfreezeService
from app.schemas.stockfreeze import StockfreezeCreate, StockfreezeUpdate, StockfreezeViewModel
from app.core.response import success_response, error_response
from app.core.current_user import CurrentUser
from app.core.dependencies import get_current_user

router = APIRouter()


@router.post("/stockfreeze/list")
async def search_stockfreeze(
    page_index: int = Query(1, ge=1, description='页码'),
    page_size: int = Query(10, ge=1, le=100, description='每页数量'),
    job_code: str = Query(None, description='作业编号'),
    db: AsyncSession = Depends(get_db_by_tenant),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    分页查询库存冻结列表
    
    Args:
        page_index: 页码,从1开始
        page_size: 每页数量
        job_code: 作业编号(模糊查询)
        db: 数据库会话
        current_user: 当前登录用户
        
    Returns:
        库存冻结列表和总数
    """
    service = StockfreezeService(db)
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


@router.get("/stockfreeze")
async def get_stockfreeze(
    id: int = Query(..., description='库存冻结ID'),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    根据ID获取库存冻结信息
    
    Args:
        id: 库存冻结ID
        db: 数据库会话
        
    Returns:
        库存冻结信息
    """
    service = StockfreezeService(db)
    result = await service.get_by_id(id)
    
    if result is None:
        return error_response("记录不存在")
    
    return success_response(result)


@router.post("/stockfreeze")
async def create_stockfreeze(
    data: StockfreezeCreate,
    db: AsyncSession = Depends(get_db_by_tenant),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    创建库存冻结
    
    Args:
        data: 库存冻结创建数据
        db: 数据库会话
        current_user: 当前登录用户
        
    Returns:
        创建的库存冻结信息
    """
    service = StockfreezeService(db)
    stockfreeze_id, msg = await service.create(data, current_user)
    
    if stockfreeze_id == 0:
        return error_response(msg)
    
    result = await service.get_by_id(stockfreeze_id)
    return success_response(result)


@router.post("/stockfreeze/update")
async def update_stockfreeze(
    data: StockfreezeUpdate,
    db: AsyncSession = Depends(get_db_by_tenant),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    更新库存冻结信息
    
    Args:
        data: 库存冻结更新数据
        db: 数据库会话
        current_user: 当前登录用户
        
    Returns:
        更新后的库存冻结信息
    """
    service = StockfreezeService(db)
    flag, msg = await service.update(data, current_user)
    
    if not flag:
        return error_response(msg)
    
    result = await service.get_by_id(data.id)
    return success_response(result)


@router.post("/stockfreeze/delete")
async def delete_stockfreeze(
    id: int = Query(..., description='库存冻结ID'),
    db: AsyncSession = Depends(get_db_by_tenant),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    删除库存冻结
    
    Args:
        id: 库存冻结ID
        db: 数据库会话
        current_user: 当前登录用户
        
    Returns:
        删除结果
    """
    service = StockfreezeService(db)
    flag, msg = await service.delete(id, current_user)
    
    if not flag:
        return error_response(msg)
    
    return success_response(msg)
