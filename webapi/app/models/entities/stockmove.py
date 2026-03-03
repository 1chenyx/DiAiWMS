from sqlalchemy import Column, String, Integer, Boolean, BigInteger, Numeric
from app.models.base import WMSBaseModel


class Stockmove(WMSBaseModel):
    """
    库存移动实体类
    
    用于记录库存移动作业,包括原货位、目标货位、移动数量、处理人等信息
    """
    __tablename__ = 'stockmove'

    job_code = Column(String(64), nullable=False, default='', comment='作业编号')
    move_status = Column(Integer, nullable=False, default=0, comment='移动状态')
    sku_id = Column(Integer, nullable=False, default=0, comment='SKU ID')
    orig_goods_location_id = Column(Integer, nullable=False, default=0, comment='原货位ID')
    dest_googs_location_id = Column(Integer, nullable=False, default=0, comment='目标货位ID')
    qty = Column(Integer, nullable=False, default=0, comment='数量')
    goods_owner_id = Column(Integer, nullable=False, default=0, comment='货主ID')
    handler = Column(String(64), nullable=False, default='', comment='处理人')
    handle_time = Column(BigInteger, nullable=False, default=0, comment='处理时间')
    creator = Column(String(64), nullable=False, default='', comment='创建人')
    create_time = Column(BigInteger, nullable=False, default=0, comment='创建时间')
    last_update_time = Column(BigInteger, nullable=False, default=0, comment='最后更新时间')
    tenant_id = Column(String(36), nullable=False, default='', comment='租户ID')
    series_number = Column(String(100), nullable=False, default='', comment='序列号')
    expiry_date = Column(BigInteger, nullable=False, default=0, comment='过期日期')
    price = Column(Numeric(precision=10, scale=2), nullable=False, default=0, comment='价格')
    putaway_date = Column(BigInteger, nullable=False, default=0, comment='上架日期')
