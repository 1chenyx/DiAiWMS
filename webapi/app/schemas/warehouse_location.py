from typing import Optional, List
from pydantic import BaseModel, Field


class WarehouseLocationViewModel(BaseModel):
    """
    仓库位置视图模型（统一的三级树形结构）
    """
    id: int = Field(default=0, description="主键ID")
    node_type: int = Field(default=1, description="节点类型: 1-仓库, 2-库区, 3-库位")
    parent_id: int = Field(default=0, description="父节点ID")
    node_name: str = Field(default="", max_length=100, description="节点名称")
    city: str = Field(default="", max_length=50, description="城市")
    address: str = Field(default="", max_length=200, description="地址")
    email: str = Field(default="", max_length=100, description="邮箱")
    manager: str = Field(default="", max_length=50, description="管理员")
    contact_tel: str = Field(default="", max_length=20, description="联系电话")
    area_property: int = Field(default=0, description="区域属性")
    location_length: float = Field(default=0, description="货位长度")
    location_width: float = Field(default=0, description="货位宽度")
    location_height: float = Field(default=0, description="货位高度")
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
    creator: str = Field(default="", max_length=50, description="创建人")


class WarehouseLocationCreateViewModel(BaseModel):
    """
    仓库位置创建视图模型
    """
    node_type: int = Field(..., description="节点类型: 1-仓库, 2-库区, 3-库位")
    parent_id: int = Field(default=0, description="父节点ID")
    node_name: str = Field(..., max_length=100, description="节点名称")
    city: Optional[str] = Field(default="", max_length=50, description="城市")
    address: Optional[str] = Field(default="", max_length=200, description="地址")
    email: Optional[str] = Field(default="", max_length=100, description="邮箱")
    manager: Optional[str] = Field(default="", max_length=50, description="管理员")
    contact_tel: Optional[str] = Field(default="", max_length=20, description="联系电话")
    area_property: Optional[int] = Field(default=0, description="区域属性")
    location_length: Optional[float] = Field(default=0, description="货位长度")
    location_width: Optional[float] = Field(default=0, description="货位宽度")
    location_height: Optional[float] = Field(default=0, description="货位高度")
    location_volume: Optional[float] = Field(default=0, description="货位体积")
    location_load: Optional[float] = Field(default=0, description="货位载重")
    roadway_number: Optional[str] = Field(default="", max_length=50, description="巷道号")
    shelf_number: Optional[str] = Field(default="", max_length=50, description="货架号")
    layer_number: Optional[str] = Field(default="", max_length=50, description="层号")
    tag_number: Optional[str] = Field(default="", max_length=50, description="标签号")
    is_valid: bool = Field(default=True, description="是否有效")


class WarehouseLocationUpdateViewModel(BaseModel):
    """
    仓库位置更新视图模型
    """
    id: int = Field(..., description="仓库位置ID")
    node_name: Optional[str] = Field(None, max_length=100, description="节点名称")
    city: Optional[str] = Field(None, max_length=50, description="城市")
    address: Optional[str] = Field(None, max_length=200, description="地址")
    email: Optional[str] = Field(None, max_length=100, description="邮箱")
    manager: Optional[str] = Field(None, max_length=50, description="管理员")
    contact_tel: Optional[str] = Field(None, max_length=20, description="联系电话")
    area_property: Optional[int] = Field(None, description="区域属性")
    location_length: Optional[float] = Field(None, description="货位长度")
    location_width: Optional[float] = Field(None, description="货位宽度")
    location_height: Optional[float] = Field(None, description="货位高度")
    location_volume: Optional[float] = Field(None, description="货位体积")
    location_load: Optional[float] = Field(None, description="货位载重")
    roadway_number: Optional[str] = Field(None, max_length=50, description="巷道号")
    shelf_number: Optional[str] = Field(None, max_length=50, description="货架号")
    layer_number: Optional[str] = Field(None, max_length=50, description="层号")
    tag_number: Optional[str] = Field(None, max_length=50, description="标签号")
    is_valid: Optional[bool] = Field(None, description="是否有效")


class WarehouseLocationTreeNode(BaseModel):
    """
    仓库位置树节点模型
    """
    id: int = Field(default=0, description="主键ID")
    node_type: int = Field(default=1, description="节点类型: 1-仓库, 2-库区, 3-库位")
    node_name: str = Field(default="", description="节点名称")
    parent_id: int = Field(default=0, description="父节点ID")
    children: List['WarehouseLocationTreeNode'] = Field(default_factory=list, description="子节点")
