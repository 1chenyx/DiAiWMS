from sqlalchemy import Column, String, Integer, BigInteger, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import WMSBaseModel


class InboundOrderItem(WMSBaseModel):
    """
    入库订单明细实体类
    
    用于记录入库订单的明细信息
    """
    __tablename__ = 'inbound_order_item'

    order_id = Column(Integer, ForeignKey('inbound_order.id'), nullable=False, comment='入库订单ID')
    spu_id = Column(Integer, nullable=False, default=0, comment='SPU ID')
    sku_id = Column(Integer, ForeignKey('sku.id'), nullable=False, default=0, comment='SKU ID')
    qty = Column(Integer, nullable=False, default=0, comment='数量')
    weight = Column(Numeric(precision=10, scale=2), nullable=False, default=0, comment='重量')
    volume = Column(Numeric(precision=10, scale=2), nullable=False, default=0, comment='体积')
    price = Column(Numeric(precision=10, scale=2), nullable=False, default=0, comment='价格')
    expiry_date = Column(BigInteger, nullable=False, default=0, comment='过期日期')
    tenant_id = Column(String(36), nullable=False, default='', comment='租户ID')

    order = relationship("InboundOrder", back_populates="items")
    sku = relationship("Sku")
