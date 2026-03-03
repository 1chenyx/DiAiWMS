from pydantic import BaseModel, Field


class UserRoleCreate(BaseModel):
    role_name: str = Field(..., max_length=64, description='角色名称')


class UserRoleUpdate(BaseModel):
    id: int
    role_name: str = Field(..., max_length=64, description='角色名称')
    is_valid: bool = Field(True, description='是否有效')


class UserRoleViewModel(BaseModel):
    id: int
    role_name: str
    tenant_id: str
    is_valid: bool
    create_time: int
    last_update_time: int

    class Config:
        from_attributes = True
