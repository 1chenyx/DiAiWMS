"""
@author axiner
@version v1.0.0
@created 2024/07/29 22:22
@abstract 主入口
@description FastAPI应用程序主入口文件,负责应用初始化和路由注册
@history
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from loguru import logger

import sys

from app import (
    api,
    middleware,
)
from app.initializer import g

# 配置loguru输出到stderr
logger.remove()
logger.add(sys.stderr, format="{time:YYYY-MM-DD HH:mm:ss.SSS} {level} {name}:{line} {message}", level="INFO")

g.setup()
# 配置API文档URL
openapi_url = "/openapi.json"
docs_url = "/docs"
redoc_url = "/redoc"
if g.config.app_disable_docs is True:
    openapi_url, docs_url, redoc_url = None, None, None


@asynccontextmanager
async def lifespan(xapp: FastAPI):
    """
    应用生命周期管理
    
    Args:
        xapp: FastAPI应用实例
    """
    logger.info(f"Application env '{g.config.app_env}'")
    logger.info(f"Application yaml '{g.config.yaml_path.name}'")
    logger.info(f"Application title '{g.config.app_title}'")
    logger.info(f"Application version '{g.config.app_version}'")
    
    # 初始化Redis连接
    from app.utils.cache_manager import CacheManager
    try:
        logger.info("Initializing Redis connection...")
        cache_manager = CacheManager()
        if cache_manager._redis_client:
            logger.info(f"Redis connection initialized successfully: {cache_manager._config.redis_host}:{cache_manager._config.redis_port}")
        else:
            logger.warning("Redis connection failed, using in-memory cache")
    except Exception as e:
        logger.error(f"Failed to initialize CacheManager: {e}", exc_info=True)
    
    # AI工具初始化已移除，等待重新实现
    
    # 应用启动
    logger.info("Application server running")
    yield
    # 应用关闭
    logger.info("Application server shutdown")


app = FastAPI(
    title=g.config.app_title,
    summary=g.config.app_summary,
    description=g.config.app_description,
    version=g.config.app_version,
    debug=g.config.app_debug,
    openapi_url=openapi_url,
    docs_url=docs_url,
    redoc_url=redoc_url,
    lifespan=lifespan,
    default_response_class=ORJSONResponse,
)
# 注册中间件和路由
middleware.register_middlewares(app)
api.register_routers(app)
