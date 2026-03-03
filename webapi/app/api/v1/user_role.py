from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.dependencies import get_db_by_tenant
from app.services.user_role_service import UserRoleService
from app.schemas.user_role import UserRoleCreate, UserRoleUpdate, UserRoleViewModel
from app.core.response import success_response, error_response
from app.core.current_user import CurrentUser
from app.core.dependencies import get_current_user

router = APIRouter()


@router.post("/userrole/list")
async def search_userrole(
    page_index: int = Query(1, ge=1, description='页码'),
    page_size: int = Query(10, ge=1, le=100, description='每页数量'),
    role_name: str = Query(None, description='角色名称'),
    db: AsyncSession = Depends(get_db_by_tenant),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    分页查询用户角色列表
    
    Args:
        page_index: 页码,从1开始
        page_size: 每页数量
        role_name: 角色名称(模糊查询)
        db: 数据库会话
        current_user: 当前登录用户
        
    Returns:
        用户角色列表和总数
    """
    service = UserRoleService(db)
    data, totals = await service.search(
        page_index=page_index,
        page_size=page_size,
        role_name=role_name,
        current_user=current_user
    )
    
    return success_response({
        'rows': data,
        'totals': totals
    })


@router.get("/userrole")
async def get_userrole(
    id: int = Query(..., description='用户角色ID'),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    根据ID获取用户角色信息
    
    Args:
        id: 用户角色ID
        db: 数据库会话
        
    Returns:
        用户角色信息
    """
    service = UserRoleService(db)
    result = await service.get_by_id(id)
    
    if result is None:
        return error_response("记录不存在")
    
    return success_response(result)


@router.post("/userrole")
async def create_userrole(
    data: UserRoleCreate,
    db: AsyncSession = Depends(get_db_by_tenant),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    创建用户角色
    
    Args:
        data: 用户角色创建数据
        db: 数据库会话
        current_user: 当前登录用户
        
    Returns:
        创建的用户角色信息
    """
    service = UserRoleService(db)
    userrole_id, msg = await service.create(data, current_user)
    
    if userrole_id == 0:
        return error_response(msg)
    
    result = await service.get_by_id(userrole_id)
    return success_response(result)


@router.post("/userrole/update")
async def update_userrole(
    data: UserRoleUpdate,
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    更新用户角色信息
    
    Args:
        data: 用户角色更新数据
        db: 数据库会话
        
    Returns:
        更新后的用户角色信息
    """
    service = UserRoleService(db)
    flag, msg = await service.update(data)
    
    if not flag:
        return error_response(msg)
    
    result = await service.get_by_id(data.id)
    return success_response(result)


@router.post("/userrole/delete")
async def delete_userrole(
    id: int = Query(..., description='用户角色ID'),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    删除用户角色
    
    Args:
        id: 用户角色ID
        db: 数据库会话
        
    Returns:
        删除结果
    """
    service = UserRoleService(db)
    flag, msg = await service.delete(id)
    
    if not flag:
        return error_response(msg)
    
    return success_response(msg)
