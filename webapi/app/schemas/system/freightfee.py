from pydantic import BaseModel, Field


class FreightfeeCreate(BaseModel):
    carrier: str = Field(..., max_length=64, description='承运商')
    departure_city: str = Field(..., max_length=64, description='出发城市')
    arrival_city: str = Field(..., max_length=64, description='到达城市')
    price_per_weight: float = Field(0, description='每公斤价格')
    price_per_volume: float = Field(0, description='每立方米价格')
    min_payment: float = Field(0, description='最低运费')


class FreightfeeUpdate(BaseModel):
    id: int
    carrier: str = Field(..., max_length=64, description='承运商')
    departure_city: str = Field(..., max_length=64, description='出发城市')
    arrival_city: str = Field(..., max_length=64, description='到达城市')
    price_per_weight: float = Field(0, description='每公斤价格')
    price_per_volume: float = Field(0, description='每立方米价格')
    min_payment: float = Field(0, description='最低运费')
    is_valid: bool = Field(False, description='是否有效')


class FreightfeeViewModel(BaseModel):
    id: int
    carrier: str
    departure_city: str
    arrival_city: str
    price_per_weight: float
    price_per_volume: float
    min_payment: float
    creator: str
    create_time: int
    last_update_time: int
    is_valid: bool
    tenant_id: str

    class Config:
        from_attributes = True
