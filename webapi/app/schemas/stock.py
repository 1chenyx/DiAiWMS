from typing import Optional
from pydantic import BaseModel, Field


class StockViewModel(BaseModel):
    """
    库存视图模型
    
    用于库存信息的展示和返回
    """
    id: int = Field(default=0, description="主键ID")
    sku_id: int = Field(default=0, description="SKU ID")
    goods_location_id: int = Field(default=0, description="货位ID")
    qty: int = Field(default=0, description="数量")
    goods_owner_id: int = Field(default=0, description="货主ID")
    is_freeze: bool = Field(default=False, description="是否冻结")
    last_update_time: int = Field(default=0, description="最后更新时间")
    tenant_id: str = Field(default="", description="租户ID")
    series_number: str = Field(default="", max_length=100, description="序列号")
    expiry_date: int = Field(default=0, description="过期日期")
    price: float = Field(default=0, description="价格")
    putaway_date: int = Field(default=0, description="上架日期")
    warehouse_id: int = Field(default=0, description="仓库ID")
    warehouse_name: str = Field(default="", description="仓库名称")
    warehouse_area_id: int = Field(default=0, description="库区ID")
    warehouse_area_name: str = Field(default="", description="库区名称")
    warehouse_location_name: str = Field(default="", description="库位名称")
    spu_name: str = Field(default="", description="商品名称")
    sku_code: str = Field(default="", description="SKU编码")
    sku_name: str = Field(default="", description="SKU名称")


class StockCreateViewModel(BaseModel):
    """
    库存创建视图模型
    
    用于创建新库存时的数据验证和序列化
    """
    sku_id: int = Field(..., description="SKU ID")
    goods_location_id: int = Field(..., description="货位ID")
    qty: int = Field(..., description="数量")
    goods_owner_id: int = Field(..., description="货主ID")
    is_freeze: bool = Field(default=False, description="是否冻结")
    series_number: Optional[str] = Field(default="", max_length=100, description="序列号")
    expiry_date: Optional[int] = Field(default=0, description="过期日期")
    price: float = Field(default=0, description="价格")
    putaway_date: Optional[int] = Field(default=0, description="上架日期")


class StockUpdateViewModel(BaseModel):
    """
    库存更新视图模型
    
    用于更新库存信息时的数据验证和序列化
    """
    id: int = Field(..., description="库存ID")
    sku_id: Optional[int] = Field(None, description="SKU ID")
    goods_location_id: Optional[int] = Field(None, description="货位ID")
    qty: Optional[int] = Field(None, description="数量")
    goods_owner_id: Optional[int] = Field(None, description="货主ID")
    is_freeze: Optional[bool] = Field(None, description="是否冻结")
    series_number: Optional[str] = Field(None, max_length=100, description="序列号")
    expiry_date: Optional[int] = Field(None, description="过期日期")
    price: Optional[float] = Field(None, description="价格")
    putaway_date: Optional[int] = Field(None, description="上架日期")
