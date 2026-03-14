from sqlalchemy import Column, String, Integer, Boolean, BigInteger, Numeric
from app.models.base import WMSBaseModel


class Stockadjust(WMSBaseModel):
    """
    库存调整实体类
    
    用于记录库存调整作业,包括调整数量、类型、原因等信息
    """
    __tablename__ = 'stockadjust'

    job_code = Column(String(64), nullable=False, default='', comment='作业编号')
    sku_id = Column(Integer, nullable=False, default=0, comment='SKU ID')
    goods_owner_id = Column(Integer, nullable=False, default=0, comment='货主ID')
    goods_location_id = Column(Integer, nullable=False, default=0, comment='货位ID')
    qty = Column(Integer, nullable=False, default=0, comment='数量')
    creator = Column(String(64), nullable=False, default='', comment='创建人')
    create_time = Column(BigInteger, nullable=False, default=0, comment='创建时间')
    last_update_time = Column(BigInteger, nullable=False, default=0, comment='最后更新时间')
    tenant_id = Column(String(36), nullable=False, default='', comment='租户ID')
    is_update_stock = Column(Boolean, nullable=False, default=False, comment='是否更新库存')
    job_type = Column(Integer, nullable=False, default=0, comment='作业类型')
    source_table_id = Column(Integer, nullable=False, default=0, comment='来源表ID')
    series_number = Column(String(100), nullable=False, default='', comment='序列号')
    expiry_date = Column(BigInteger, nullable=False, default=0, comment='过期日期')
    price = Column(Numeric(precision=10, scale=2), nullable=False, default=0, comment='价格')
    putaway_date = Column(BigInteger, nullable=False, default=0, comment='上架日期')
