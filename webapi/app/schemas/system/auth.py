from typing import Optional
from pydantic import BaseModel, Field


class LoginInputViewModel(BaseModel):
    """
    登录输入视图模型
    
    用于用户登录时的请求数据验证
    """
    tenant_code: str = Field(..., max_length=50, description="租户编号")
    user_name: str = Field(..., max_length=128, description="用户名")
    password: str = Field(..., max_length=64, description="密码")


class EnterpriseRegisterInputViewModel(BaseModel):
    """
    企业注册输入视图模型
    
    用于企业自主注册时的请求数据验证
    """
    tenant_name: str = Field(..., max_length=100, description="企业名称")
    tenant_code: str = Field(..., max_length=50, description="企业编码")
    contact_person: str = Field(..., max_length=50, description="联系人")
    contact_phone: str = Field(..., max_length=20, description="联系电话")
    contact_email: str = Field(..., max_length=100, description="联系邮箱")
    address: str = Field("", max_length=256, description="地址")
    description: str = Field("", max_length=500, description="描述")
    admin_user_name: str = Field(..., max_length=100, description="管理员用户名")
    admin_password: str = Field(..., max_length=64, description="管理员密码")
    admin_contact_tel: str = Field("", max_length=20, description="管理员联系电话")
    admin_email: str = Field("", max_length=100, description="管理员邮箱")


class EnterpriseRegisterOutputViewModel(BaseModel):
    """
    企业注册输出视图模型
    
    用于返回企业注册成功后的信息
    """
    tenant_id: str = Field(description="租户ID")
    tenant_name: str = Field(description="企业名称")
    tenant_code: str = Field(description="企业编码")
    user_id: int = Field(description="管理员用户ID")
    user_name: str = Field(description="管理员用户名")


class LoginOutputViewModel(BaseModel):
    """
    登录输出视图模型
    
    用于返回登录成功后的用户信息和令牌
    """
    user_num: str = Field(description="用户编号")
    user_name: str = Field(description="用户名")
    user_id: int = Field(description="用户ID")
    user_role: str = Field(description="用户角色")
    userrole_id: int = Field(description="用户角色ID")
    tenant_id: str = Field(description="租户ID")
    expire: int = Field(description="过期时间")
    access_token: str = Field(description="访问令牌")
    refresh_token: str = Field(description="刷新令牌")


class RefreshTokenInputViewModel(BaseModel):
    """
    刷新令牌输入视图模型
    
    用于刷新访问令牌时的请求数据验证
    """
    access_token: str = Field(..., description="访问令牌")
    refresh_token: str = Field(..., description="刷新令牌")


class RefreshTokenOutputViewModel(BaseModel):
    """
    刷新令牌输出视图模型
    
    用于返回刷新后的访问令牌和过期时间
    """
    access_token: str = Field(description="访问令牌")
    expire: int = Field(description="过期时间")
