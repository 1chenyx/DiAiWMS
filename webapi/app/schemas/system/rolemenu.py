from pydantic import BaseModel, Field


class RolemenuCreate(BaseModel):
    userrole_id: int = Field(..., description='用户角色ID')
    menu_id: int = Field(..., description='菜单ID')
    authority: int = Field(1, description='权限')
    menu_actions_authority: str = Field('[]', max_length=1000, description='菜单操作权限')


class RolemenuUpdate(BaseModel):
    id: int
    userrole_id: int = Field(..., description='用户角色ID')
    menu_id: int = Field(..., description='菜单ID')
    authority: int = Field(1, description='权限')
    menu_actions_authority: str = Field('[]', max_length=1000, description='菜单操作权限')


class RolemenuViewModel(BaseModel):
    id: int
    userrole_id: int
    menu_id: int
    authority: int
    create_time: int
    last_update_time: int
    tenant_id: str
    menu_actions_authority: str
    role_name: str

    class Config:
        from_attributes = True
