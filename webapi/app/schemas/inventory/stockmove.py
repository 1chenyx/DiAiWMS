from pydantic import BaseModel, Field


class StockmoveCreate(BaseModel):
    job_code: str = Field(..., max_length=64, description='作业编号')
    sku_id: int = Field(..., description='SKU ID')
    orig_goods_location_id: int = Field(0, description='原货位ID')
    dest_googs_location_id: int = Field(0, description='目标货位ID')
    qty: int = Field(..., description='数量')
    goods_owner_id: int = Field(0, description='货主ID')
    series_number: str = Field('', max_length=100, description='序列号')
    expiry_date: int = Field(0, description='过期日期')
    price: float = Field(0, description='价格')
    putaway_date: int = Field(0, description='上架日期')


class StockmoveUpdate(BaseModel):
    id: int
    job_code: str = Field(..., max_length=64, description='作业编号')
    sku_id: int = Field(..., description='SKU ID')
    orig_goods_location_id: int = Field(0, description='原货位ID')
    dest_googs_location_id: int = Field(0, description='目标货位ID')
    qty: int = Field(..., description='数量')
    goods_owner_id: int = Field(0, description='货主ID')
    series_number: str = Field('', max_length=100, description='序列号')
    expiry_date: int = Field(0, description='过期日期')
    price: float = Field(0, description='价格')
    putaway_date: int = Field(0, description='上架日期')


class StockmoveViewModel(BaseModel):
    id: int
    job_code: str
    move_status: int
    sku_id: int
    orig_goods_location_id: int
    dest_googs_location_id: int
    qty: int
    goods_owner_id: int
    handler: str
    handle_time: int
    creator: str
    create_time: int
    last_update_time: int
    tenant_id: str
    series_number: str
    expiry_date: int
    price: float
    putaway_date: int
    sku_code: str
    sku_name: str
    orig_location_code: str

    class Config:
        from_attributes = True
