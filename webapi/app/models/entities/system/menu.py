from sqlalchemy import Column, String, Integer, BigInteger
from app.models.base import WMSBaseModel


class Menu(WMSBaseModel):
    """
    菜单实体类
    
    用于管理系统的菜单结构,包括菜单名称、路径、排序等信息
    """
    __tablename__ = 'menu'

    menu_name = Column(String(128), nullable=False, default='', comment='菜单名称')
    module = Column(String(128), nullable=False, default='', comment='模块')
    vue_path = Column(String(256), nullable=False, default='', comment='Vue路径')
    vue_path_detail = Column(String(256), nullable=False, default='', comment='Vue详细路径')
    vue_directory = Column(String(256), nullable=False, default='', comment='Vue目录')
    sort = Column(Integer, nullable=False, default=0, comment='排序')
    tenant_id = Column(String(36), nullable=False, default='', comment='租户ID')
    menu_actions = Column(String(1000), nullable=False, default='[]', comment='菜单操作')
