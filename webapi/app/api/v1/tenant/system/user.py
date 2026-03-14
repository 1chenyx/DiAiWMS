from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.dependencies import get_db_by_tenant
from app.services.system.user_service import UserService
from app.schemas.system.user import UserCreateViewModel, UserUpdateViewModel, UserViewModel
from app.core.response import success_response, error_response
from app.core.current_user import CurrentUser
from app.core.dependencies import get_current_user

_tag = "系统管理-用户管理"
router = APIRouter()


@router.post("/user/list")
async def search_user(
    page_index: int = Query(1, ge=1, description='页码'),
    page_size: int = Query(10, ge=1, le=100, description='每页数量'),
    user_name: str = Query(None, description='用户名'),
    db: AsyncSession = Depends(get_db_by_tenant),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    分页查询用户列表
    
    Args:
        page_index: 页码,从1开始
        page_size: 每页数量
        user_name: 用户名(模糊查询)
        db: 数据库会话
        current_user: 当前登录用户
        
    Returns:
        用户列表和总数
    """
    service = UserService(db)
    data, totals = await service.search(
        page_index=page_index,
        page_size=page_size,
        user_name=user_name,
        current_user=current_user
    )
    
    return success_response({
        'rows': data,
        'totals': totals
    })


@router.get("/user")
async def get_user(
    id: int = Query(..., description='用户ID'),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    根据ID获取用户信息
    
    Args:
        id: 用户ID
        db: 数据库会话
        
    Returns:
        用户信息
    """
    service = UserService(db)
    result = await service.get_by_id(id)
    
    if result is None:
        return error_response("记录不存在")
    
    return success_response(result)


@router.post("/user")
async def create_user(
    data: UserCreateViewModel,
    db: AsyncSession = Depends(get_db_by_tenant),
    current_user: CurrentUser = Depends(get_current_user)
):
    service = UserService(db)
    user_id, msg = await service.create(data, current_user)
    
    if user_id == 0:
        return error_response(msg)
    
    result = await service.get_by_id(user_id)
    return success_response(result)


@router.post("/user/update")
async def update_user(
    data: UserUpdateViewModel,
    db: AsyncSession = Depends(get_db_by_tenant)
):
    service = UserService(db)
    flag, msg = await service.update(data)
    
    if not flag:
        return error_response(msg)
    
    result = await service.get_by_id(data.id)
    return success_response(result)


@router.post("/user/delete")
async def delete_user(
    id: int = Query(..., description='用户ID'),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    service = UserService(db)
    flag, msg = await service.delete(id)
    
    if not flag:
        return error_response(msg)
    
    return success_response(msg)
