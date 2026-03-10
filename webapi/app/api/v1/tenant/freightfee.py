from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.dependencies import get_db_by_tenant
from app.services.freightfee_service import FreightfeeService
from app.schemas.freightfee import FreightfeeCreate, FreightfeeUpdate, FreightfeeViewModel
from app.core.response import success_response, error_response
from app.core.current_user import CurrentUser
from app.core.dependencies import get_current_user

router = APIRouter()


@router.post("/freightfee/list")
async def search_freightfee(
    page_index: int = Query(1, ge=1, description='页码'),
    page_size: int = Query(10, ge=1, le=100, description='每页数量'),
    carrier: str = Query(None, description='承运商'),
    departure_city: str = Query(None, description='出发城市'),
    arrival_city: str = Query(None, description='到达城市'),
    db: AsyncSession = Depends(get_db_by_tenant),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    分页查询运费列表
    
    Args:
        page_index: 页码,从1开始
        page_size: 每页数量
        carrier: 承运商(模糊查询)
        departure_city: 出发城市(模糊查询)
        arrival_city: 到达城市(模糊查询)
        db: 数据库会话
        current_user: 当前登录用户
        
    Returns:
        运费列表和总数
    """
    service = FreightfeeService(db)
    data, totals = await service.search(
        page_index=page_index,
        page_size=page_size,
        carrier=carrier,
        departure_city=departure_city,
        arrival_city=arrival_city,
        current_user=current_user
    )
    
    return success_response({
        'rows': data,
        'totals': totals
    })


@router.get("/freightfee")
async def get_freightfee(
    id: int = Query(..., description='运费ID'),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    根据ID获取运费信息
    
    Args:
        id: 运费ID
        db: 数据库会话
        
    Returns:
        运费信息
    """
    service = FreightfeeService(db)
    result = await service.get_by_id(id)
    
    if result is None:
        return error_response("记录不存在")
    
    return success_response(result)


@router.post("/freightfee")
async def create_freightfee(
    data: FreightfeeCreate,
    db: AsyncSession = Depends(get_db_by_tenant),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    创建运费
    
    Args:
        data: 运费创建数据
        db: 数据库会话
        current_user: 当前登录用户
        
    Returns:
        创建的运费信息
    """
    service = FreightfeeService(db)
    freightfee_id, msg = await service.create(data, current_user)
    
    if freightfee_id == 0:
        return error_response(msg)
    
    result = await service.get_by_id(freightfee_id)
    return success_response(result)


@router.post("/freightfee/update")
async def update_freightfee(
    data: FreightfeeUpdate,
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    更新运费信息
    
    Args:
        data: 运费更新数据
        db: 数据库会话
        
    Returns:
        更新后的运费信息
    """
    service = FreightfeeService(db)
    flag, msg = await service.update(data)
    
    if not flag:
        return error_response(msg)
    
    result = await service.get_by_id(data.id)
    return success_response(result)


@router.post("/freightfee/delete")
async def delete_freightfee(
    id: int = Query(..., description='运费ID'),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    删除运费
    
    Args:
        id: 运费ID
        db: 数据库会话
        
    Returns:
        删除结果
    """
    service = FreightfeeService(db)
    flag, msg = await service.delete(id)
    
    if not flag:
        return error_response(msg)
    
    return success_response(msg)
