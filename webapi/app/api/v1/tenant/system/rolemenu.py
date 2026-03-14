from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.dependencies import get_db_by_tenant
from app.services.system.rolemenu_service import RolemenuService
from app.schemas.system.rolemenu import RolemenuCreate, RolemenuUpdate, RolemenuViewModel
from app.core.response import success_response, error_response
from app.core.current_user import CurrentUser
from app.core.dependencies import get_current_user

_tag = "系统管理-角色菜单"
router = APIRouter()


@router.post("/rolemenu/list")
async def search_rolemenu(
    page_index: int = Query(1, ge=1, description='页码'),
    page_size: int = Query(10, ge=1, le=100, description='每页数量'),
    userrole_id: int = Query(None, description='用户角色ID'),
    db: AsyncSession = Depends(get_db_by_tenant),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    分页查询角色菜单列表
    
    Args:
        page_index: 页码,从1开始
        page_size: 每页数量
        userrole_id: 用户角色ID
        db: 数据库会话
        current_user: 当前登录用户
        
    Returns:
        角色菜单列表和总数
    """
    service = RolemenuService(db)
    data, totals = await service.search(
        page_index=page_index,
        page_size=page_size,
        userrole_id=userrole_id,
        current_user=current_user
    )
    
    return success_response({
        'rows': data,
        'totals': totals
    })


@router.get("/rolemenu")
async def get_rolemenu(
    id: int = Query(..., description='角色菜单ID'),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    根据ID获取角色菜单信息
    
    Args:
        id: 角色菜单ID
        db: 数据库会话
        
    Returns:
        角色菜单信息
    """
    service = RolemenuService(db)
    result = await service.get_by_id(id)
    
    if result is None:
        return error_response("记录不存在")
    
    return success_response(result)


@router.post("/rolemenu")
async def create_rolemenu(
    data: RolemenuCreate,
    db: AsyncSession = Depends(get_db_by_tenant),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    创建角色菜单
    
    Args:
        data: 角色菜单创建数据
        db: 数据库会话
        current_user: 当前登录用户
        
    Returns:
        创建的角色菜单信息
    """
    service = RolemenuService(db)
    rolemenu_id, msg = await service.create(data, current_user)
    
    if rolemenu_id == 0:
        return error_response(msg)
    
    result = await service.get_by_id(rolemenu_id)
    return success_response(result)


@router.post("/rolemenu/update")
async def update_rolemenu(
    data: RolemenuUpdate,
    db: AsyncSession = Depends(get_db_by_tenant),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    更新角色菜单信息
    
    Args:
        data: 角色菜单更新数据
        db: 数据库会话
        current_user: 当前登录用户
        
    Returns:
        更新后的角色菜单信息
    """
    service = RolemenuService(db)
    flag, msg = await service.update(data, current_user)
    
    if not flag:
        return error_response(msg)
    
    result = await service.get_by_id(data.id)
    return success_response(result)


@router.post("/rolemenu/delete")
async def delete_rolemenu(
    id: int = Query(..., description='角色菜单ID'),
    db: AsyncSession = Depends(get_db_by_tenant),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    删除角色菜单
    
    Args:
        id: 角色菜单ID
        db: 数据库会话
        current_user: 当前登录用户
        
    Returns:
        删除结果
    """
    service = RolemenuService(db)
    flag, msg = await service.delete(id, current_user)
    
    if not flag:
        return error_response(msg)
    
    return success_response(msg)
