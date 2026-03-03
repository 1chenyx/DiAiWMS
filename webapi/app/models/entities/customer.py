from sqlalchemy import Column, String, Boolean, BigInteger
from app.models.base import WMSBaseModel


class Customer(WMSBaseModel):
    """
    客户实体类
    
    用于存储客户的基本信息,包括客户名称、地址、联系方式等
    """
    __tablename__ = 'customer'

    customer_name = Column(String(128), nullable=False, default='', comment='客户名称')
    city = Column(String(128), nullable=False, default='', comment='城市')
    address = Column(String(256), nullable=False, default='', comment='地址')
    email = Column(String(128), nullable=False, default='', comment='邮箱')
    manager = Column(String(64), nullable=False, default='', comment='管理员')
    contact_tel = Column(String(64), nullable=False, default='', comment='联系电话')
    creator = Column(String(64), nullable=False, default='', comment='创建人')
    create_time = Column(BigInteger, nullable=False, default=0, comment='创建时间')
    last_update_time = Column(BigInteger, nullable=False, default=0, comment='最后更新时间')
    is_valid = Column(Boolean, nullable=False, default=True, comment='是否有效')
    tenant_id = Column(String(36), nullable=False, default='', comment='租户ID')
