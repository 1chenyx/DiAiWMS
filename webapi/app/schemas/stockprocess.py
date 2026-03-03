from pydantic import BaseModel, Field


class StockprocessCreate(BaseModel):
    job_code: str = Field(..., max_length=64, description='作业编号')
    job_type: bool = Field(False, description='作业类型')


class StockprocessUpdate(BaseModel):
    id: int
    job_code: str = Field(..., max_length=64, description='作业编号')
    job_type: bool = Field(False, description='作业类型')


class StockprocessViewModel(BaseModel):
    id: int
    job_code: str
    job_type: bool
    process_status: bool
    processor: str
    process_time: int
    creator: str
    create_time: int
    last_update_time: int
    tenant_id: str

    class Config:
        from_attributes = True
