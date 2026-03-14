from app.repositories.base_repository import BaseRepository
from app.models.entities.system import TenantAIConfig


class TenantAIConfigRepository(BaseRepository[TenantAIConfig]):
    """
    租户AI配置仓储
    """
    
    def __init__(self, db_session):
        super().__init__(TenantAIConfig, db_session)
