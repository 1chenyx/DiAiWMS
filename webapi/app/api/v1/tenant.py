from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.dependencies import get_master_db_session
from app.services.tenant_service import TenantService
from app.schemas.tenant import TenantCreateViewModel, TenantUpdateViewModel, TenantViewModel
from app.api.responses import success_response, error_response

router = APIRouter()


@router.post("/tenant/list")
async def search_tenant(
    page_index: int = Query(1, ge=1, description='页码'),
    page_size: int = Query(10, ge=1, le=100, description='每页数量'),
    tenant_name: str = Query(None, description='租户名称'),
    tenant_code: str = Query(None, description='租户编码'),
    db: AsyncSession = Depends(get_master_db_session)
):
    """
    分页查询租户列表
    
    Args:
        page_index: 页码,从1开始
        page_size: 每页数量
        tenant_name: 租户名称(模糊查询)
        tenant_code: 租户编码(模糊查询)
        db: 数据库会话
        
    Returns:
        租户列表和总数
    """
    service = TenantService(db)
    data, totals = await service.search(
        page_index=page_index,
        page_size=page_size,
        tenant_name=tenant_name,
        tenant_code=tenant_code
    )
    
    return success_response({
        'rows': data,
        'totals': totals
    })


@router.get("/tenant")
async def get_tenant(
    id: int = Query(..., description='租户ID'),
    db: AsyncSession = Depends(get_master_db_session)
):
    """
    根据ID获取租户信息
    
    Args:
        id: 租户ID
        db: 数据库会话
        
    Returns:
        租户信息
    """
    service = TenantService(db)
    result = await service.get_by_id(id)
    
    if result is None:
        return error_response("记录不存在")
    
    return success_response(result)


@router.post("/tenant")
async def create_tenant(
    data: TenantCreateViewModel,
    db: AsyncSession = Depends(get_master_db_session)
):
    """
    创建新租户
    
    Args:
        data: 租户创建数据
        db: 数据库会话
        
    Returns:
        创建的租户信息
    """
    from app.core.current_user import CurrentUser
    
    current_user = CurrentUser(
        user_id=1,
        user_num='admin',
        user_name='admin',
        user_role='admin',
        tenant_id=1,
        userrole_id=1
    )
    
    service = TenantService(db)
    tenant_id, msg = await service.create(data, current_user)
    
    if tenant_id == 0:
        return error_response(msg)
    
    result = await service.get_by_id(tenant_id)
    return success_response(result)


@router.post("/tenant/update")
async def update_tenant(
    data: TenantUpdateViewModel,
    db: AsyncSession = Depends(get_master_db_session)
):
    """
    更新租户信息
    
    Args:
        data: 租户更新数据
        db: 数据库会话
        
    Returns:
        更新后的租户信息
    """
    service = TenantService(db)
    flag, msg = await service.update(data)
    
    if not flag:
        return error_response(msg)
    
    result = await service.get_by_id(data.id)
    return success_response(result)


@router.post("/tenant/delete")
async def delete_tenant(
    id: int = Query(..., description='租户ID'),
    db: AsyncSession = Depends(get_master_db_session)
):
    """
    删除租户
    
    Args:
        id: 租户ID
        db: 数据库会话
        
    Returns:
        删除结果
    """
    service = TenantService(db)
    flag, msg = await service.delete(id)
    
    if not flag:
        return error_response(msg)
    
    return success_response(msg)
