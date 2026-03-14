from pydantic import BaseModel, Field


class MenuCreate(BaseModel):
    menu_name: str = Field(..., max_length=64, description='菜单名称')
    menu_type: str = Field(..., max_length=32, description='菜单类型')
    parent_id: int = Field(None, description='父菜单ID')
    menu_path: str = Field(None, max_length=255, description='菜单路径')
    menu_icon: str = Field(None, max_length=64, description='菜单图标')
    menu_sort: int = Field(0, description='菜单排序')
    is_valid: bool = Field(True, description='是否有效')


class MenuUpdate(BaseModel):
    id: int
    menu_name: str = Field(..., max_length=64, description='菜单名称')
    menu_type: str = Field(..., max_length=32, description='菜单类型')
    parent_id: int = Field(None, description='父菜单ID')
    menu_path: str = Field(None, max_length=255, description='菜单路径')
    menu_icon: str = Field(None, max_length=64, description='菜单图标')
    menu_sort: int = Field(0, description='菜单排序')
    is_valid: bool = Field(True, description='是否有效')


class MenuViewModel(BaseModel):
    id: int
    menu_name: str
    menu_type: str
    parent_id: int
    menu_path: str
    menu_icon: str
    menu_sort: int
    is_valid: bool
    create_time: int
    last_update_time: int

    class Config:
        from_attributes = True
