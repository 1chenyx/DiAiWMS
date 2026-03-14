from datetime import datetime
from pydantic import BaseModel, Field


class SupplierCreate(BaseModel):
    """
    供应商创建视图模型
    
    用于创建新供应商时的数据验证和序列化
    """
    supplier_name: str = Field(..., max_length=256, description='供应商名称')
    city: str = Field('', max_length=128, description='城市')
    address: str = Field('', max_length=256, description='地址')
    manager: str = Field('', max_length=64, description='管理员')
    email: str = Field('', max_length=128, description='邮箱')
    contact_tel: str = Field('', max_length=64, description='联系电话')


class SupplierUpdate(BaseModel):
    """
    供应商更新视图模型
    
    用于更新供应商信息时的数据验证和序列化
    """
    id: int
    supplier_name: str = Field(..., max_length=256, description='供应商名称')
    city: str = Field('', max_length=128, description='城市')
    address: str = Field('', max_length=256, description='地址')
    manager: str = Field('', max_length=64, description='管理员')
    email: str = Field('', max_length=128, description='邮箱')
    contact_tel: str = Field('', max_length=64, description='联系电话')


class SupplierViewModel(BaseModel):
    """
    供应商视图模型
    
    用于供应商信息的展示和返回
    """
    id: int
    supplier_name: str
    city: str
    address: str
    manager: str
    email: str
    contact_tel: str
    creator: str
    create_time: int
    last_update_time: int
    is_valid: bool
    tenant_id: str

    class Config:
        from_attributes = True
