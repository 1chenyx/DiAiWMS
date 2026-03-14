from pydantic import BaseModel, Field


class ActionLogCreate(BaseModel):
    vue_path: str = Field(..., max_length=255, description='Vue路径')
    user_name: str = Field(..., max_length=64, description='用户名')
    action_content: str = Field(..., max_length=1000, description='操作内容')


class ActionLogUpdate(BaseModel):
    id: int
    vue_path: str = Field(..., max_length=255, description='Vue路径')
    user_name: str = Field(..., max_length=64, description='用户名')
    action_content: str = Field(..., max_length=1000, description='操作内容')


class ActionLogViewModel(BaseModel):
    id: int
    vue_path: str
    user_name: str
    action_content: str
    action_time: int
    tenant_id: str

    class Config:
        from_attributes = True
