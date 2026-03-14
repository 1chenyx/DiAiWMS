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
