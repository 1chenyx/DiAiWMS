from sqlalchemy import Column, String, Integer, Boolean, BigInteger, Numeric
from app.models.base import WMSBaseModel


class Stocktaking(WMSBaseModel):
    """
    库存盘点实体类
    
    用于记录库存盘点作业,包括账面数量、盘点数量、差异数量等信息
    """
    __tablename__ = 'stocktaking'

    job_code = Column(String(64), nullable=False, default='', comment='作业编号')
    job_status = Column(Boolean, nullable=False, default=False, comment='作业状态')
    sku_id = Column(Integer, nullable=False, default=0, comment='SKU ID')
    goods_owner_id = Column(Integer, nullable=False, default=0, comment='货主ID')
    goods_location_id = Column(Integer, nullable=False, default=0, comment='货位ID')
    series_number = Column(String(100), nullable=False, default='', comment='序列号')
    expiry_date = Column(BigInteger, nullable=False, default=0, comment='过期日期')
    price = Column(Numeric(precision=10, scale=2), nullable=False, default=0, comment='价格')
    putaway_date = Column(BigInteger, nullable=False, default=0, comment='上架日期')
    book_qty = Column(Integer, nullable=False, default=0, comment='账面数量')
    counted_qty = Column(Integer, nullable=False, default=0, comment='盘点数量')
    difference_qty = Column(Integer, nullable=False, default=0, comment='差异数量')
    creator = Column(String(64), nullable=False, default='', comment='创建人')
    create_time = Column(BigInteger, nullable=False, default=0, comment='创建时间')
    last_update_time = Column(BigInteger, nullable=False, default=0, comment='最后更新时间')
    tenant_id = Column(String(36), nullable=False, default='', comment='租户ID')
    handler = Column(String(64), nullable=False, default='', comment='处理人')
    handle_time = Column(BigInteger, nullable=False, default=0, comment='处理时间')
