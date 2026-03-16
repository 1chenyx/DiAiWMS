from sqlalchemy.ext.asyncio import AsyncSession
from app.initializer._db import init_db_async_session
from app.initializer import g
from app.core.tenant_database import tenant_db_pool


async def get_db():
    """
    获取数据库会话(向后兼容,默认使用主库)
    使用 context manager 确保 session 自动关闭
    
    Returns:
        异步数据库会话对象
    """
    async_session_factory = init_db_async_session(
        db_drivername=g.config.db_drivername,
        db_database=g.config.db_database,
        db_username=g.config.db_username,
        db_password=g.config.db_password,
        db_host=g.config.db_host,
        db_port=g.config.db_port,
        db_charset=g.config.db_charset,
        db_echo=g.config.app_debug,
    )
    session = async_session_factory()
    try:
        yield session
    finally:
        await session.close()


async def get_master_db():
    """
    获取主库会话(用于租户管理模块)
    使用 context manager 确保 session 自动关闭
    
    Returns:
        主库异步会话对象
    """
    session = tenant_db_pool.get_master_session()
    try:
        yield session
    finally:
        await session.close()


async def get_tenant_db(tenant_id: str, use_slave: bool = False):
    """
    获取租户数据库会话
    使用 context manager 确保 session 自动关闭
    
    Args:
        tenant_id: 租户ID
        use_slave: 是否使用从库(用于读操作)
        
    Returns:
        租户数据库异步会话对象
    """
    session = await tenant_db_pool.get_tenant_session(tenant_id, use_slave=use_slave)
    try:
        yield session
    finally:
        await session.close()
