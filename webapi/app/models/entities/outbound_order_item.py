from sqlalchemy import Column, String, Integer, BigInteger, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import WMSBaseModel


class OutboundOrderItem(WMSBaseModel):
    """
    出库订单明细实体类
    
    用于记录出库订单的明细信息
    """
    __tablename__ = 'outbound_order_item'

    order_id = Column(Integer, ForeignKey('outbound_order.id'), nullable=False, comment='出库订单ID')
    spu_id = Column(Integer, nullable=False, default=0, comment='SPU ID')
    sku_id = Column(Integer, ForeignKey('sku.id'), nullable=False, default=0, comment='SKU ID')
    qty = Column(Integer, nullable=False, default=0, comment='数量')
    weight = Column(Numeric(precision=10, scale=2), nullable=False, default=0, comment='重量')
    volume = Column(Numeric(precision=10, scale=2), nullable=False, default=0, comment='体积')
    price = Column(Numeric(precision=10, scale=2), nullable=False, default=0, comment='价格')
    expiry_date = Column(BigInteger, nullable=False, default=0, comment='过期日期')
    goods_location_id = Column(Integer, nullable=False, default=0, comment='指定库位ID')
    tenant_id = Column(String(36), nullable=False, default='', comment='租户ID')

    order = relationship("OutboundOrder", back_populates="items")
    sku = relationship("Sku")
