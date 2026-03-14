from pydantic import BaseModel, Field


class StockfreezeCreate(BaseModel):
    job_code: str = Field(..., max_length=64, description='作业编号')
    job_type: bool = Field(False, description='作业类型')
    sku_id: int = Field(..., description='SKU ID')
    goods_owner_id: int = Field(0, description='货主ID')
    goods_location_id: int = Field(0, description='货位ID')
    series_number: str = Field('', max_length=100, description='序列号')


class StockfreezeUpdate(BaseModel):
    id: int
    job_code: str = Field(..., max_length=64, description='作业编号')
    job_type: bool = Field(False, description='作业类型')
    sku_id: int = Field(..., description='SKU ID')
    goods_owner_id: int = Field(0, description='货主ID')
    goods_location_id: int = Field(0, description='货位ID')
    series_number: str = Field('', max_length=100, description='序列号')


class StockfreezeViewModel(BaseModel):
    id: int
    job_code: str
    job_type: bool
    sku_id: int
    goods_owner_id: int
    goods_location_id: int
    handler: str
    handle_time: int
    last_update_time: int
    tenant_id: str
    series_number: str
    sku_code: str
    sku_name: str
    location_code: str

    class Config:
        from_attributes = True
