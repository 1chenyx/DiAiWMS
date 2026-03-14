from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies import get_db_by_tenant, get_current_user
from app.api.responses import success_response, error_response
from app.schemas.system.ai_config import (
    TenantAIConfigViewModel,
    TenantAIConfigCreateViewModel,
    TenantAIConfigUpdateViewModel
)
from app.services.system.ai_config_service import TenantAIConfigService


_tag = "系统管理-AI配置"
router = APIRouter(prefix="/ai/tenant-config")


@router.get("/list")
async def get_config_list(
    provider_code: Optional[str] = Query(None, description="提供商代码"),
    is_default: Optional[bool] = Query(None, description="是否默认配置"),
    page_index: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db_by_tenant),
    current_user = Depends(get_current_user)
):
    """
    获取租户AI配置列表
    
    Args:
        provider_code: 提供商代码
        is_default: 是否默认配置
        page_index: 页码
        page_size: 每页数量
        db: 数据库会话
        current_user: 当前用户
        
    Returns:
        配置列表
    """
    service = TenantAIConfigService(db)
    result = await service.get_list(
        tenant_id=current_user.tenant_id,
        provider_code=provider_code,
        is_default=is_default,
        page_index=page_index,
        page_size=page_size
    )
    
    return success_response(result)


@router.get("/get")
async def get_config(
    config_id: int = Query(..., description="配置ID"),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    获取租户AI配置
    
    Args:
        config_id: 配置ID
        db: 数据库会话
        
    Returns:
        配置信息
    """
    service = TenantAIConfigService(db)
    config = await service.get_by_id(config_id)
    
    if config is None:
        return error_response("配置不存在")
    
    return success_response(config)


@router.get("/default")
async def get_default_config(
    db: AsyncSession = Depends(get_db_by_tenant),
    current_user = Depends(get_current_user)
):
    """
    获取默认租户AI配置
    
    Args:
        db: 数据库会话
        current_user: 当前用户
        
    Returns:
        默认配置信息
    """
    service = TenantAIConfigService(db)
    config = await service.get_default(current_user.tenant_id)
    
    if config is None:
        return error_response("未找到默认配置")
    
    return success_response(config)


@router.post("/")
async def create_config(
    view_model: TenantAIConfigCreateViewModel,
    db: AsyncSession = Depends(get_db_by_tenant),
    current_user = Depends(get_current_user)
):
    """
    创建租户AI配置
    
    Args:
        view_model: 配置创建视图模型
        db: 数据库会话
        current_user: 当前用户
        
    Returns:
        配置信息
    """
    service = TenantAIConfigService(db)
    config = await service.create(
        view_model=view_model,
        tenant_id=current_user.tenant_id,
        creator=current_user.user_name
    )
    
    if config is None:
        return error_response("创建配置失败")
    
    return success_response(config)


@router.post("/update")
async def update_config(
    view_model: TenantAIConfigUpdateViewModel,
    config_id: int = Query(..., description="配置ID"),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    更新租户AI配置
    
    Args:
        config_id: 配置ID
        view_model: 配置更新视图模型
        db: 数据库会话
        
    Returns:
        配置信息
    """
    service = TenantAIConfigService(db)
    config = await service.update(config_id, view_model)
    
    if config is None:
        return error_response("配置不存在")
    
    return success_response(config)


@router.post("/delete")
async def delete_config(
    config_id: int = Query(..., description="配置ID"),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    删除租户AI配置
    
    Args:
        config_id: 配置ID
        db: 数据库会话
        
    Returns:
        删除结果
    """
    service = TenantAIConfigService(db)
    success = await service.delete(config_id)
    
    if not success:
        return error_response("配置不存在")
    
    return success_response({"message": "删除成功"})


@router.post("/set-default")
async def set_default_config(
    config_id: int = Query(..., description="配置ID"),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    设置为默认配置
    
    Args:
        config_id: 配置ID
        db: 数据库会话
        
    Returns:
        配置信息
    """
    service = TenantAIConfigService(db)
    config = await service.set_default(config_id)
    
    if config is None:
        return error_response("配置不存在")
    
    return success_response(config)
