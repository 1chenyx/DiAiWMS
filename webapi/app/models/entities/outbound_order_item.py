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
    spu_code = Column(String(64), nullable=False, default='', comment='SPU编码')
    spu_name = Column(String(128), nullable=False, default='', comment='SPU名称')
    sku_id = Column(Integer, ForeignKey('sku.id'), nullable=False, default=0, comment='SKU ID')
    sku_code = Column(String(64), nullable=False, default='', comment='SKU编码')
    sku_name = Column(String(128), nullable=False, default='', comment='SKU名称')
    qty = Column(Integer, nullable=False, default=0, comment='数量')
    weight = Column(Numeric(precision=10, scale=2), nullable=False, default=0, comment='重量')
    volume = Column(Numeric(precision=10, scale=2), nullable=False, default=0, comment='体积')
    price = Column(Numeric(precision=10, scale=2), nullable=False, default=0, comment='价格')
    expiry_date = Column(BigInteger, nullable=False, default=0, comment='过期日期')
    batch_no = Column(String(64), nullable=False, default='', comment='批次号')
    production_date = Column(BigInteger, nullable=False, default=0, comment='生产日期')
    goods_location_id = Column(Integer, nullable=False, default=0, comment='指定库位ID')
    goods_location_code = Column(String(64), nullable=False, default='', comment='库位编码')
    tenant_id = Column(String(36), nullable=False, default='', comment='租户ID')

    order = relationship("OutboundOrder", back_populates="items")
    sku = relationship("Sku")
