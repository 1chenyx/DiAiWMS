from pydantic import BaseModel, Field


class UserCreateViewModel(BaseModel):
    """
    用户创建视图模型
    
    用于创建新用户时的数据验证和序列化
    """
    user_num: str = Field(..., max_length=64, description='用户编号')
    user_name: str = Field(..., max_length=64, description='用户名')
    user_role: str = Field(..., max_length=64, description='用户角色')
    password: str = Field(None, max_length=128, description='密码')


class UserUpdateViewModel(BaseModel):
    """
    用户更新视图模型
    
    用于更新用户信息时的数据验证和序列化
    """
    id: int
    user_num: str = Field(..., max_length=64, description='用户编号')
    user_name: str = Field(..., max_length=64, description='用户名')
    user_role: str = Field(..., max_length=64, description='用户角色')
    password: str = Field(None, max_length=128, description='密码')
    is_valid: bool = Field(True, description='是否有效')


class UserViewModel(BaseModel):
    """
    用户视图模型
    
    用于用户信息的展示和返回
    """
    id: int
    user_num: str
    user_name: str
    user_role: str
    tenant_id: str
    is_valid: bool
    create_time: int
    last_update_time: int
    role_name: str

    class Config:
        from_attributes = True
