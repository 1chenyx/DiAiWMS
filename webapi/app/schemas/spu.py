from typing import Optional, List
from pydantic import BaseModel, Field


class SpuViewModel(BaseModel):
    """
    SPU视图模型
    
    用于SPU信息的展示和返回
    """
    id: int = Field(default=0, description="主键ID")
    spu_code: str = Field(default="", max_length=50, description="SPU编码")
    spu_name: str = Field(default="", max_length=100, description="SPU名称")
    category_id: int = Field(default=0, description="分类ID")
    spu_description: str = Field(default="", max_length=500, description="SPU描述")
    supplier_id: int = Field(default=0, description="供应商ID")
    supplier_name: str = Field(default="", max_length=100, description="供应商名称")
    brand: str = Field(default="", max_length=100, description="品牌")
    origin: str = Field(default="", max_length=100, description="产地")
    length_unit: int = Field(default=0, description="长度单位")
    volume_unit: int = Field(default=0, description="体积单位")
    weight_unit: int = Field(default=0, description="重量单位")
    creator: str = Field(default="", max_length=50, description="创建人")
    create_time: int = Field(default=0, description="创建时间")
    last_update_time: int = Field(default=0, description="最后更新时间")
    is_valid: bool = Field(default=True, description="是否有效")
    tenant_id: str = Field(default="", description="租户ID")


class SpuCreateViewModel(BaseModel):
    """
    SPU创建视图模型
    
    用于创建新SPU时的数据验证和序列化
    """
    spu_code: str = Field(..., max_length=50, description="SPU编码")
    spu_name: str = Field(..., max_length=100, description="SPU名称")
    category_id: int = Field(..., description="分类ID")
    spu_description: Optional[str] = Field(default="", max_length=500, description="SPU描述")
    supplier_id: Optional[int] = Field(default=0, description="供应商ID")
    brand: Optional[str] = Field(default="", max_length=100, description="品牌")
    origin: Optional[str] = Field(default="", max_length=100, description="产地")
    length_unit: int = Field(default=0, description="长度单位")
    volume_unit: int = Field(default=0, description="体积单位")
    weight_unit: int = Field(default=0, description="重量单位")
    is_valid: bool = Field(default=True, description="是否有效")
    skus: Optional[List['SpuSkuCreateViewModel']] = Field(default=None, description="SKU列表")


class SpuUpdateViewModel(BaseModel):
    """
    SPU更新视图模型
    
    用于更新SPU信息时的数据验证和序列化
    """
    id: int = Field(..., description="SPU ID")
    spu_code: Optional[str] = Field(None, max_length=50, description="SPU编码")
    spu_name: Optional[str] = Field(None, max_length=100, description="SPU名称")
    category_id: Optional[int] = Field(None, description="分类ID")
    spu_description: Optional[str] = Field(None, max_length=500, description="SPU描述")
    supplier_id: Optional[int] = Field(None, description="供应商ID")
    brand: Optional[str] = Field(None, max_length=100, description="品牌")
    origin: Optional[str] = Field(None, max_length=100, description="产地")
    length_unit: Optional[int] = Field(None, description="长度单位")
    volume_unit: Optional[int] = Field(None, description="体积单位")
    weight_unit: Optional[int] = Field(None, description="重量单位")
    is_valid: Optional[bool] = Field(None, description="是否有效")
    skus: Optional[List['SkuUpdateViewModel']] = Field(default=None, description="SKU列表")
    delete_sku_ids: Optional[List[int]] = Field(default=None, description="要删除的SKU ID列表")


from app.schemas.sku import SkuCreateViewModel, SkuUpdateViewModel, SpuSkuCreateViewModel
