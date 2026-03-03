from datetime import datetime
from pydantic import BaseModel, Field


class GoodsOwnerCreate(BaseModel):
    """
    货主创建视图模型
    
    用于创建新货主时的数据验证和序列化
    """
    goods_owner_name: str = Field(..., max_length=256, description='货主名称')
    city: str = Field('', max_length=128, description='城市')
    address: str = Field('', max_length=256, description='地址')
    manager: str = Field('', max_length=64, description='管理员')
    contact_tel: str = Field('', max_length=64, description='联系电话')


class GoodsOwnerUpdate(BaseModel):
    """
    货主更新视图模型
    
    用于更新货主信息时的数据验证和序列化
    """
    id: int
    goods_owner_name: str = Field(..., max_length=256, description='货主名称')
    city: str = Field('', max_length=128, description='城市')
    address: str = Field('', max_length=256, description='地址')
    manager: str = Field('', max_length=64, description='管理员')
    contact_tel: str = Field('', max_length=64, description='联系电话')


class GoodsOwnerViewModel(BaseModel):
    """
    货主视图模型
    
    用于货主信息的展示和返回
    """
    id: int
    goods_owner_name: str
    city: str
    address: str
    manager: str
    contact_tel: str
    creator: str
    create_time: int
    last_update_time: int
    is_valid: bool

    class Config:
        from_attributes = True
