from sqlalchemy import Column, String, Integer, Boolean, BigInteger, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import WMSBaseModel


class OutboundReceipt(WMSBaseModel):
    """
    出库单实体类
    
    用于记录出库单信息，是出库流程的第三阶段（最终单）
    在此阶段扣减库存
    状态：0-待出库，1-已出库，2-已取消
    """
    __tablename__ = 'outbound_receipt'

    receipt_no = Column(String(64), nullable=False, default='', comment='出库单号')
    receipt_status = Column(Integer, nullable=False, default=0, comment='出库单状态：0-待出库，1-已出库，2-已取消')
    pick_putaway_id = Column(Integer, ForeignKey('outbound_pick_putaway.id'), nullable=False, comment='拣货上架单ID')
    order_id = Column(Integer, nullable=False, default=0, comment='出库订单ID')
    order_no = Column(String(64), nullable=False, default='', comment='出库订单号')
    customer_id = Column(Integer, nullable=False, default=0, comment='客户ID')
    customer_name = Column(String(128), nullable=False, default='', comment='客户名称')
    warehouse_id = Column(Integer, nullable=False, default=0, comment='仓库ID')
    goods_owner_id = Column(Integer, nullable=False, default=0, comment='货主ID')
    goods_owner_name = Column(String(128), nullable=False, default='', comment='货主名称')
    total_qty = Column(Integer, nullable=False, default=0, comment='总数量')
    actual_qty = Column(Integer, nullable=False, default=0, comment='实际出库数量')
    total_weight = Column(Numeric(precision=10, scale=2), nullable=False, default=0, comment='总重量')
    actual_weight = Column(Numeric(precision=10, scale=2), nullable=False, default=0, comment='实际重量')
    total_volume = Column(Numeric(precision=10, scale=2), nullable=False, default=0, comment='总体积')
    actual_volume = Column(Numeric(precision=10, scale=2), nullable=False, default=0, comment='实际体积')
    package_no = Column(String(64), nullable=False, default='', comment='打包单号')
    package_person = Column(String(64), nullable=False, default='', comment='打包人')
    package_time = Column(BigInteger, nullable=False, default=0, comment='打包时间')
    weighing_no = Column(String(64), nullable=False, default='', comment='称重单号')
    weighing_person = Column(String(64), nullable=False, default='', comment='称重人')
    weighing_weight = Column(Numeric(precision=10, scale=2), nullable=False, default=0, comment='称重重量')
    waybill_no = Column(String(64), nullable=False, default='', comment='运单号')
    carrier = Column(String(128), nullable=False, default='', comment='承运商')
    freightfee = Column(Numeric(precision=10, scale=2), nullable=False, default=0, comment='运费')
    outbound_time = Column(BigInteger, nullable=False, default=0, comment='出库时间')
    outbound_person = Column(String(64), nullable=False, default='', comment='出库人')
    remark = Column(String(512), nullable=True, comment='备注')
    creator = Column(String(64), nullable=False, default='', comment='创建人')
    create_time = Column(BigInteger, nullable=False, default=0, comment='创建时间')
    last_update_time = Column(BigInteger, nullable=False, default=0, comment='最后更新时间')
    tenant_id = Column(String(36), nullable=False, default='', comment='租户ID')

    items = relationship("OutboundReceiptItem", back_populates="receipt", cascade="all, delete-orphan")
    pick_putaway = relationship("OutboundPickPutaway", back_populates="receipt")
