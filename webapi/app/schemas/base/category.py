from typing import Optional, List
from pydantic import BaseModel, Field


class CategoryViewModel(BaseModel):
    """
    商品分类视图模型
    
    用于商品分类信息的展示和返回
    """
    id: int = Field(default=0, description="主键ID")
    category_name: str = Field(default="", max_length=100, description="分类名称")
    parent_id: int = Field(default=0, description="父分类ID")
    creator: str = Field(default="", max_length=50, description="创建人")
    create_time: int = Field(default=0, description="创建时间")
    last_update_time: int = Field(default=0, description="最后更新时间")
    is_valid: bool = Field(default=True, description="是否有效")
    tenant_id: str = Field(default="", description="租户ID")


class CategoryTreeViewModel(BaseModel):
    """
    商品分类树形视图模型
    
    用于商品分类树形结构的展示和返回
    """
    id: int = Field(default=0, description="主键ID")
    category_name: str = Field(default="", max_length=100, description="分类名称")
    parent_id: int = Field(default=0, description="父分类ID")
    creator: str = Field(default="", max_length=50, description="创建人")
    create_time: int = Field(default=0, description="创建时间")
    last_update_time: int = Field(default=0, description="最后更新时间")
    is_valid: bool = Field(default=True, description="是否有效")
    tenant_id: str = Field(default="", description="租户ID")
    children: List['CategoryTreeViewModel'] = Field(default=[], description="子分类列表")


CategoryTreeViewModel.model_rebuild()


class CategoryCreateViewModel(BaseModel):
    """
    商品分类创建视图模型
    
    用于创建新商品分类时的数据验证和序列化
    """
    category_name: str = Field(..., max_length=100, description="分类名称")
    parent_id: int = Field(default=0, description="父分类ID")
    is_valid: bool = Field(default=True, description="是否有效")


class CategoryUpdateViewModel(BaseModel):
    """
    商品分类更新视图模型
    
    用于更新商品分类信息时的数据验证和序列化
    """
    id: int = Field(..., description="分类ID")
    category_name: Optional[str] = Field(None, max_length=100, description="分类名称")
    parent_id: Optional[int] = Field(None, description="父分类ID")
    is_valid: Optional[bool] = Field(None, description="是否有效")
