from app.repositories.base_repository import BaseRepository
from app.models.entities.system import TenantAITool


class TenantAIToolRepository(BaseRepository[TenantAITool]):
    """
    租户AI工具配置仓储
    """
    
    def __init__(self, db_session):
        super().__init__(TenantAITool, db_session)
