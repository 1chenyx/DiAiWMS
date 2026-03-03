from sqlalchemy import Column, String, Integer, Boolean, BigInteger
from sqlalchemy.orm import relationship
from app.models.base import WMSBaseModel


class Stockprocess(WMSBaseModel):
    """
    库存加工实体类
    
    用于记录库存加工作业,包括加工类型、状态、加工人等信息
    """
    __tablename__ = 'stockprocess'

    job_code = Column(String(64), nullable=False, default='', comment='作业编号')
    job_type = Column(Boolean, nullable=False, default=False, comment='作业类型')
    process_status = Column(Boolean, nullable=False, default=False, comment='加工状态')
    processor = Column(String(64), nullable=False, default='', comment='加工人')
    process_time = Column(BigInteger, nullable=False, default=0, comment='加工时间')
    creator = Column(String(64), nullable=False, default='', comment='创建人')
    create_time = Column(BigInteger, nullable=False, default=0, comment='创建时间')
    last_update_time = Column(BigInteger, nullable=False, default=0, comment='最后更新时间')
    tenant_id = Column(String(36), nullable=False, default='', comment='租户ID')

    detail_list = relationship("Stockprocessdetail", back_populates="stockprocess", cascade="all, delete-orphan")
