from datetime import datetime
from sqlalchemy import String, Boolean, BigInteger, Text, Integer
from sqlalchemy.orm import mapped_column
from app.models.base import WMSBaseModel


class TenantAIRule(WMSBaseModel):
    """
    租户AI规则配置实体类
    
    用于存储租户自定义的规则配置信息
    """
    __tablename__ = "tenant_ai_rule"

    tenant_id = mapped_column(String(36), nullable=False, default="", comment="租户ID")
    rule_name = mapped_column(String(100), nullable=False, default="", comment="规则名称")
    rule_category = mapped_column(String(50), nullable=False, default="", comment="规则类别")
    priority = mapped_column(Integer, nullable=False, default=0, comment="优先级(数字越大优先级越高)")
    content = mapped_column(Text, nullable=False, default="", comment="规则内容")
    description = mapped_column(String(500), nullable=False, default="", comment="规则描述")
    is_active = mapped_column(Boolean, nullable=False, default=True, comment="是否激活")
    is_system = mapped_column(Boolean, nullable=False, default=False, comment="是否系统规则")
    is_valid = mapped_column(Boolean, nullable=False, default=True, comment="是否有效")
    creator = mapped_column(String(50), nullable=False, default="", comment="创建人")
    create_time = mapped_column(BigInteger, nullable=False, default=lambda: int(datetime.now().timestamp()), comment="创建时间")
    last_update_time = mapped_column(BigInteger, nullable=False, default=lambda: int(datetime.now().timestamp()), comment="最后更新时间")
