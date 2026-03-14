from pydantic import BaseModel, Field


class StockadjustCreate(BaseModel):
    job_code: str = Field(..., max_length=64, description='作业编号')
    sku_id: int = Field(..., description='SKU ID')
    goods_owner_id: int = Field(0, description='货主ID')
    goods_location_id: int = Field(0, description='货位ID')
    qty: int = Field(..., description='数量')
    job_type: int = Field(0, description='作业类型')
    source_table_id: int = Field(0, description='来源表ID')
    series_number: str = Field('', max_length=100, description='序列号')
    expiry_date: int = Field(0, description='过期日期')
    price: float = Field(0, description='价格')
    putaway_date: int = Field(0, description='上架日期')


class StockadjustUpdate(BaseModel):
    id: int
    job_code: str = Field(..., max_length=64, description='作业编号')
    sku_id: int = Field(..., description='SKU ID')
    goods_owner_id: int = Field(0, description='货主ID')
    goods_location_id: int = Field(0, description='货位ID')
    qty: int = Field(..., description='数量')
    job_type: int = Field(0, description='作业类型')
    source_table_id: int = Field(0, description='来源表ID')
    series_number: str = Field('', max_length=100, description='序列号')
    expiry_date: int = Field(0, description='过期日期')
    price: float = Field(0, description='价格')
    putaway_date: int = Field(0, description='上架日期')


class StockadjustViewModel(BaseModel):
    id: int
    job_code: str
    sku_id: int
    goods_owner_id: int
    goods_location_id: int
    qty: int
    creator: str
    create_time: int
    last_update_time: int
    tenant_id: str
    is_update_stock: bool
    job_type: int
    source_table_id: int
    series_number: str
    expiry_date: int
    price: float
    putaway_date: int
    sku_code: str
    sku_name: str
    location_code: str

    class Config:
        from_attributes = True
