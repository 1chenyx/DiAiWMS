from typing import Optional
from pydantic import BaseModel, Field


class WarehouseAreaViewModel(BaseModel):
    """
    仓库区域视图模型
    
    用于仓库区域信息的展示和返回
    """
    id: int = Field(default=0, description="主键ID")
    warehouse_id: int = Field(default=0, description="仓库ID")
    area_name: str = Field(default="", max_length=100, description="区域名称")
    parent_id: int = Field(default=0, description="父区域ID")
    create_time: int = Field(default=0, description="创建时间")
    last_update_time: int = Field(default=0, description="最后更新时间")
    is_valid: bool = Field(default=False, description="是否有效")
    tenant_id: str = Field(default="", description="租户ID")
    area_property: int = Field(default=0, description="区域属性")


class WarehouseAreaCreateViewModel(BaseModel):
    """
    仓库区域创建视图模型
    
    用于创建新仓库区域时的数据验证和序列化
    """
    warehouse_id: int = Field(..., description="仓库ID")
    area_name: str = Field(..., max_length=100, description="区域名称")
    parent_id: int = Field(default=0, description="父区域ID")
    is_valid: bool = Field(default=True, description="是否有效")
    area_property: int = Field(default=0, description="区域属性")


class WarehouseAreaUpdateViewModel(BaseModel):
    """
    仓库区域更新视图模型
    
    用于更新仓库区域信息时的数据验证和序列化
    """
    id: int = Field(..., description="库区ID")
    area_name: Optional[str] = Field(None, max_length=100, description="区域名称")
    parent_id: Optional[int] = Field(None, description="父区域ID")
    is_valid: Optional[bool] = Field(None, description="是否有效")
    area_property: Optional[int] = Field(None, description="区域属性")
