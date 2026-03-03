from typing import Type, TypeVar, Callable, Optional
from functools import wraps
from fastapi import Depends

from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies import get_db_by_tenant
from app.services.base_service import BaseService

ServiceType = TypeVar("ServiceType", bound=BaseService)


def inject_service(service_class: Type[ServiceType]) -> Callable[[], ServiceType]:
    """
    依赖注入装饰器，用于自动注入Service实例
    
    Args:
        service_class: Service类
        
    Returns:
        依赖注入函数
    """
    def dependency(
        db: AsyncSession = Depends(get_db_by_tenant)
    ) -> ServiceType:
        """
        依赖注入函数
        
        Args:
            db: 数据库会话
            
        Returns:
            Service实例
        """
        return service_class(db)
    
    return dependency


def get_service_dependency(service_class: Type[ServiceType]):
    """
    获取Service依赖注入函数
    
    Args:
        service_class: Service类
        
    Returns:
        依赖注入函数
    """
    return inject_service(service_class)
