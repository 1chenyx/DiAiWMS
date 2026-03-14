from pydantic import BaseModel, Field


class TenantCreateViewModel(BaseModel):
    """
    租户创建视图模型
    
    用于创建新租户时的数据验证和序列化
    """
    tenant_name: str = Field(..., max_length=100, description='租户名称')
    tenant_code: str = Field(..., max_length=50, description='租户编码')
    contact_person: str = Field(..., max_length=50, description='联系人')
    contact_phone: str = Field(..., max_length=20, description='联系电话')
    contact_email: str = Field(..., max_length=100, description='联系邮箱')
    address: str = Field(..., max_length=256, description='地址')
    description: str = Field(..., max_length=500, description='描述')


class TenantUpdateViewModel(BaseModel):
    """
    租户更新视图模型
    
    用于更新租户信息时的数据验证和序列化
    """
    id: int
    tenant_name: str = Field(..., max_length=100, description='租户名称')
    tenant_code: str = Field(..., max_length=50, description='租户编码')
    contact_person: str = Field(..., max_length=50, description='联系人')
    contact_phone: str = Field(..., max_length=20, description='联系电话')
    contact_email: str = Field(..., max_length=100, description='联系邮箱')
    address: str = Field(..., max_length=256, description='地址')
    description: str = Field(..., max_length=500, description='描述')
    is_valid: bool = Field(True, description='是否有效')


class TenantViewModel(BaseModel):
    """
    租户视图模型
    
    用于租户信息的展示和返回
    """
    id: int
    tenant_name: str
    tenant_code: str
    contact_person: str
    contact_phone: str
    contact_email: str
    address: str
    description: str
    is_valid: bool
    creator: str
    create_time: int
    last_update_time: int

    class Config:
        from_attributes = True
