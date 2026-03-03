from sqlalchemy import String, Integer, Boolean, BigInteger, Text
from sqlalchemy.orm import mapped_column
from app.models.base import WMSBaseModel


class TenantAIConfig(WMSBaseModel):
    """
    租户AI配置表
    
    存储租户的AI使用配置，包括API密钥和默认模型选择
    """
    __tablename__ = "tenant_ai_config"
    
    provider_code = mapped_column(String(32), nullable=False, comment="提供商代码")
    model_code = mapped_column(String(64), nullable=False, comment="模型代码")
    api_key = mapped_column(String(512), nullable=False, comment="API密钥")
    api_endpoint = mapped_column(String(512), nullable=True, comment="API端点URL")
    is_default = mapped_column(Boolean, default=False, comment="是否为默认配置")
    tenant_id = mapped_column(String(36), nullable=False, comment="租户ID")
    creator = mapped_column(String(64), nullable=True, comment="创建人")
    create_time = mapped_column(BigInteger, nullable=False, comment="创建时间")
    last_update_time = mapped_column(BigInteger, nullable=False, comment="最后更新时间")
    is_valid = mapped_column(Boolean, default=True, comment="是否有效")
