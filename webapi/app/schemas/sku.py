from typing import Optional
from pydantic import BaseModel, Field


class SkuViewModel(BaseModel):
    """
    SKU视图模型
    
    用于SKU信息的展示和返回
    """
    id: int = Field(default=0, description="主键ID")
    spu_id: int = Field(default=0, description="SPU ID")
    sku_code: str = Field(default="", max_length=50, description="SKU编码")
    sku_name: str = Field(default="", max_length=100, description="SKU名称")
    bar_code: str = Field(default="", max_length=50, description="条码")
    weight: float = Field(default=0, description="重量")
    lenght: float = Field(default=0, description="长度")
    width: float = Field(default=0, description="宽度")
    height: float = Field(default=0, description="高度")
    volume: float = Field(default=0, description="体积")
    unit: str = Field(default="", max_length=20, description="单位")
    cost: float = Field(default=0, description="成本")
    price: float = Field(default=0, description="价格")
    create_time: int = Field(default=0, description="创建时间")
    last_update_time: int = Field(default=0, description="最后更新时间")
    available_quantity: int = Field(default=0, description="可用库存数量")


class SkuCreateViewModel(BaseModel):
    """
    SKU创建视图模型
    
    用于创建新SKU时的数据验证和序列化
    """
    spu_id: int = Field(..., description="SPU ID")
    sku_code: str = Field(..., max_length=50, description="SKU编码")
    sku_name: str = Field(..., max_length=100, description="SKU名称")
    bar_code: Optional[str] = Field(default="", max_length=50, description="条码")
    weight: float = Field(default=0, description="重量")
    lenght: float = Field(default=0, description="长度")
    width: float = Field(default=0, description="宽度")
    height: float = Field(default=0, description="高度")
    volume: float = Field(default=0, description="体积")
    unit: Optional[str] = Field(default="", max_length=20, description="单位")
    cost: float = Field(default=0, description="成本")
    price: float = Field(default=0, description="价格")


class SkuUpdateViewModel(BaseModel):
    """
    SKU更新视图模型
    
    用于更新SKU信息时的数据验证和序列化
    """
    id: int = Field(..., description="SKU ID")
    spu_id: Optional[int] = Field(None, description="SPU ID")
    sku_code: Optional[str] = Field(None, max_length=50, description="SKU编码")
    sku_name: Optional[str] = Field(None, max_length=100, description="SKU名称")
    bar_code: Optional[str] = Field(None, max_length=50, description="条码")
    weight: Optional[float] = Field(None, description="重量")
    lenght: Optional[float] = Field(None, description="长度")
    width: Optional[float] = Field(None, description="宽度")
    height: Optional[float] = Field(None, description="高度")
    volume: Optional[float] = Field(None, description="体积")
    unit: Optional[str] = Field(None, max_length=20, description="单位")
    cost: Optional[float] = Field(None, description="成本")
    price: Optional[float] = Field(None, description="价格")


class SpuSkuCreateViewModel(BaseModel):
    """
    SPU嵌套SKU创建视图模型
    
    用于在创建SPU时嵌套创建SKU，不需要spu_id字段
    """
    sku_code: str = Field(..., max_length=50, description="SKU编码")
    sku_name: str = Field(..., max_length=100, description="SKU名称")
    bar_code: Optional[str] = Field(default="", max_length=50, description="条码")
    weight: float = Field(default=0, description="重量")
    lenght: float = Field(default=0, description="长度")
    width: float = Field(default=0, description="宽度")
    height: float = Field(default=0, description="高度")
    volume: float = Field(default=0, description="体积")
    unit: Optional[str] = Field(default="", max_length=20, description="单位")
    cost: float = Field(default=0, description="成本")
    price: float = Field(default=0, description="价格")
