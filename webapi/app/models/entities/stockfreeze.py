from sqlalchemy import Column, String, Integer, Boolean, BigInteger
from app.models.base import WMSBaseModel


class Stockfreeze(WMSBaseModel):
    """
    库存冻结实体类
    
    用于记录库存冻结和解冻作业,包括冻结类型、处理人、处理时间等
    """
    __tablename__ = 'stockfreeze'

    job_code = Column(String(64), nullable=False, default='', comment='作业编号')
    job_type = Column(Boolean, nullable=False, default=False, comment='作业类型')
    sku_id = Column(Integer, nullable=False, default=0, comment='SKU ID')
    goods_owner_id = Column(Integer, nullable=False, default=0, comment='货主ID')
    goods_location_id = Column(Integer, nullable=False, default=0, comment='货位ID')
    handler = Column(String(64), nullable=False, default='', comment='处理人')
    handle_time = Column(BigInteger, nullable=False, default=0, comment='处理时间')
    last_update_time = Column(BigInteger, nullable=False, default=0, comment='最后更新时间')
    tenant_id = Column(String(36), nullable=False, default='', comment='租户ID')
    series_number = Column(String(100), nullable=False, default='', comment='序列号')
