from datetime import datetime
from sqlalchemy import String, Boolean, BigInteger, SmallInteger, ForeignKey
from sqlalchemy.orm import mapped_column, relationship
from app.models.base import WMSBaseModel


class Spu(WMSBaseModel):
    """
    SPU(标准产品单元)实体类
    
    用于存储商品的基本信息,包括商品编码、名称、分类、供应商、品牌等通用属性
    """
    __tablename__ = "spu"

    spu_code = mapped_column(String(50), nullable=False, default="", comment="SPU编码")
    spu_name = mapped_column(String(100), nullable=False, default="", comment="SPU名称")
    category_id = mapped_column(BigInteger, nullable=False, default=0, comment="分类ID")
    spu_description = mapped_column(String(500), nullable=False, default="", comment="SPU描述")
    supplier_id = mapped_column(BigInteger, nullable=False, default=0, comment="供应商ID")
    supplier_name = mapped_column(String(100), nullable=False, default="", comment="供应商名称")
    brand = mapped_column(String(100), nullable=False, default="", comment="品牌")
    origin = mapped_column(String(100), nullable=False, default="", comment="产地")
    length_unit = mapped_column(SmallInteger, nullable=False, default=0, comment="长度单位")
    volume_unit = mapped_column(SmallInteger, nullable=False, default=0, comment="体积单位")
    weight_unit = mapped_column(SmallInteger, nullable=False, default=0, comment="重量单位")
    creator = mapped_column(String(50), nullable=False, default="", comment="创建人")
    create_time = mapped_column(BigInteger, nullable=False, default=lambda: int(datetime.now().timestamp()), comment="创建时间")
    last_update_time = mapped_column(BigInteger, nullable=False, default=lambda: int(datetime.now().timestamp()), comment="最后更新时间")
    is_valid = mapped_column(Boolean, nullable=False, default=True, comment="是否有效")
    tenant_id = mapped_column(String(36), nullable=False, default="", comment="租户ID")
