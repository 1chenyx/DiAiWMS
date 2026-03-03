from sqlalchemy import Column, String, Integer, BigInteger, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import WMSBaseModel


class OutboundReceiptItem(WMSBaseModel):
    """
    出库单明细实体类
    
    用于记录出库单的明细信息
    """
    __tablename__ = 'outbound_receipt_item'

    receipt_id = Column(Integer, ForeignKey('outbound_receipt.id'), nullable=False, comment='出库单ID')
    pick_putaway_item_id = Column(Integer, nullable=False, default=0, comment='拣货上架单明细ID')
    spu_id = Column(Integer, nullable=False, default=0, comment='SPU ID')
    sku_id = Column(Integer, ForeignKey('sku.id'), nullable=False, default=0, comment='SKU ID')
    qty = Column(Integer, nullable=False, default=0, comment='数量')
    actual_qty = Column(Integer, nullable=False, default=0, comment='实际数量')
    weight = Column(Numeric(precision=10, scale=2), nullable=False, default=0, comment='重量')
    actual_weight = Column(Numeric(precision=10, scale=2), nullable=False, default=0, comment='实际重量')
    volume = Column(Numeric(precision=10, scale=2), nullable=False, default=0, comment='体积')
    actual_volume = Column(Numeric(precision=10, scale=2), nullable=False, default=0, comment='实际体积')
    price = Column(Numeric(precision=10, scale=2), nullable=False, default=0, comment='价格')
    expiry_date = Column(BigInteger, nullable=False, default=0, comment='过期日期')
    goods_location_id = Column(Integer, nullable=False, default=0, comment='出库库位ID')
    series_number = Column(String(100), nullable=False, default='', comment='序列号')
    tenant_id = Column(String(36), nullable=False, default='', comment='租户ID')

    receipt = relationship("OutboundReceipt", back_populates="items")
    sku = relationship("Sku")
