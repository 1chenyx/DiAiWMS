from pydantic import BaseModel, Field


class StocktakingCreate(BaseModel):
    job_code: str = Field(..., max_length=64, description='作业编号')
    sku_id: int = Field(..., description='SKU ID')
    goods_owner_id: int = Field(0, description='货主ID')
    goods_location_id: int = Field(0, description='货位ID')
    series_number: str = Field('', max_length=100, description='序列号')
    expiry_date: int = Field(0, description='过期日期')
    price: float = Field(0, description='价格')
    putaway_date: int = Field(0, description='上架日期')
    book_qty: int = Field(0, description='账面数量')


class StocktakingUpdate(BaseModel):
    id: int
    job_code: str = Field(..., max_length=64, description='作业编号')
    sku_id: int = Field(..., description='SKU ID')
    goods_owner_id: int = Field(0, description='货主ID')
    goods_location_id: int = Field(0, description='货位ID')
    series_number: str = Field('', max_length=100, description='序列号')
    expiry_date: int = Field(0, description='过期日期')
    price: float = Field(0, description='价格')
    putaway_date: int = Field(0, description='上架日期')
    book_qty: int = Field(0, description='账面数量')
    counted_qty: int = Field(0, description='盘点数量')


class StocktakingViewModel(BaseModel):
    id: int
    job_code: str
    job_status: bool
    sku_id: int
    goods_owner_id: int
    goods_location_id: int
    series_number: str
    expiry_date: int
    price: float
    putaway_date: int
    book_qty: int
    counted_qty: int
    difference_qty: int
    creator: str
    create_time: int
    last_update_time: int
    tenant_id: str
    handler: str
    handle_time: int
    sku_code: str
    sku_name: str
    location_code: str

    class Config:
        from_attributes = True
