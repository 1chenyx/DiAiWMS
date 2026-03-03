from typing import Optional
from pydantic import BaseModel


class CurrentUser(BaseModel):
    """
    当前用户模型
    
    用于存储当前登录用户的信息
    """
    user_id: int = 0
    user_num: str = ""
    user_name: str = ""
    user_role: str = ""
    tenant_id: str = ""
    userrole_id: int = 0
    is_authenticated: bool = False
