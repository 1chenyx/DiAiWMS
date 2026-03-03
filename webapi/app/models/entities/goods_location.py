from datetime import datetime
from sqlalchemy import String, BigInteger, Boolean, Numeric
from sqlalchemy.orm import mapped_column
from app.models.base import WMSBaseModel


class GoodsLocation(WMSBaseModel):
    """
    货位实体类
    
    用于存储仓库中具体的货位信息,包括货位名称、尺寸、载重、所在位置等
    """
    __tablename__ = "goodslocation"

    warehouse_id = mapped_column(BigInteger, nullable=False, default=0, comment="仓库ID")
    warehouse_name = mapped_column(String(100), nullable=False, default="", comment="仓库名称")
    warehouse_area_name = mapped_column(String(100), nullable=False, default="", comment="库区名称")
    warehouse_area_property = mapped_column(BigInteger, nullable=False, default=0, comment="库区属性")
    location_name = mapped_column(String(100), nullable=False, default="", comment="货位名称")
    location_length = mapped_column(Numeric(10, 2), nullable=False, default=0, comment="货位长度")
    location_width = mapped_column(Numeric(10, 2), nullable=False, default=0, comment="货位宽度")
    location_heigth = mapped_column(Numeric(10, 2), nullable=False, default=0, comment="货位高度")
    location_volume = mapped_column(Numeric(10, 2), nullable=False, default=0, comment="货位体积")
    location_load = mapped_column(Numeric(10, 2), nullable=False, default=0, comment="货位载重")
    roadway_number = mapped_column(String(50), nullable=False, default="", comment="巷道号")
    shelf_number = mapped_column(String(50), nullable=False, default="", comment="货架号")
    layer_number = mapped_column(String(50), nullable=False, default="", comment="层号")
    tag_number = mapped_column(String(50), nullable=False, default="", comment="标签号")
    create_time = mapped_column(BigInteger, nullable=False, default=lambda: int(datetime.now().timestamp()), comment="创建时间")
    last_update_time = mapped_column(BigInteger, nullable=False, default=lambda: int(datetime.now().timestamp()), comment="最后更新时间")
    is_valid = mapped_column(Boolean, nullable=False, default=False, comment="是否有效")
    tenant_id = mapped_column(String(36), nullable=False, default="", comment="租户ID")
    warehouse_area_id = mapped_column(BigInteger, nullable=False, default=0, comment="库区ID")
