from datetime import datetime
from sqlalchemy import String, BigInteger, Boolean, Numeric
from sqlalchemy.orm import mapped_column
from app.models.base import WMSBaseModel


class Stock(WMSBaseModel):
    """
    库存实体类
    
    用于记录仓库中各个货位的库存信息,包括SKU、数量、货位、货主等
    """
    __tablename__ = "stock"

    sku_id = mapped_column(BigInteger, nullable=False, default=0, comment="SKU ID")
    goods_location_id = mapped_column(BigInteger, nullable=False, default=0, comment="货位ID")
    qty = mapped_column(BigInteger, nullable=False, default=0, comment="数量")
    goods_owner_id = mapped_column(BigInteger, nullable=False, default=0, comment="货主ID")
    is_freeze = mapped_column(Boolean, nullable=False, default=False, comment="是否冻结")
    last_update_time = mapped_column(BigInteger, nullable=False, default=lambda: int(datetime.now().timestamp()), comment="最后更新时间")
    tenant_id = mapped_column(String(36), nullable=False, default="", comment="租户ID")
    series_number = mapped_column(String(100), nullable=False, default="", comment="序列号")
    expiry_date = mapped_column(BigInteger, nullable=False, default=lambda: int(datetime(1900, 1, 1).timestamp()), comment="过期日期")
    price = mapped_column(Numeric(10, 2), nullable=False, default=0, comment="价格")
    putaway_date = mapped_column(BigInteger, nullable=False, default=lambda: int(datetime(1900, 1, 1).timestamp()), comment="上架日期")
