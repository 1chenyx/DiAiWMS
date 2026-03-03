from sqlalchemy import Column, String, Integer, Boolean, BigInteger, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import WMSBaseModel


class OutboundPickPutaway(WMSBaseModel):
    """
    出库拣货上架单实体类
    
    用于记录出库拣货上架信息，是出库流程的第二阶段
    在此阶段锁定库存
    状态：0-待拣货，1-拣货中，2-拣货完成，3-已生成出库单，4-已取消
    """
    __tablename__ = 'outbound_pick_putaway'

    pick_putaway_no = Column(String(64), nullable=False, default='', comment='拣货上架单号')
    pick_putaway_status = Column(Integer, nullable=False, default=0, comment='拣货上架状态：0-待拣货，1-拣货中，2-拣货完成，3-已生成出库单，4-已取消')
    order_id = Column(Integer, ForeignKey('outbound_order.id'), nullable=False, comment='出库订单ID')
    order_no = Column(String(64), nullable=False, default='', comment='出库订单号')
    customer_id = Column(Integer, nullable=False, default=0, comment='客户ID')
    customer_name = Column(String(128), nullable=False, default='', comment='客户名称')
    warehouse_id = Column(Integer, nullable=False, default=0, comment='仓库ID')
    goods_owner_id = Column(Integer, nullable=False, default=0, comment='货主ID')
    goods_owner_name = Column(String(128), nullable=False, default='', comment='货主名称')
    total_qty = Column(Integer, nullable=False, default=0, comment='总数量')
    picked_qty = Column(Integer, nullable=False, default=0, comment='已拣货数量')
    total_weight = Column(Numeric(precision=10, scale=2), nullable=False, default=0, comment='总重量')
    total_volume = Column(Numeric(precision=10, scale=2), nullable=False, default=0, comment='总体积')
    picker_id = Column(Integer, nullable=False, default=0, comment='拣货人ID')
    picker = Column(String(64), nullable=False, default='', comment='拣货人')
    pick_start_time = Column(BigInteger, nullable=False, default=0, comment='拣货开始时间')
    pick_end_time = Column(BigInteger, nullable=False, default=0, comment='拣货结束时间')
    remark = Column(String(512), nullable=True, comment='备注')
    creator = Column(String(64), nullable=False, default='', comment='创建人')
    create_time = Column(BigInteger, nullable=False, default=0, comment='创建时间')
    last_update_time = Column(BigInteger, nullable=False, default=0, comment='最后更新时间')
    tenant_id = Column(String(36), nullable=False, default='', comment='租户ID')

    items = relationship("OutboundPickPutawayItem", back_populates="pick_putaway", cascade="all, delete-orphan")
    order = relationship("OutboundOrder", back_populates="pick_putaway")
    receipt = relationship("OutboundReceipt", back_populates="pick_putaway", uselist=False)
