from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.dependencies import get_db_by_tenant, get_current_user
from app.services.goods_owner_service import GoodsOwnerService
from app.schemas.goods_owner import GoodsOwnerCreate, GoodsOwnerUpdate, GoodsOwnerViewModel
from app.core.response import success_response, error_response
from app.core.current_user import CurrentUser

router = APIRouter()


@router.post("/goodsowner/list")
async def search_goods_owner(
    page_index: int = Query(1, ge=1, description='页码'),
    page_size: int = Query(10, ge=1, le=100, description='每页数量'),
    goods_owner_name: str = Query(None, description='货主名称'),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    分页查询货主列表
    
    Args:
        page_index: 页码,从1开始
        page_size: 每页数量
        goods_owner_name: 货主名称(模糊查询)
        current_user: 当前登录用户
        db: 数据库会话
        
    Returns:
        货主列表和总数
    """
    service = GoodsOwnerService(db)
    data, totals = await service.search(
        page_index=page_index,
        page_size=page_size,
        goods_owner_name=goods_owner_name,
        current_user=current_user
    )
    
    return success_response({
        'rows': data,
        'totals': totals
    })


@router.get("/goodsowner/all")
async def get_all_goods_owners(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    获取所有货主列表
    
    Args:
        current_user: 当前登录用户
        db: 数据库会话
        
    Returns:
        货主列表
    """
    service = GoodsOwnerService(db)
    data = await service.get_all(current_user)
    
    return success_response(data)


@router.get("/goodsowner")
async def get_goods_owner(
    id: int = Query(..., description='货主ID'),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    根据ID获取货主信息
    
    Args:
        id: 货主ID
        current_user: 当前登录用户
        db: 数据库会话
        
    Returns:
        货主信息
    """
    service = GoodsOwnerService(db)
    result = await service.get_by_id(id, current_user)
    
    if result is None:
        return error_response("记录不存在")
    
    return success_response(result)


@router.post("/goodsowner")
async def create_goods_owner(
    data: GoodsOwnerCreate,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    创建货主
    
    Args:
        data: 货主创建数据
        current_user: 当前登录用户
        db: 数据库会话
        
    Returns:
        创建的货主信息
    """
    service = GoodsOwnerService(db)
    goods_owner_id, msg = await service.create(data, current_user)
    
    if goods_owner_id == 0:
        return error_response(msg)
    
    result = await service.get_by_id(goods_owner_id, current_user)
    return success_response(result)


@router.post("/goodsowner/update")
async def update_goods_owner(
    data: GoodsOwnerUpdate,
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    更新货主信息
    
    Args:
        data: 货主更新数据
        db: 数据库会话
        
    Returns:
        更新后的货主信息
    """
    service = GoodsOwnerService(db)
    flag, msg = await service.update(data)
    
    if not flag:
        return error_response(msg)
    
    result = await service.get_by_id(data.id)
    return success_response(result)


@router.post("/goodsowner/delete")
async def delete_goods_owner(
    id: int = Query(..., description='货主ID'),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    删除货主
    
    Args:
        id: 货主ID
        db: 数据库会话
        
    Returns:
        删除结果
    """
    service = GoodsOwnerService(db)
    flag, msg = await service.delete(id)
    
    if not flag:
        return error_response(msg)
    
    return success_response(msg)
