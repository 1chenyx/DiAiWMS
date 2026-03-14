from datetime import datetime
from sqlalchemy import Column, Integer, String, BigInteger
from app.models.base import WMSBaseModel


class ActionLog(WMSBaseModel):
    """
    操作日志实体类
    
    用于记录用户在前端系统的操作行为,包括访问路径、操作内容、操作时间等信息
    """
    __tablename__ = "action_log"

    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键ID')
    vue_path = Column(String(255), nullable=False, default='', comment='Vue路径')
    user_name = Column(String(64), nullable=False, default='', comment='用户名')
    action_content = Column(String(1000), nullable=False, default='', comment='操作内容')
    action_time = Column(BigInteger, nullable=False, default=lambda: int(datetime.now().timestamp()), comment='操作时间')
    tenant_id = Column(String(36), nullable=False, default='', comment='租户ID')
