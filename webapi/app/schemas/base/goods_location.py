from typing import Optional
from pydantic import BaseModel, Field


class GoodsLocationViewModel(BaseModel):
    """
    货位视图模型
    
    用于货位信息的展示和返回
    """
    id: int = Field(default=0, description="主键ID")
    warehouse_id: int = Field(default=0, description="仓库ID")
    warehouse_name: str = Field(default="", max_length=100, description="仓库名称")
    warehouse_area_name: str = Field(default="", max_length=100, description="库区名称")
    warehouse_area_property: int = Field(default=0, description="库区属性")
    location_name: str = Field(default="", max_length=100, description="货位名称")
    location_length: float = Field(default=0, description="货位长度")
    location_width: float = Field(default=0, description="货位宽度")
    location_heigth: float = Field(default=0, description="货位高度")
    location_volume: float = Field(default=0, description="货位体积")
    location_load: float = Field(default=0, description="货位载重")
    roadway_number: str = Field(default="", max_length=50, description="巷道号")
    shelf_number: str = Field(default="", max_length=50, description="货架号")
    layer_number: str = Field(default="", max_length=50, description="层号")
    tag_number: str = Field(default="", max_length=50, description="标签号")
    create_time: int = Field(default=0, description="创建时间")
    last_update_time: int = Field(default=0, description="最后更新时间")
    is_valid: bool = Field(default=False, description="是否有效")
    tenant_id: str = Field(default="", description="租户ID")
    warehouse_area_id: int = Field(default=0, description="库区ID")


class GoodsLocationCreateViewModel(BaseModel):
    """
    货位创建视图模型
    
    用于创建新货位时的数据验证和序列化
    """
    warehouse_id: int = Field(..., description="仓库ID")
    location_name: str = Field(..., max_length=100, description="货位名称")
    location_length: float = Field(default=0, description="货位长度")
    location_width: float = Field(default=0, description="货位宽度")
    location_heigth: float = Field(default=0, description="货位高度")
    location_volume: float = Field(default=0, description="货位体积")
    location_load: float = Field(default=0, description="货位载重")
    roadway_number: Optional[str] = Field(default="", max_length=50, description="巷道号")
    shelf_number: Optional[str] = Field(default="", max_length=50, description="货架号")
    layer_number: Optional[str] = Field(default="", max_length=50, description="层号")
    tag_number: Optional[str] = Field(default="", max_length=50, description="标签号")
    warehouse_area_id: int = Field(default=0, description="库区ID")
    is_valid: bool = Field(default=True, description="是否有效")


class GoodsLocationUpdateViewModel(BaseModel):
    """
    货位更新视图模型
    
    用于更新货位信息时的数据验证和序列化
    """
    id: int = Field(..., description="货位ID")
    location_name: Optional[str] = Field(None, max_length=100, description="货位名称")
    location_length: Optional[float] = Field(None, description="货位长度")
    location_width: Optional[float] = Field(None, description="货位宽度")
    location_heigth: Optional[float] = Field(None, description="货位高度")
    location_volume: Optional[float] = Field(None, description="货位体积")
    location_load: Optional[float] = Field(None, description="货位载重")
    roadway_number: Optional[str] = Field(None, max_length=50, description="巷道号")
    shelf_number: Optional[str] = Field(None, max_length=50, description="货架号")
    layer_number: Optional[str] = Field(None, max_length=50, description="层号")
    tag_number: Optional[str] = Field(None, max_length=50, description="标签号")
    warehouse_area_id: Optional[int] = Field(None, description="库区ID")
    is_valid: Optional[bool] = Field(None, description="是否有效")
