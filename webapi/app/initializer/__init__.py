"""
初始化
"""
import threading
from functools import cached_property

from loguru import logger
from loguru._logger import Logger  # noqa
from sqlalchemy.orm import sessionmaker
from toollib.utils import Singleton

from app.initializer._conf import Config, init_config
from app.initializer._db import init_db_async_session
from app.initializer._log import init_logger
from app.core.tenant_database import tenant_db_pool


class G(metaclass=Singleton):
    """
    全局变量
    """
    _initialized = False
    _init_lock = threading.Lock()
    _init_properties = [
        "config",
        "logger",
        "db_async_session",
    ]

    def __init__(self):
        self._initialized = False

    @cached_property
    def config(self) -> Config:
        return init_config()

    @cached_property
    def logger(self) -> Logger:
        return init_logger(
            level="DEBUG" if self.config.app_debug else "INFO",
            serialize=self.config.app_log_serialize,
            outdir=self.config.app_log_outdir,
        )

    @cached_property
    def db_async_session(self) -> sessionmaker:
        return init_db_async_session(
            db_drivername=self.config.db_drivername,
            db_database=self.config.db_database,
            db_username=self.config.db_username,
            db_password=self.config.db_password,
            db_host=self.config.db_host,
            db_port=self.config.db_port,
            db_charset=self.config.db_charset,
            db_echo=self.config.app_debug,
            is_create_tables=True,
        )

    def setup(self):
        with self._init_lock:
            if not self._initialized:
                for prop_name in self._init_properties:
                    if hasattr(self, prop_name):
                        getattr(self, prop_name)
                    else:
                        logger.warning(f"{prop_name} not found")
                
                tenant_db_pool.initialize_master(
                    db_drivername=self.config.db_drivername,
                    db_database=self.config.db_database,
                    db_username=self.config.db_username,
                    db_password=self.config.db_password,
                    db_host=self.config.db_host,
                    db_port=self.config.db_port,
                    db_charset=self.config.db_charset,
                    db_echo=self.config.app_debug,
                    db_pool_size=20,
                    db_max_overflow=10,
                    db_pool_recycle=3600,
                    slave_host=self.config.db_slave_host,
                    slave_port=self.config.db_slave_port,
                )
                
                self._initialized = True


g = G()
