from datetime import datetime
from pydantic import BaseModel, Field


class CustomerCreate(BaseModel):
    """
    客户创建视图模型
    
    用于创建新客户时的数据验证和序列化
    """
    customer_name: str = Field(..., max_length=256, description='客户名称')
    city: str = Field('', max_length=128, description='城市')
    address: str = Field('', max_length=256, description='地址')
    manager: str = Field('', max_length=64, description='管理员')
    email: str = Field('', max_length=128, description='邮箱')
    contact_tel: str = Field('', max_length=64, description='联系电话')


class CustomerUpdate(BaseModel):
    """
    客户更新视图模型
    
    用于更新客户信息时的数据验证和序列化
    """
    id: int
    customer_name: str = Field(..., max_length=256, description='客户名称')
    city: str = Field('', max_length=128, description='城市')
    address: str = Field('', max_length=256, description='地址')
    manager: str = Field('', max_length=64, description='管理员')
    email: str = Field('', max_length=128, description='邮箱')
    contact_tel: str = Field('', max_length=64, description='联系电话')


class CustomerViewModel(BaseModel):
    """
    客户视图模型
    
    用于客户信息的展示和返回
    """
    id: int
    customer_name: str
    city: str
    address: str
    manager: str
    email: str
    contact_tel: str
    creator: str
    create_time: int
    last_update_time: int
    is_valid: bool

    class Config:
        from_attributes = True
