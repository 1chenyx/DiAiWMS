from typing import TypeVar, Generic, Type, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.base_repository import BaseRepository
from app.services.base_service import BaseService, TenantAwareService

RepositoryType = TypeVar("RepositoryType", bound=BaseRepository)
ServiceType = TypeVar("ServiceType", bound=BaseService)


class DependencyFactory(Generic[RepositoryType, ServiceType]):
    """
    依赖注入工厂
    
    用于创建Repository和Service实例
    """

    def __init__(
        self,
        repository_class: Type[RepositoryType],
        service_class: Type[ServiceType]
    ):
        """
        初始化依赖工厂
        
        Args:
            repository_class: Repository类
            service_class: Service类
        """
        self._repository_class = repository_class
        self._service_class = service_class

    def create_repository(self, db_session: AsyncSession) -> RepositoryType:
        """
        创建Repository实例
        
        Args:
            db_session: 数据库会话
            
        Returns:
            Repository实例
        """
        return self._repository_class(db_session)

    def create_service(self, db_session: AsyncSession) -> ServiceType:
        """
        创建Service实例
        
        Args:
            db_session: 数据库会话
            
        Returns:
            Service实例
        """
        repository = self.create_repository(db_session)
        return self._service_class(repository)


def get_repository(
    repository_class: Type[RepositoryType],
    db_session: AsyncSession
) -> RepositoryType:
    """
    获取Repository实例
    
    Args:
        repository_class: Repository类
        db_session: 数据库会话
        
    Returns:
        Repository实例
    """
    return repository_class(db_session)


def get_service(
    service_class: Type[ServiceType],
    db_session: AsyncSession
) -> ServiceType:
    """
    获取Service实例
    
    Args:
        service_class: Service类
        db_session: 数据库会话
        
    Returns:
        Service实例
    """
    return service_class(db_session)
