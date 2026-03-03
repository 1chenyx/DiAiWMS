from datetime import datetime
from sqlalchemy import Column, Integer, String, Numeric, BigInteger, Boolean
from app.models.base import WMSBaseModel


class Freightfee(WMSBaseModel):
    """
    运费实体类
    
    用于存储运费计算规则,包括承运商、出发城市、到达城市、价格等信息
    """
    __tablename__ = "freightfee"

    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键ID')
    carrier = Column(String(64), nullable=False, default='', comment='承运商')
    departure_city = Column(String(64), nullable=False, default='', comment='出发城市')
    arrival_city = Column(String(64), nullable=False, default='', comment='到达城市')
    price_per_weight = Column(Numeric(10, 2), nullable=False, default=0, comment='每公斤价格')
    price_per_volume = Column(Numeric(10, 2), nullable=False, default=0, comment='每立方米价格')
    min_payment = Column(Numeric(10, 2), nullable=False, default=0, comment='最低运费')
    creator = Column(String(64), nullable=False, default='', comment='创建人')
    create_time = Column(BigInteger, nullable=False, default=lambda: int(datetime.now().timestamp()), comment='创建时间')
    last_update_time = Column(BigInteger, nullable=False, default=lambda: int(datetime.now().timestamp()), comment='最后更新时间')
    is_valid = Column(Boolean, nullable=False, default=False, comment='是否有效')
    tenant_id = Column(String(36), nullable=False, default='', comment='租户ID')
