from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from app.core.tenant_database import tenant_db_pool
from app.api.dependencies import get_master_db_session
from app.api.responses import success_response, error_response
from sqlalchemy.ext.asyncio import AsyncSession

_tag = "公共接口-数据库管理"
router = APIRouter()


class TenantDatabaseConfigInput(BaseModel):
    """
    租户数据库配置输入模型
    """
    tenant_id: str = Field(..., description='租户ID')
    db_drivername: str = Field(..., description='数据库驱动类型')
    db_database: str = Field(..., description='数据库名称')
    db_username: str = Field(..., description='数据库用户名')
    db_password: str = Field(..., description='数据库密码')
    db_host: str = Field(..., description='数据库主机')
    db_port: int = Field(..., description='数据库端口')
    db_charset: str = Field(default='utf8', description='数据库字符集')
    db_pool_size: int = Field(default=10, description='连接池大小')
    db_max_overflow: int = Field(default=5, description='连接池最大溢出数')
    db_pool_recycle: int = Field(default=3600, description='连接回收时间(秒)')
    slave_host: str = Field(default=None, description='从库主机(可选)')
    slave_port: int = Field(default=None, description='从库端口(可选)')


@router.post("/tenant-database/add")
async def add_tenant_database(
    data: TenantDatabaseConfigInput,
    db: AsyncSession = Depends(get_master_db_session)
):
    """
    添加租户数据库连接池
    
    Args:
        data: 租户数据库配置
        db: 主库会话
        
    Returns:
        添加结果
    """
    try:
        tenant_db_pool.add_tenant_database(
            tenant_id=data.tenant_id,
            db_drivername=data.db_drivername,
            db_database=data.db_database,
            db_username=data.db_username,
            db_password=data.db_password,
            db_host=data.db_host,
            db_port=data.db_port,
            db_charset=data.db_charset,
            db_pool_size=data.db_pool_size,
            db_max_overflow=data.db_max_overflow,
            db_pool_recycle=data.db_pool_recycle,
            slave_host=data.slave_host,
            slave_port=data.slave_port,
        )
        return success_response({"message": f"租户 {data.tenant_id} 的数据库连接池添加成功"})
    except Exception as e:
        return error_response(f"添加租户数据库连接池失败: {str(e)}")


@router.post("/tenant-database/remove")
async def remove_tenant_database(
    tenant_id: str = Query(..., description='租户ID'),
    db: AsyncSession = Depends(get_master_db_session)
):
    """
    移除租户数据库连接池
    
    Args:
        tenant_id: 租户ID(UUID字符串)
        db: 主库会话
        
    Returns:
        移除结果
    """
    try:
        tenant_db_pool.remove_tenant_database(tenant_id)
        return success_response({"message": f"租户 {tenant_id} 的数据库连接池已移除"})
    except Exception as e:
        return error_response(f"移除租户数据库连接池失败: {str(e)}")


@router.get("/tenant-database/check")
async def check_tenant_database(
    tenant_id: str = Query(..., description='租户ID'),
    db: AsyncSession = Depends(get_master_db_session)
):
    """
    检查租户数据库连接池是否存在
    
    Args:
        tenant_id: 租户ID(UUID字符串)
        db: 主库会话
        
    Returns:
        检查结果
    """
    exists = tenant_db_pool.tenant_exists(tenant_id)
    return success_response({
        "tenant_id": tenant_id,
        "exists": exists
    })


@router.get("/tenant-database/config")
async def get_tenant_database_config(
    tenant_id: str = Query(..., description='租户ID'),
    db: AsyncSession = Depends(get_master_db_session)
):
    """
    获取租户数据库配置
    
    Args:
        tenant_id: 租户ID(UUID字符串)
        db: 主库会话
        
    Returns:
        租户数据库配置
    """
    config = tenant_db_pool.get_tenant_config(tenant_id)
    if config is None:
        return error_response(f"租户 {tenant_id} 的数据库配置不存在")
    
    return success_response({
        "tenant_id": tenant_id,
        "db_drivername": config.db_drivername,
        "db_database": config.db_database,
        "db_username": config.db_username,
        "db_host": config.db_host,
        "db_port": config.db_port,
        "db_charset": config.db_charset,
        "db_pool_size": config.db_pool_size,
        "db_max_overflow": config.db_max_overflow,
        "db_pool_recycle": config.db_pool_recycle,
        "slave_host": config.slave_host,
        "slave_port": config.slave_port,
    })


@router.get("/tenant-database/list")
async def list_tenant_databases(
    db: AsyncSession = Depends(get_master_db_session)
):
    """
    列出所有租户数据库连接池
    
    Args:
        db: 主库会话
        
    Returns:
        租户数据库列表
    """
    tenant_configs = []
    for tenant_id, config in tenant_db_pool._tenant_configs.items():
        tenant_configs.append({
            "tenant_id": tenant_id,
            "db_drivername": config.db_drivername,
            "db_database": config.db_database,
            "db_username": config.db_username,
            "db_host": config.db_host,
            "db_port": config.db_port,
            "db_charset": config.db_charset,
            "db_pool_size": config.db_pool_size,
            "db_max_overflow": config.db_max_overflow,
            "db_pool_recycle": config.db_pool_recycle,
            "slave_host": config.slave_host,
            "slave_port": config.slave_port,
        })
    
    return success_response({
        "count": len(tenant_configs),
        "tenants": tenant_configs
    })
