from datetime import datetime
from sqlalchemy import String, Boolean, BigInteger, Integer
from sqlalchemy.orm import mapped_column
from app.models.base import WMSBaseModel


class Tenant(WMSBaseModel):
    """
    租户实体类
    
    用于存储多租户系统中的租户信息,包括租户名称、联系方式、数据库配置等
    """
    __tablename__ = "tenant"

    id = mapped_column(String(36), primary_key=True, nullable=False, default="", comment="主键ID(UUID)")
    tenant_name = mapped_column(String(100), nullable=False, default="", comment="租户名称")
    tenant_code = mapped_column(String(50), nullable=False, default="", unique=True, comment="租户编码")
    contact_person = mapped_column(String(50), nullable=False, default="", comment="联系人")
    contact_phone = mapped_column(String(20), nullable=False, default="", comment="联系电话")
    contact_email = mapped_column(String(100), nullable=False, default="", comment="联系邮箱")
    address = mapped_column(String(256), nullable=False, default="", comment="地址")
    description = mapped_column(String(500), nullable=False, default="", comment="描述")
    db_drivername = mapped_column(String(50), nullable=False, default="postgresql+asyncpg", comment="数据库驱动类型")
    db_database = mapped_column(String(100), nullable=False, default="", comment="数据库名称")
    db_username = mapped_column(String(100), nullable=False, default="", comment="数据库用户名")
    db_password = mapped_column(String(100), nullable=False, default="", comment="数据库密码")
    db_host = mapped_column(String(100), nullable=False, default="localhost", comment="数据库主机")
    db_port = mapped_column(Integer, nullable=False, default=5432, comment="数据库端口")
    db_charset = mapped_column(String(20), nullable=False, default="utf8", comment="数据库字符集")
    db_pool_size = mapped_column(Integer, nullable=False, default=10, comment="连接池大小")
    db_max_overflow = mapped_column(Integer, nullable=False, default=5, comment="连接池最大溢出数")
    db_pool_recycle = mapped_column(Integer, nullable=False, default=3600, comment="连接回收时间(秒)")
    slave_host = mapped_column(String(100), nullable=True, default=None, comment="从库主机(可选)")
    slave_port = mapped_column(Integer, nullable=True, default=None, comment="从库端口(可选)")
    is_valid = mapped_column(Boolean, nullable=False, default=True, comment="是否有效")
    creator = mapped_column(String(50), nullable=False, default="", comment="创建人")
    create_time = mapped_column(BigInteger, nullable=False, default=lambda: int(datetime.now().timestamp()), comment="创建时间")
    last_update_time = mapped_column(BigInteger, nullable=False, default=lambda: int(datetime.now().timestamp()), comment="最后更新时间")
