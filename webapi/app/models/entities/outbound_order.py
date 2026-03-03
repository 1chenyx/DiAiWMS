from sqlalchemy import Column, String, Integer, Boolean, BigInteger, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import WMSBaseModel


class OutboundOrder(WMSBaseModel):
    """
    出库订单实体类
    
    用于记录出库订单信息，是出库流程的第一阶段
    状态：0-待处理，1-已生成拣货单，2-已取消
    """
    __tablename__ = 'outbound_order'

    order_no = Column(String(64), nullable=False, default='', comment='出库订单号')
    order_status = Column(Integer, nullable=False, default=0, comment='订单状态：0-待处理，1-已生成拣货单，2-已取消')
    customer_id = Column(Integer, nullable=False, default=0, comment='客户ID')
    customer_name = Column(String(128), nullable=False, default='', comment='客户名称')
    warehouse_id = Column(Integer, nullable=False, default=0, comment='仓库ID')
    goods_owner_id = Column(Integer, nullable=False, default=0, comment='货主ID')
    goods_owner_name = Column(String(128), nullable=False, default='', comment='货主名称')
    total_qty = Column(Integer, nullable=False, default=0, comment='总数量')
    total_weight = Column(Numeric(precision=10, scale=2), nullable=False, default=0, comment='总重量')
    total_volume = Column(Numeric(precision=10, scale=2), nullable=False, default=0, comment='总体积')
    remark = Column(String(512), nullable=True, comment='备注')
    creator = Column(String(64), nullable=False, default='', comment='创建人')
    create_time = Column(BigInteger, nullable=False, default=0, comment='创建时间')
    last_update_time = Column(BigInteger, nullable=False, default=0, comment='最后更新时间')
    tenant_id = Column(String(36), nullable=False, default='', comment='租户ID')

    items = relationship("OutboundOrderItem", back_populates="order", cascade="all, delete-orphan")
    pick_putaway = relationship("OutboundPickPutaway", back_populates="order", uselist=False)
