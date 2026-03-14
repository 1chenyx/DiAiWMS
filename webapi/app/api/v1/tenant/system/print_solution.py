from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.dependencies import get_db_by_tenant
from app.services.system.print_solution_service import PrintSolutionService
from app.schemas.system.print_solution import PrintSolutionCreate, PrintSolutionUpdate, PrintSolutionViewModel
from app.core.response import success_response, error_response
from app.core.current_user import CurrentUser
from app.core.dependencies import get_current_user

_tag = "系统管理-打印方案"
router = APIRouter()


@router.post("/printsolution/list")
async def search_printsolution(
    page_index: int = Query(1, ge=1, description='页码'),
    page_size: int = Query(10, ge=1, le=100, description='每页数量'),
    vue_path: str = Query(None, description='Vue路径'),
    solution_name: str = Query(None, description='方案名称'),
    db: AsyncSession = Depends(get_db_by_tenant),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    分页查询打印方案列表
    
    Args:
        page_index: 页码,从1开始
        page_size: 每页数量
        vue_path: Vue路径(模糊查询)
        solution_name: 方案名称(模糊查询)
        db: 数据库会话
        current_user: 当前登录用户
        
    Returns:
        打印方案列表和总数
    """
    service = PrintSolutionService(db)
    data, totals = await service.search(
        page_index=page_index,
        page_size=page_size,
        vue_path=vue_path,
        solution_name=solution_name,
        current_user=current_user
    )
    
    return success_response({
        'rows': data,
        'totals': totals
    })


@router.get("/printsolution")
async def get_printsolution(
    id: int = Query(..., description='打印方案ID'),
    db: AsyncSession = Depends(get_db_by_tenant)
):
    """
    根据ID获取打印方案信息
    
    Args:
        id: 打印方案ID
        db: 数据库会话
        
    Returns:
        打印方案信息
    """
    service = PrintSolutionService(db)
    result = await service.get_by_id(id)
    
    if result is None:
        return error_response("记录不存在")
    
    return success_response(result)


@router.post("/printsolution")
async def create_printsolution(
    data: PrintSolutionCreate,
    db: AsyncSession = Depends(get_db_by_tenant),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    创建打印方案
    
    Args:
        data: 打印方案创建数据
        db: 数据库会话
        current_user: 当前登录用户
        
    Returns:
        创建的打印方案信息
    """
    service = PrintSolutionService(db)
    printsolution_id, msg = await service.create(data, current_user)
    
    if printsolution_id == 0:
        return error_response(msg)
    
    result = await service.get_by_id(printsolution_id)
    return success_response(result)


@router.post("/printsolution/update")
async def update_printsolution(
    data: PrintSolutionUpdate,
    db: AsyncSession = Depends(get_db_by_tenant),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    更新打印方案信息
    
    Args:
        data: 打印方案更新数据
        db: 数据库会话
        current_user: 当前登录用户
        
    Returns:
        更新后的打印方案信息
    """
    service = PrintSolutionService(db)
    flag, msg = await service.update(data, current_user)
    
    if not flag:
        return error_response(msg)
    
    result = await service.get_by_id(data.id)
    return success_response(result)


@router.post("/printsolution/delete")
async def delete_printsolution(
    id: int = Query(..., description='打印方案ID'),
    db: AsyncSession = Depends(get_db_by_tenant),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    删除打印方案
    
    Args:
        id: 打印方案ID
        db: 数据库会话
        current_user: 当前登录用户
        
    Returns:
        删除结果
    """
    service = PrintSolutionService(db)
    flag, msg = await service.delete(id, current_user)
    
    if not flag:
        return error_response(msg)
    
    return success_response(msg)
