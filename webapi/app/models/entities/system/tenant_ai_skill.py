from datetime import datetime
from sqlalchemy import String, Boolean, BigInteger, Text
from sqlalchemy.orm import mapped_column
from app.models.base import WMSBaseModel


class TenantAISkill(WMSBaseModel):
    """
    租户AI技能配置实体类
    
    用于存储租户自定义的技能配置信息
    """
    __tablename__ = "tenant_ai_skill"

    tenant_id = mapped_column(String(36), nullable=False, default="", comment="租户ID")
    skill_name = mapped_column(String(100), nullable=False, default="", comment="技能名称")
    skill_type = mapped_column(String(50), nullable=False, default="", comment="技能类型")
    description = mapped_column(String(500), nullable=False, default="", comment="技能描述")
    config = mapped_column(Text, nullable=False, default="{}", comment="技能配置(JSON)")
    is_active = mapped_column(Boolean, nullable=False, default=True, comment="是否激活")
    is_valid = mapped_column(Boolean, nullable=False, default=True, comment="是否有效")
    creator = mapped_column(String(50), nullable=False, default="", comment="创建人")
    create_time = mapped_column(BigInteger, nullable=False, default=lambda: int(datetime.now().timestamp()), comment="创建时间")
    last_update_time = mapped_column(BigInteger, nullable=False, default=lambda: int(datetime.now().timestamp()), comment="最后更新时间")
