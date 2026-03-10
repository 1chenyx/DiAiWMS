from sqlalchemy import Column, String, Integer, Boolean, BigInteger, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import WMSBaseModel


class InboundPickPutaway(WMSBaseModel):
    """
    入库拣货上架单实体类
    
    用于记录入库拣货上架信息，是入库流程的第二阶段
    在此阶段锁定库存（预分配库位）
    状态：0-待上架，1-上架中，2-上架完成，3-已生成入库单，4-已取消
    """
    __tablename__ = 'inbound_pick_putaway'

    pick_putaway_no = Column(String(64), nullable=False, default='', comment='拣货上架单号')
    pick_putaway_status = Column(Integer, nullable=False, default=0, comment='拣货上架状态：0-待上架，1-上架中，2-上架完成，3-已生成入库单，4-已取消')
    order_id = Column(Integer, ForeignKey('inbound_order.id'), nullable=False, comment='入库订单ID')
    order_no = Column(String(64), nullable=False, default='', comment='入库订单号')
    order_nos = Column(String(512), nullable=False, default='', comment='入库订单号列表（JSON格式）')
    supplier_id = Column(Integer, nullable=False, default=0, comment='供应商ID')
    supplier_name = Column(String(128), nullable=False, default='', comment='供应商名称')
    warehouse_id = Column(Integer, nullable=False, default=0, comment='仓库ID')
    goods_owner_id = Column(Integer, nullable=False, default=0, comment='货主ID')
    goods_owner_name = Column(String(128), nullable=False, default='', comment='货主名称')
    total_qty = Column(Integer, nullable=False, default=0, comment='总数量')
    putaway_qty = Column(Integer, nullable=False, default=0, comment='已上架数量')
    total_weight = Column(Numeric(precision=10, scale=2), nullable=False, default=0, comment='总重量')
    total_volume = Column(Numeric(precision=10, scale=2), nullable=False, default=0, comment='总体积')
    putaway_person_id = Column(Integer, nullable=False, default=0, comment='上架人ID')
    putaway_person = Column(String(64), nullable=False, default='', comment='上架人')
    putaway_start_time = Column(BigInteger, nullable=False, default=0, comment='上架开始时间')
    putaway_end_time = Column(BigInteger, nullable=False, default=0, comment='上架结束时间')
    remark = Column(String(512), nullable=True, comment='备注')
    creator = Column(String(64), nullable=False, default='', comment='创建人')
    create_time = Column(BigInteger, nullable=False, default=0, comment='创建时间')
    last_update_time = Column(BigInteger, nullable=False, default=0, comment='最后更新时间')
    tenant_id = Column(String(36), nullable=False, default='', comment='租户ID')

    items = relationship("InboundPickPutawayItem", back_populates="pick_putaway", cascade="all, delete-orphan")
    order = relationship("InboundOrder", back_populates="pick_putaway")
    receipt = relationship("InboundReceipt", back_populates="pick_putaway", uselist=False)
