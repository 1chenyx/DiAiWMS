from typing import Optional
from pydantic import BaseModel, Field


class WarehouseViewModel(BaseModel):
    """
    仓库视图模型
    
    用于仓库信息的展示和返回
    """
    id: int = Field(default=0, description="主键ID")
    warehouse_name: str = Field(default="", max_length=32, description="仓库名称")
    city: str = Field(default="", max_length=128, description="城市")
    address: str = Field(default="", max_length=256, description="地址")
    email: str = Field(default="", max_length=128, description="邮箱")
    manager: str = Field(default="", max_length=64, description="管理员")
    contact_tel: str = Field(default="", max_length=64, description="联系电话")
    creator: str = Field(default="", max_length=64, description="创建人")
    create_time: int = Field(default=0, description="创建时间")
    last_update_time: int = Field(default=0, description="最后更新时间")
    is_valid: bool = Field(default=True, description="是否有效")
    tenant_id: str = Field(default="", description="租户ID")


class WarehouseCreateViewModel(BaseModel):
    """
    仓库创建视图模型
    
    用于创建新仓库时的数据验证和序列化
    """
    warehouse_name: str = Field(..., max_length=32, description="仓库名称")
    city: str = Field(..., max_length=128, description="城市")
    address: str = Field(..., max_length=256, description="地址")
    email: Optional[str] = Field(default="", max_length=128, description="邮箱")
    manager: Optional[str] = Field(default="", max_length=64, description="管理员")
    contact_tel: Optional[str] = Field(default="", max_length=64, description="联系电话")
    is_valid: bool = Field(default=True, description="是否有效")


class WarehouseUpdateViewModel(BaseModel):
    """
    仓库更新视图模型
    
    用于更新仓库信息时的数据验证和序列化
    """
    id: int = Field(..., description="仓库ID")
    warehouse_name: Optional[str] = Field(None, max_length=32, description="仓库名称")
    city: Optional[str] = Field(None, max_length=128, description="城市")
    address: Optional[str] = Field(None, max_length=256, description="地址")
    email: Optional[str] = Field(None, max_length=128, description="邮箱")
    manager: Optional[str] = Field(None, max_length=64, description="管理员")
    contact_tel: Optional[str] = Field(None, max_length=64, description="联系电话")
    is_valid: Optional[bool] = Field(None, description="是否有效")
