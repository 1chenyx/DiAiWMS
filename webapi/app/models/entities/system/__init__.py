"""
系统模块实体
"""
from app.models.entities.system.tenant import Tenant
from app.models.entities.system.user import User
from app.models.entities.system.user_role import UserRole
from app.models.entities.system.menu import Menu
from app.models.entities.system.rolemenu import Rolemenu as RoleMenu
from app.models.entities.system.action_log import ActionLog
from app.models.entities.system.freightfee import Freightfee as FreightFee
from app.models.entities.system.print_solution import PrintSolution
from app.models.entities.system.tenant_ai_config import TenantAIConfig
from app.models.entities.system.tenant_ai_tool import TenantAITool
from app.models.entities.system.tenant_ai_skill import TenantAISkill
from app.models.entities.system.tenant_ai_rule import TenantAIRule

__all__ = [
    "Tenant",
    "User",
    "UserRole",
    "Menu",
    "RoleMenu",
    "ActionLog",
    "FreightFee",
    "PrintSolution",
    "TenantAIConfig",
    "TenantAITool",
    "TenantAISkill",
    "TenantAIRule",
]
