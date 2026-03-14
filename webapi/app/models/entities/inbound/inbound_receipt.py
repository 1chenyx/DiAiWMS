from sqlalchemy import Column, String, Integer, Boolean, BigInteger, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import WMSBaseModel


class InboundReceipt(WMSBaseModel):
    """
    入库单实体类
    
    用于记录入库单信息，是入库流程的第三阶段（最终单）
    在此阶段增加库存
    状态：0-待入库，1-已入库，2-已取消
    """
    __tablename__ = 'inbound_receipt'

    receipt_no = Column(String(64), nullable=False, default='', comment='入库单号')
    receipt_status = Column(Integer, nullable=False, default=0, comment='入库单状态：0-待入库，1-已入库，2-已取消')
    pick_putaway_id = Column(Integer, ForeignKey('inbound_pick_putaway.id'), nullable=False, comment='拣货上架单ID')
    order_id = Column(Integer, nullable=False, default=0, comment='入库订单ID')
    order_no = Column(String(64), nullable=False, default='', comment='入库订单号')
    supplier_id = Column(Integer, nullable=False, default=0, comment='供应商ID')
    supplier_name = Column(String(128), nullable=False, default='', comment='供应商名称')
    warehouse_id = Column(Integer, nullable=False, default=0, comment='仓库ID')
    goods_owner_id = Column(Integer, nullable=False, default=0, comment='货主ID')
    goods_owner_name = Column(String(128), nullable=False, default='', comment='货主名称')
    total_qty = Column(Integer, nullable=False, default=0, comment='总数量')
    actual_qty = Column(Integer, nullable=False, default=0, comment='实际入库数量')
    total_weight = Column(Numeric(precision=10, scale=2), nullable=False, default=0, comment='总重量')
    actual_weight = Column(Numeric(precision=10, scale=2), nullable=False, default=0, comment='实际重量')
    total_volume = Column(Numeric(precision=10, scale=2), nullable=False, default=0, comment='总体积')
    actual_volume = Column(Numeric(precision=10, scale=2), nullable=False, default=0, comment='实际体积')
    arrival_time = Column(BigInteger, nullable=False, default=0, comment='到货时间')
    unload_time = Column(BigInteger, nullable=False, default=0, comment='卸货时间')
    unload_person_id = Column(Integer, nullable=False, default=0, comment='卸货人ID')
    unload_person = Column(String(64), nullable=False, default='', comment='卸货人')
    inbound_time = Column(BigInteger, nullable=False, default=0, comment='入库时间')
    inbound_person = Column(String(64), nullable=False, default='', comment='入库人')
    remark = Column(String(512), nullable=True, comment='备注')
    creator = Column(String(64), nullable=False, default='', comment='创建人')
    create_time = Column(BigInteger, nullable=False, default=0, comment='创建时间')
    last_update_time = Column(BigInteger, nullable=False, default=0, comment='最后更新时间')
    tenant_id = Column(String(36), nullable=False, default='', comment='租户ID')

    items = relationship("InboundReceiptItem", back_populates="receipt", cascade="all, delete-orphan")
    pick_putaway = relationship("InboundPickPutaway", back_populates="receipt")
