from datetime import datetime
from sqlalchemy import String, Boolean, BigInteger, Text
from sqlalchemy.orm import mapped_column
from app.models.base import WMSBaseModel


class TenantAITool(WMSBaseModel):
    """
    租户AI工具配置实体类
    
    用于存储租户激活的工具配置信息
    """
    __tablename__ = "tenant_ai_tool"

    tenant_id = mapped_column(String(36), nullable=False, default="", comment="租户ID")
    tool_code = mapped_column(String(100), nullable=False, default="", comment="工具代码")
    tool_name = mapped_column(String(100), nullable=False, default="", comment="工具名称")
    tool_category = mapped_column(String(50), nullable=False, default="", comment="工具分类")
    is_active = mapped_column(Boolean, nullable=False, default=True, comment="是否激活")
    config = mapped_column(Text, nullable=False, default="{}", comment="工具配置(JSON)")
    description = mapped_column(String(500), nullable=False, default="", comment="工具描述")
    is_valid = mapped_column(Boolean, nullable=False, default=True, comment="是否有效")
    creator = mapped_column(String(50), nullable=False, default="", comment="创建人")
    create_time = mapped_column(BigInteger, nullable=False, default=lambda: int(datetime.now().timestamp()), comment="创建时间")
    last_update_time = mapped_column(BigInteger, nullable=False, default=lambda: int(datetime.now().timestamp()), comment="最后更新时间")
