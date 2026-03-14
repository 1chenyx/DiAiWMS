from datetime import datetime
from sqlalchemy import String, Boolean, BigInteger, SmallInteger
from sqlalchemy.orm import mapped_column
from app.models.base import WMSBaseModel


class WarehouseArea(WMSBaseModel):
    """
    仓库区域实体类
    
    用于管理仓库的区域划分,支持多级区域结构
    """
    __tablename__ = "warehousearea"

    warehouse_id = mapped_column(BigInteger, nullable=False, default=0, comment="仓库ID")
    area_name = mapped_column(String(100), nullable=False, default="", comment="区域名称")
    parent_id = mapped_column(BigInteger, nullable=False, default=0, comment="父区域ID")
    create_time = mapped_column(BigInteger, nullable=False, default=lambda: int(datetime.now().timestamp()), comment="创建时间")
    last_update_time = mapped_column(BigInteger, nullable=False, default=lambda: int(datetime.now().timestamp()), comment="最后更新时间")
    is_valid = mapped_column(Boolean, nullable=False, default=False, comment="是否有效")
    tenant_id = mapped_column(String(36), nullable=False, default="", comment="租户ID")
    area_property = mapped_column(SmallInteger, nullable=False, default=0, comment="区域属性")
