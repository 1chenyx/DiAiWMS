from sqlalchemy import Column, String, Integer, BigInteger, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import WMSBaseModel


class InboundPutawayTask(WMSBaseModel):
    """
    入库实际上架任务实体类
    
    用于记录每次实际上架的详细信息，支持分批上架
    """
    __tablename__ = 'inbound_putaway_task'

    pick_putaway_item_id = Column(Integer, ForeignKey('inbound_pick_putaway_item.id'), nullable=False, comment='拣货上架单明细ID')
    putaway_qty = Column(Integer, nullable=False, default=0, comment='本次上架数量')
    weight = Column(Numeric(precision=10, scale=2), nullable=False, default=0, comment='重量')
    volume = Column(Numeric(precision=10, scale=2), nullable=False, default=0, comment='体积')
    price = Column(Numeric(precision=10, scale=2), nullable=False, default=0, comment='价格')
    expiry_date = Column(BigInteger, nullable=False, default=0, comment='过期日期')
    batch_no = Column(String(64), nullable=False, default='', comment='批次号')
    production_date = Column(BigInteger, nullable=False, default=0, comment='生产日期')
    goods_location_id = Column(Integer, nullable=False, default=0, comment='上架库位ID')
    warehouse_id = Column(Integer, nullable=False, default=0, comment='仓库ID')
    warehouse_name = Column(String(100), nullable=False, default='', comment='仓库名称')
    warehouse_area_id = Column(Integer, nullable=False, default=0, comment='库区ID')
    warehouse_area_name = Column(String(100), nullable=False, default='', comment='库区名称')
    warehouse_location_name = Column(String(100), nullable=False, default='', comment='库位名称')
    putaway_person_id = Column(Integer, nullable=False, default=0, comment='上架人ID')
    putaway_person = Column(String(64), nullable=False, default='', comment='上架人')
    putaway_time = Column(BigInteger, nullable=False, default=0, comment='上架时间')
    series_number = Column(String(100), nullable=False, default='', comment='序列号')
    tenant_id = Column(String(36), nullable=False, default='', comment='租户ID')

    pick_putaway_item = relationship("InboundPickPutawayItem")
