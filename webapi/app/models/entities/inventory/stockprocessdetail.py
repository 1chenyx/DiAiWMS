from sqlalchemy import Column, String, Integer, Boolean, BigInteger, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import WMSBaseModel


class Stockprocessdetail(WMSBaseModel):
    """
    库存加工明细实体类
    
    用于记录库存加工作业的明细信息,包括SKU、数量、货位等
    """
    __tablename__ = 'stockprocessdetail'

    stock_process_id = Column(Integer, ForeignKey('stockprocess.id'), nullable=False, default=0, comment='库存加工ID')
    sku_id = Column(Integer, nullable=False, default=0, comment='SKU ID')
    goods_owner_id = Column(Integer, nullable=False, default=0, comment='货主ID')
    goods_location_id = Column(Integer, nullable=False, default=0, comment='货位ID')
    qty = Column(Integer, nullable=False, default=0, comment='数量')
    last_update_time = Column(BigInteger, nullable=False, default=0, comment='最后更新时间')
    tenant_id = Column(String(36), nullable=False, default='', comment='租户ID')
    is_source = Column(Boolean, nullable=False, default=False, comment='是否来源')
    is_update_stock = Column(Boolean, nullable=False, default=False, comment='是否更新库存')
    series_number = Column(String(100), nullable=False, default='', comment='序列号')
    expiry_date = Column(BigInteger, nullable=False, default=0, comment='过期日期')
    price = Column(Numeric(precision=10, scale=2), nullable=False, default=0, comment='价格')
    putaway_date = Column(BigInteger, nullable=False, default=0, comment='上架日期')

    stockprocess = relationship("Stockprocess", back_populates="detail_list")
