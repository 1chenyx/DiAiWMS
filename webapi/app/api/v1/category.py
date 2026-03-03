from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.schemas.category import CategoryViewModel, CategoryCreateViewModel, CategoryUpdateViewModel, CategoryTreeViewModel
from app.services.category_service import CategoryService
from app.core.database import get_db
from app.api.dependencies import get_db_by_tenant
from app.api.responses import success_response, error_response

router = APIRouter()


@router.get("/category", response_model=CategoryViewModel)
async def get_category(
    id: int = Query(..., description="分类ID"),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    根据ID获取分类信息
    
    Args:
        id: 分类ID
        db: 数据库会话
        
    Returns:
        分类信息
    """
    service = CategoryService(db)
    result = await service.get_by_id(id)
    
    if result is None:
        return error_response("分类不存在")
    
    return success_response(result)


@router.get("/category/list")
async def get_category_list(
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    获取所有分类列表
    
    Args:
        db: 数据库会话
        
    Returns:
        分类列表
    """
    from app.core.current_user import CurrentUser
    
    current_user = CurrentUser()
    service = CategoryService(db)
    result = await service.get_all(current_user)
    
    return success_response(result)


@router.get("/category/tree", response_model=List[CategoryTreeViewModel])
async def get_category_tree(
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    获取分类树形结构
    
    最高级分类的父ID为0
    
    Args:
        db: 数据库会话
        
    Returns:
        分类树形结构列表
    """
    from app.core.current_user import CurrentUser
    
    current_user = CurrentUser()
    service = CategoryService(db)
    result = await service.get_tree(current_user)
    
    return success_response(result)


@router.post("/category", response_model=CategoryViewModel)
async def create_category(
    view_model: CategoryCreateViewModel,
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    创建新分类
    
    Args:
        view_model: 分类创建数据
        db: 数据库会话
        
    Returns:
        创建的分类信息
    """
    from app.core.current_user import CurrentUser
    
    current_user = CurrentUser()
    service = CategoryService(db)
    id, msg = await service.add(view_model, current_user)
    
    if id == 0:
        return error_response(msg)
    
    result = await service.get_by_id(id)
    return success_response(result)


@router.post("/category/update", response_model=CategoryViewModel)
async def update_category(
    view_model: CategoryUpdateViewModel,
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    更新分类信息
    
    Args:
        view_model: 分类更新数据
        db: 数据库会话
        
    Returns:
        更新后的分类信息
    """
    from app.core.current_user import CurrentUser
    
    current_user = CurrentUser()
    service = CategoryService(db)
    flag, msg = await service.update(view_model.id, view_model, current_user)
    
    if not flag:
        return error_response(msg)
    
    result = await service.get_by_id(view_model.id)
    return success_response(result)


@router.post("/category/delete")
async def delete_category(
    id: int = Query(..., description="分类ID"),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    删除分类
    
    Args:
        id: 分类ID
        db: 数据库会话
        
    Returns:
        删除结果
    """
    service = CategoryService(db)
    flag, msg = await service.delete(id)
    
    if not flag:
        return error_response(msg)
    
    return success_response({"id": id})
