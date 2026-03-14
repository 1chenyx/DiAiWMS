from sqlalchemy import Column, String, Integer, BigInteger
from app.models.base import WMSBaseModel


class Rolemenu(WMSBaseModel):
    """
    角色菜单关联实体类
    
    用于管理用户角色与菜单的关联关系,包括权限分配等
    """
    __tablename__ = 'rolemenu'

    userrole_id = Column(Integer, nullable=False, default=0, comment='用户角色ID')
    menu_id = Column(Integer, nullable=False, default=0, comment='菜单ID')
    authority = Column(Integer, nullable=False, default=1, comment='权限')
    create_time = Column(BigInteger, nullable=False, default=0, comment='创建时间')
    last_update_time = Column(BigInteger, nullable=False, default=0, comment='最后更新时间')
    tenant_id = Column(String(36), nullable=False, default='', comment='租户ID')
    menu_actions_authority = Column(String(1000), nullable=False, default='[]', comment='菜单操作权限')
