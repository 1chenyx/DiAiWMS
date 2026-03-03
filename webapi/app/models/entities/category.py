from datetime import datetime
from sqlalchemy import String, Boolean, BigInteger
from sqlalchemy.orm import mapped_column
from app.models.base import WMSBaseModel


class Category(WMSBaseModel):
    """
    商品分类实体类
    
    用于管理商品分类信息,支持多级分类结构
    """
    __tablename__ = "category"

    category_name = mapped_column(String(100), nullable=False, default="", comment="分类名称")
    parent_id = mapped_column(BigInteger, nullable=False, default=0, comment="父分类ID")
    creator = mapped_column(String(50), nullable=False, default="", comment="创建人")
    create_time = mapped_column(BigInteger, nullable=False, default=lambda: int(datetime.now().timestamp()), comment="创建时间")
    last_update_time = mapped_column(BigInteger, nullable=False, default=lambda: int(datetime.now().timestamp()), comment="最后更新时间")
    is_valid = mapped_column(Boolean, nullable=False, default=True, comment="是否有效")
    tenant_id = mapped_column(String(36), nullable=False, default="", comment="租户ID")
