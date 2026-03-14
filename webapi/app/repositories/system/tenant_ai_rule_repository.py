from app.repositories.base_repository import BaseRepository
from app.models.entities.system import TenantAIRule


class TenantAIRuleRepository(BaseRepository[TenantAIRule]):
    """
    租户AI规则配置仓储
    """
    
    def __init__(self, db_session):
        super().__init__(TenantAIRule, db_session)
