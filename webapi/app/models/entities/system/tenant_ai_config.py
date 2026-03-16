from datetime import datetime
from sqlalchemy import String, Boolean, BigInteger, Float
from sqlalchemy.orm import mapped_column
from app.models.base import WMSBaseModel


class TenantAIConfig(WMSBaseModel):
    """
    租户AI配置实体类
    
    用于存储租户的LLM配置信息,包括服务商、模型、API密钥等
    """
    __tablename__ = "tenant_ai_config"

    tenant_id = mapped_column(String(36), nullable=False, default="", comment="租户ID")
    provider_code = mapped_column(String(50), nullable=False, default="", comment="服务商代码")
    model_code = mapped_column(String(100), nullable=False, default="", comment="模型代码")
    api_key = mapped_column(String(500), nullable=False, default="", comment="API密钥")
    api_endpoint = mapped_column(String(256), nullable=True, default=None, comment="API端点")
    is_default = mapped_column(Boolean, nullable=False, default=False, comment="是否默认配置")
    temperature = mapped_column(Float, nullable=True, default=0.7, comment="温度参数")
    max_tokens = mapped_column(BigInteger, nullable=True, default=2000, comment="最大token数")
    is_valid = mapped_column(Boolean, nullable=False, default=True, comment="是否有效")
    creator = mapped_column(String(50), nullable=False, default="", comment="创建人")
    create_time = mapped_column(BigInteger, nullable=False, default=lambda: int(datetime.now().timestamp()), comment="创建时间")
    last_update_time = mapped_column(BigInteger, nullable=False, default=lambda: int(datetime.now().timestamp()), comment="最后更新时间")
