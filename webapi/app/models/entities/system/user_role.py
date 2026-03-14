from datetime import datetime
from sqlalchemy import String, Boolean, BigInteger
from sqlalchemy.orm import mapped_column
from app.models.base import WMSBaseModel


class UserRole(WMSBaseModel):
    """
    用户角色实体类
    
    用于管理系统中的用户角色信息,包括角色名称、状态等
    """
    __tablename__ = "userrole"

    role_name = mapped_column(String(50), nullable=False, default="", comment="角色名称")
    is_valid = mapped_column(Boolean, nullable=False, default=False, comment="是否有效")
    create_time = mapped_column(BigInteger, nullable=False, default=lambda: int(datetime.now().timestamp()), comment="创建时间")
    last_update_time = mapped_column(BigInteger, nullable=False, default=lambda: int(datetime.now().timestamp()), comment="最后更新时间")
    tenant_id = mapped_column(String(36), nullable=False, default="", comment="租户ID")
