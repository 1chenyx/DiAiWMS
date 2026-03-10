from datetime import datetime
from sqlalchemy import String, BigInteger, SmallInteger, ForeignKey, Numeric
from sqlalchemy.orm import mapped_column
from app.models.base import WMSBaseModel


class Sku(WMSBaseModel):
    """
    SKU(库存量单位)实体类
    
    用于存储商品的具体规格信息,包括尺寸、重量、价格等详细属性
    """
    __tablename__ = "sku"

    tenant_id = mapped_column(String(50), nullable=False, default="", comment="租户ID")
    spu_id = mapped_column(BigInteger, ForeignKey("spu.id"), nullable=False, default=0, comment="SPU ID")
    sku_code = mapped_column(String(50), nullable=False, default="", comment="SKU编码")
    sku_name = mapped_column(String(100), nullable=False, default="", comment="SKU名称")
    bar_code = mapped_column(String(50), nullable=False, default="", comment="条码")
    weight = mapped_column(Numeric(10, 2), nullable=False, default=0, comment="重量")
    lenght = mapped_column(Numeric(10, 2), nullable=False, default=0, comment="长度")
    width = mapped_column(Numeric(10, 2), nullable=False, default=0, comment="宽度")
    height = mapped_column(Numeric(10, 2), nullable=False, default=0, comment="高度")
    volume = mapped_column(Numeric(10, 2), nullable=False, default=0, comment="体积")
    unit = mapped_column(String(20), nullable=False, default="", comment="单位")
    cost = mapped_column(Numeric(10, 2), nullable=False, default=0, comment="成本")
    price = mapped_column(Numeric(10, 2), nullable=False, default=0, comment="价格")
    shelf_life = mapped_column(SmallInteger, nullable=False, default=0, comment="保质期(天)")
    create_time = mapped_column(BigInteger, nullable=False, default=lambda: int(datetime.now().timestamp()), comment="创建时间")
    last_update_time = mapped_column(BigInteger, nullable=False, default=lambda: int(datetime.now().timestamp()), comment="最后更新时间")
