from sqlalchemy import Column, String, Integer, BigInteger, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import WMSBaseModel


class OutboundPickPutawayItem(WMSBaseModel):
    """
    出库拣货上架单明细实体类
    
    用于记录拣货上架单的明细信息，包含拣货详情
    """
    __tablename__ = 'outbound_pick_putaway_item'

    pick_putaway_id = Column(Integer, ForeignKey('outbound_pick_putaway.id'), nullable=False, comment='拣货上架单ID')
    order_item_id = Column(Integer, nullable=False, default=0, comment='出库订单明细ID')
    spu_id = Column(Integer, nullable=False, default=0, comment='SPU ID')
    sku_id = Column(Integer, ForeignKey('sku.id'), nullable=False, default=0, comment='SKU ID')
    qty = Column(Integer, nullable=False, default=0, comment='拣货数量')
    picked_qty = Column(Integer, nullable=False, default=0, comment='已拣货数量')
    weight = Column(Numeric(precision=10, scale=2), nullable=False, default=0, comment='重量')
    volume = Column(Numeric(precision=10, scale=2), nullable=False, default=0, comment='体积')
    price = Column(Numeric(precision=10, scale=2), nullable=False, default=0, comment='价格')
    expiry_date = Column(BigInteger, nullable=False, default=0, comment='过期日期')
    goods_location_id = Column(Integer, nullable=False, default=0, comment='拣货库位ID')
    picker_id = Column(Integer, nullable=False, default=0, comment='拣货人ID')
    picker = Column(String(64), nullable=False, default='', comment='拣货人')
    pick_time = Column(BigInteger, nullable=False, default=0, comment='拣货时间')
    series_number = Column(String(100), nullable=False, default='', comment='序列号')
    tenant_id = Column(String(36), nullable=False, default='', comment='租户ID')

    pick_putaway = relationship("OutboundPickPutaway", back_populates="items")
    sku = relationship("Sku")
