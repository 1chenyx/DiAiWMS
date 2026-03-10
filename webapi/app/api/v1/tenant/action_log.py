from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.dependencies import get_db_by_tenant
from app.services.action_log_service import ActionLogService
from app.schemas.action_log import ActionLogCreate, ActionLogUpdate, ActionLogViewModel
from app.core.response import success_response, error_response
from app.core.current_user import CurrentUser
from app.core.dependencies import get_current_user

router = APIRouter()


@router.post("/actionlog/list")
async def search_actionlog(
    page_index: int = Query(1, ge=1, description='页码'),
    page_size: int = Query(10, ge=1, le=100, description='每页数量'),
    vue_path: str = Query(None, description='Vue路径'),
    user_name: str = Query(None, description='用户名'),
    db: AsyncSession = Depends(get_db_by_tenant),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    分页查询操作日志列表
    
    Args:
        page_index: 页码,从1开始
        page_size: 每页数量
        vue_path: Vue路径(模糊查询)
        user_name: 用户名(模糊查询)
        db: 数据库会话
        current_user: 当前登录用户
        
    Returns:
        操作日志列表和总数
    """
    service = ActionLogService(db)
    data, totals = await service.search(
        page_index=page_index,
        page_size=page_size,
        vue_path=vue_path,
        user_name=user_name,
        current_user=current_user
    )
    
    return success_response({
        'rows': data,
        'totals': totals
    })


@router.get("/actionlog")
async def get_actionlog(
    id: int = Query(..., description='操作日志ID'),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    根据ID获取操作日志信息
    
    Args:
        id: 操作日志ID
        db: 数据库会话
        
    Returns:
        操作日志信息
    """
    service = ActionLogService(db)
    result = await service.get_by_id(id)
    
    if result is None:
        return error_response("记录不存在")
    
    return success_response(result)


@router.post("/actionlog")
async def create_actionlog(
    data: ActionLogCreate,
    db: AsyncSession = Depends(get_db_by_tenant),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    创建操作日志
    
    Args:
        data: 操作日志创建数据
        db: 数据库会话
        current_user: 当前登录用户
        
    Returns:
        创建的操作日志信息
    """
    service = ActionLogService(db)
    actionlog_id, msg = await service.create(data, current_user)
    
    if actionlog_id == 0:
        return error_response(msg)
    
    result = await service.get_by_id(actionlog_id)
    return success_response(result)


@router.post("/actionlog/update")
async def update_actionlog(
    data: ActionLogUpdate,
    db: AsyncSession = Depends(get_db_by_tenant),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    更新操作日志信息
    
    Args:
        data: 操作日志更新数据
        db: 数据库会话
        current_user: 当前登录用户
        
    Returns:
        更新后的操作日志信息
    """
    service = ActionLogService(db)
    flag, msg = await service.update(data, current_user)
    
    if not flag:
        return error_response(msg)
    
    result = await service.get_by_id(data.id)
    return success_response(result)


@router.post("/actionlog/delete")
async def delete_actionlog(
    id: int = Query(..., description='操作日志ID'),
    db: AsyncSession = Depends(get_db_by_tenant),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    删除操作日志
    
    Args:
        id: 操作日志ID
        db: 数据库会话
        current_user: 当前登录用户
        
    Returns:
        删除结果
    """
    service = ActionLogService(db)
    flag, msg = await service.delete(id, current_user)
    
    if not flag:
        return error_response(msg)
    
    return success_response(msg)
