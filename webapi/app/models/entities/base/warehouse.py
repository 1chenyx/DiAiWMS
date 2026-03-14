from datetime import datetime
from sqlalchemy import String, Boolean, BigInteger
from sqlalchemy.orm import mapped_column
from app.models.base import WMSBaseModel


class Warehouse(WMSBaseModel):
    """
    仓库实体类
    
    用于存储仓库的基本信息,包括仓库名称、位置、联系方式、管理员等
    """
    __tablename__ = "warehouse"

    warehouse_name = mapped_column(String(100), nullable=False, default="", comment="仓库名称")
    city = mapped_column(String(50), nullable=False, default="", comment="城市")
    address = mapped_column(String(200), nullable=False, default="", comment="地址")
    email = mapped_column(String(100), nullable=False, default="", comment="邮箱")
    manager = mapped_column(String(50), nullable=False, default="", comment="管理员")
    contact_tel = mapped_column(String(20), nullable=False, default="", comment="联系电话")
    creator = mapped_column(String(50), nullable=False, default="", comment="创建人")
    create_time = mapped_column(BigInteger, nullable=False, default=lambda: int(datetime.now().timestamp()), comment="创建时间")
    last_update_time = mapped_column(BigInteger, nullable=False, default=lambda: int(datetime.now().timestamp()), comment="最后更新时间")
    is_valid = mapped_column(Boolean, nullable=False, default=False, comment="是否有效")
    tenant_id = mapped_column(String(36), nullable=False, default="", comment="租户ID")
