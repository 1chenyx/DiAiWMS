from datetime import datetime
from sqlalchemy import String, Boolean, BigInteger, SmallInteger, Numeric
from sqlalchemy.orm import mapped_column
from app.models.base import WMSBaseModel


class WarehouseLocation(WMSBaseModel):
    """
    仓库位置实体类（统一的三级树形结构）
    
    用于管理仓库、库区、库位的统一树形结构
    node_type: 1-仓库, 2-库区, 3-库位
    """
    __tablename__ = "warehouselocation"

    node_type = mapped_column(SmallInteger, nullable=False, default=1, comment="节点类型: 1-仓库, 2-库区, 3-库位")
    parent_id = mapped_column(BigInteger, nullable=False, default=0, comment="父节点ID (仓库为0)")
    node_name = mapped_column(String(100), nullable=False, default="", comment="节点名称")
    
    city = mapped_column(String(50), nullable=False, default="", comment="城市 (仓库)")
    address = mapped_column(String(200), nullable=False, default="", comment="地址 (仓库)")
    email = mapped_column(String(100), nullable=False, default="", comment="邮箱 (仓库)")
    manager = mapped_column(String(50), nullable=False, default="", comment="管理员 (仓库)")
    contact_tel = mapped_column(String(20), nullable=False, default="", comment="联系电话 (仓库)")
    
    area_property = mapped_column(SmallInteger, nullable=False, default=0, comment="区域属性 (库区)")
    
    location_length = mapped_column(Numeric(10, 2), nullable=False, default=0, comment="货位长度 (库位)")
    location_width = mapped_column(Numeric(10, 2), nullable=False, default=0, comment="货位宽度 (库位)")
    location_height = mapped_column(Numeric(10, 2), nullable=False, default=0, comment="货位高度 (库位)")
    location_volume = mapped_column(Numeric(10, 2), nullable=False, default=0, comment="货位体积 (库位)")
    location_load = mapped_column(Numeric(10, 2), nullable=False, default=0, comment="货位载重 (库位)")
    roadway_number = mapped_column(String(50), nullable=False, default="", comment="巷道号 (库位)")
    shelf_number = mapped_column(String(50), nullable=False, default="", comment="货架号 (库位)")
    layer_number = mapped_column(String(50), nullable=False, default="", comment="层号 (库位)")
    tag_number = mapped_column(String(50), nullable=False, default="", comment="标签号 (库位)")
    
    create_time = mapped_column(BigInteger, nullable=False, default=lambda: int(datetime.now().timestamp()), comment="创建时间")
    last_update_time = mapped_column(BigInteger, nullable=False, default=lambda: int(datetime.now().timestamp()), comment="最后更新时间")
    is_valid = mapped_column(Boolean, nullable=False, default=False, comment="是否有效")
    tenant_id = mapped_column(String(36), nullable=False, default="", comment="租户ID")
    creator = mapped_column(String(50), nullable=False, default="", comment="创建人")
