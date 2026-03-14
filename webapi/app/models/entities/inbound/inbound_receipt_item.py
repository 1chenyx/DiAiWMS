from sqlalchemy import Column, String, Integer, BigInteger, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import WMSBaseModel


class InboundReceiptItem(WMSBaseModel):
    """
    入库单明细实体类
    
    用于记录入库单的明细信息
    """
    __tablename__ = 'inbound_receipt_item'

    receipt_id = Column(Integer, ForeignKey('inbound_receipt.id'), nullable=False, comment='入库单ID')
    pick_putaway_item_id = Column(Integer, nullable=False, default=0, comment='拣货上架单明细ID')
    spu_id = Column(Integer, nullable=False, default=0, comment='SPU ID')
    spu_code = Column(String(64), nullable=False, default='', comment='SPU编码')
    spu_name = Column(String(128), nullable=False, default='', comment='SPU名称')
    sku_id = Column(Integer, ForeignKey('sku.id'), nullable=False, default=0, comment='SKU ID')
    sku_code = Column(String(64), nullable=False, default='', comment='SKU编码')
    sku_name = Column(String(128), nullable=False, default='', comment='SKU名称')
    qty = Column(Integer, nullable=False, default=0, comment='数量')
    actual_qty = Column(Integer, nullable=False, default=0, comment='实际数量')
    weight = Column(Numeric(precision=10, scale=2), nullable=False, default=0, comment='重量')
    actual_weight = Column(Numeric(precision=10, scale=2), nullable=False, default=0, comment='实际重量')
    volume = Column(Numeric(precision=10, scale=2), nullable=False, default=0, comment='体积')
    actual_volume = Column(Numeric(precision=10, scale=2), nullable=False, default=0, comment='实际体积')
    price = Column(Numeric(precision=10, scale=2), nullable=False, default=0, comment='价格')
    expiry_date = Column(BigInteger, nullable=False, default=0, comment='过期日期')
    batch_no = Column(String(64), nullable=False, default='', comment='批次号')
    production_date = Column(BigInteger, nullable=False, default=0, comment='生产日期')
    goods_location_id = Column(Integer, nullable=False, default=0, comment='入库库位ID')
    warehouse_id = Column(Integer, nullable=False, default=0, comment='仓库ID')
    warehouse_name = Column(String(100), nullable=False, default='', comment='仓库名称')
    warehouse_area_id = Column(Integer, nullable=False, default=0, comment='库区ID')
    warehouse_area_name = Column(String(100), nullable=False, default='', comment='库区名称')
    warehouse_location_name = Column(String(100), nullable=False, default='', comment='库位名称')
    series_number = Column(String(100), nullable=False, default='', comment='序列号')
    tenant_id = Column(String(36), nullable=False, default='', comment='租户ID')

    receipt = relationship("InboundReceipt", back_populates="items")
    sku = relationship("Sku")
