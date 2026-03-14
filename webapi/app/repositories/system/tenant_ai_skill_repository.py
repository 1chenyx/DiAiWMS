from app.repositories.base_repository import BaseRepository
from app.models.entities.system import TenantAISkill


class TenantAISkillRepository(BaseRepository[TenantAISkill]):
    """
    租户AI技能配置仓储
    """
    
    def __init__(self, db_session):
        super().__init__(TenantAISkill, db_session)
