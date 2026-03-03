from typing import Dict, Optional
from sqlalchemy import URL
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from loguru import logger
from toollib.utils import Singleton


class TenantDatabaseConfig:
    """
    租户数据库配置
    
    存储单个租户的数据库连接信息
    """
    def __init__(
        self,
        db_drivername: str,
        db_database: str,
        db_username: str,
        db_password: str,
        db_host: str,
        db_port: int,
        db_charset: str,
        db_pool_size: int = 20,
        db_max_overflow: int = 10,
        db_pool_recycle: int = 3600,
        slave_host: Optional[str] = None,
        slave_port: Optional[int] = None,
    ):
        self.db_drivername = db_drivername
        self.db_database = db_database
        self.db_username = db_username
        self.db_password = db_password
        self.db_host = db_host
        self.db_port = db_port
        self.db_charset = db_charset
        self.db_pool_size = db_pool_size
        self.db_max_overflow = db_max_overflow
        self.db_pool_recycle = db_pool_recycle
        self.slave_host = slave_host
        self.slave_port = slave_port

    def get_db_url(self, is_slave: bool = False) -> URL:
        """
        构建数据库连接URL
        
        Args:
            is_slave: 是否为从库
            
        Returns:
            数据库连接URL对象
        """
        query = {}
        if not self.db_drivername.startswith("postgresql"):
            query["charset"] = self.db_charset
        
        host = self.slave_host if is_slave and self.slave_host else self.db_host
        port = self.slave_port if is_slave and self.slave_port else self.db_port
        
        return URL.create(
            drivername=self.db_drivername,
            username=self.db_username,
            password=self.db_password,
            host=host,
            port=port,
            database=self.db_database,
            query=query,
        )


class TenantDatabasePool(metaclass=Singleton):
    """
    租户数据库连接池管理器
    
    管理所有租户的数据库连接池，支持动态添加和获取租户数据库连接
    支持主从数据库读写分离
    """
    
    def __init__(self):
        self._master_engine = None
        self._master_session_factory = None
        self._slave_engine = None
        self._slave_session_factory = None
        self._tenant_engines: Dict[str, Dict[str, any]] = {}
        self._tenant_configs: Dict[str, TenantDatabaseConfig] = {}
        
    def initialize_master(
        self,
        db_drivername: str,
        db_database: str,
        db_username: str,
        db_password: str,
        db_host: str,
        db_port: int,
        db_charset: str,
        db_echo: bool = False,
        db_pool_size: int = 20,
        db_max_overflow: int = 10,
        db_pool_recycle: int = 3600,
        slave_host: Optional[str] = None,
        slave_port: Optional[int] = None,
    ):
        """
        初始化主库连接池
        
        Args:
            db_drivername: 数据库驱动类型
            db_database: 数据库名称
            db_username: 数据库用户名
            db_password: 数据库密码
            db_host: 数据库主机
            db_port: 数据库端口
            db_charset: 数据库字符集
            db_echo: 是否打印SQL语句
            db_pool_size: 连接池大小
            db_max_overflow: 连接池最大溢出数
            db_pool_recycle: 连接回收时间(秒)
            slave_host: 从库主机(可选)
            slave_port: 从库端口(可选)
        """
        config = TenantDatabaseConfig(
            db_drivername=db_drivername,
            db_database=db_database,
            db_username=db_username,
            db_password=db_password,
            db_host=db_host,
            db_port=db_port,
            db_charset=db_charset,
            db_pool_size=db_pool_size,
            db_max_overflow=db_max_overflow,
            db_pool_recycle=db_pool_recycle,
            slave_host=slave_host,
            slave_port=slave_port,
        )
        
        db_url = config.get_db_url(is_slave=False)
        kwargs = {
            "pool_size": db_pool_size,
            "max_overflow": db_max_overflow,
            "pool_recycle": db_pool_recycle,
        }
        
        if db_url.drivername.startswith("sqlite"):
            kwargs = {}
        
        self._master_engine = create_async_engine(
            url=db_url,
            echo=db_echo,
            pool_pre_ping=True,
            **kwargs,
        )
        
        self._master_session_factory = async_sessionmaker(
            self._master_engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        if slave_host and slave_port:
            slave_url = config.get_db_url(is_slave=True)
            self._slave_engine = create_async_engine(
                url=slave_url,
                echo=db_echo,
                pool_pre_ping=True,
                **kwargs,
            )
            
            self._slave_session_factory = async_sessionmaker(
                self._slave_engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            logger.info("主从库连接池初始化成功")
        else:
            logger.info("主库连接池初始化成功")
    
    async def add_tenant_database(
        self,
        tenant_id: str,
        db_drivername: str,
        db_database: str,
        db_username: str,
        db_password: str,
        db_host: str,
        db_port: int,
        db_charset: str,
        db_echo: bool = False,
        db_pool_size: int = 20,
        db_max_overflow: int = 10,
        db_pool_recycle: int = 3600,
        slave_host: Optional[str] = None,
        slave_port: Optional[int] = None,
    ):
        """
        添加租户数据库连接池
        
        Args:
            tenant_id: 租户ID(UUID字符串)
            db_drivername: 数据库驱动类型
            db_database: 数据库名称
            db_username: 数据库用户名
            db_password: 数据库密码
            db_host: 数据库主机
            db_port: 数据库端口
            db_charset: 数据库字符集
            db_echo: 是否打印SQL语句
            db_pool_size: 连接池大小
            db_max_overflow: 连接池最大溢出数
            db_pool_recycle: 连接回收时间(秒)
            slave_host: 从库主机(可选)
            slave_port: 从库端口(可选)
        """
        if tenant_id in self._tenant_engines:
            logger.warning(f"租户 {tenant_id} 的数据库连接池已存在，将被替换")
            await self.remove_tenant_database(tenant_id)
        
        config = TenantDatabaseConfig(
            db_drivername=db_drivername,
            db_database=db_database,
            db_username=db_username,
            db_password=db_password,
            db_host=db_host,
            db_port=db_port,
            db_charset=db_charset,
            db_pool_size=db_pool_size,
            db_max_overflow=db_max_overflow,
            db_pool_recycle=db_pool_recycle,
            slave_host=slave_host,
            slave_port=slave_port,
        )
        
        self._tenant_configs[tenant_id] = config
        
        db_url = config.get_db_url(is_slave=False)
        kwargs = {
            "pool_size": db_pool_size,
            "max_overflow": db_max_overflow,
            "pool_recycle": db_pool_recycle,
        }
        
        if db_url.drivername.startswith("sqlite"):
            kwargs = {}
        
        engine = create_async_engine(
            url=db_url,
            echo=db_echo,
            pool_pre_ping=True,
            **kwargs,
        )
        
        session_factory = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        slave_session_factory = None
        if slave_host and slave_port:
            slave_url = config.get_db_url(is_slave=True)
            slave_engine = create_async_engine(
                url=slave_url,
                echo=db_echo,
                pool_pre_ping=True,
                **kwargs,
            )
            
            slave_session_factory = async_sessionmaker(
                slave_engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
        
        self._tenant_engines[tenant_id] = {
            "engine": engine,
            "session_factory": session_factory,
            "slave_session_factory": slave_session_factory,
        }
        
        if slave_session_factory:
            logger.info(f"租户 {tenant_id} 的主从数据库连接池添加成功")
        else:
            logger.info(f"租户 {tenant_id} 的数据库连接池添加成功")
    
    async def remove_tenant_database(self, tenant_id: str):
        """
        移除租户数据库连接池
        
        Args:
            tenant_id: 租户ID(UUID字符串)
        """
        if tenant_id in self._tenant_engines:
            engine = self._tenant_engines[tenant_id]["engine"]
            
            await engine.dispose()
            
            del self._tenant_engines[tenant_id]
            del self._tenant_configs[tenant_id]
            logger.info(f"租户 {tenant_id} 的数据库连接池已移除")
    
    def get_master_session(self) -> AsyncSession:
        """
        获取主库会话
        
        Returns:
            主库异步会话对象
            
        Raises:
            RuntimeError: 主库未初始化
        """
        if self._master_session_factory is None:
            raise RuntimeError("主库连接池未初始化")
        return self._master_session_factory()
    
    async def get_tenant_session(self, tenant_id: str, use_slave: bool = False) -> AsyncSession:
        """
        获取租户数据库会话
        
        Args:
            tenant_id: 租户ID(UUID字符串)
            use_slave: 是否使用从库(用于读操作)
            
        Returns:
            租户数据库异步会话对象
            
        Raises:
            RuntimeError: 租户数据库连接池不存在且无法创建
        """
        if tenant_id not in self._tenant_engines:
            logger.warning(f"租户 {tenant_id} 的数据库连接池不存在，尝试自动创建")
            
            # 从主库查询租户配置
            if self._master_session_factory is None:
                raise RuntimeError("主库连接池未初始化，无法创建租户连接池")
            
            # 查询租户配置
            from app.models.entities import Tenant
            from sqlalchemy import select
            
            master_session = self._master_session_factory()
            try:
                query = select(Tenant).where(Tenant.id == tenant_id)
                result = await master_session.execute(query)
                tenant = result.scalar_one_or_none()
                
                if not tenant:
                    raise RuntimeError(f"租户 {tenant_id} 不存在，无法创建数据库连接池")
                
                # 自动创建租户连接池
                await self.add_tenant_database(
                    tenant_id=tenant_id,
                    db_drivername=tenant.db_drivername,
                    db_database=tenant.db_database,
                    db_username=tenant.db_username,
                    db_password=tenant.db_password,
                    db_host=tenant.db_host,
                    db_port=tenant.db_port,
                    db_charset=tenant.db_charset,
                    db_pool_size=tenant.db_pool_size,
                    db_max_overflow=tenant.db_max_overflow,
                    db_pool_recycle=tenant.db_pool_recycle,
                    slave_host=tenant.slave_host,
                    slave_port=tenant.slave_port,
                )
                
                logger.info(f"租户 {tenant_id} 的数据库连接池自动创建成功")
            finally:
                await master_session.close()
        
        engine_info = self._tenant_engines[tenant_id]
        
        if use_slave and engine_info["slave_session_factory"]:
            return engine_info["slave_session_factory"]()
        
        return engine_info["session_factory"]()
    
    def tenant_exists(self, tenant_id: str) -> bool:
        """
        检查租户数据库连接池是否存在
        
        Args:
            tenant_id: 租户ID(UUID字符串)
            
        Returns:
            是否存在
        """
        return tenant_id in self._tenant_engines
    
    def get_tenant_config(self, tenant_id: str) -> Optional[TenantDatabaseConfig]:
        """
        获取租户数据库配置
        
        Args:
            tenant_id: 租户ID(UUID字符串)
            
        Returns:
            租户数据库配置对象，不存在则返回None
        """
        return self._tenant_configs.get(tenant_id)
    
    async def close_all(self):
        """
        关闭所有数据库连接池
        """
        if self._master_engine:
            await self._master_engine.dispose()
            logger.info("主库连接池已关闭")
        
        if self._slave_engine:
            await self._slave_engine.dispose()
            logger.info("从库连接池已关闭")
        
        for tenant_id, engine_info in self._tenant_engines.items():
            await engine_info["engine"].dispose()
            logger.info(f"租户 {tenant_id} 的数据库连接池已关闭")
        
        self._tenant_engines.clear()
        self._tenant_configs.clear()


tenant_db_pool = TenantDatabasePool()
