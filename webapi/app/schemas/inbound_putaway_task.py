from typing import Optional
from pydantic import BaseModel, Field


class InboundPutawayTaskCreate(BaseModel):
    pick_putaway_item_id: int = Field(..., description='拣货上架单明细ID')
    putaway_qty: int = Field(..., gt=0, description='上架数量')
    goods_location_id: int = Field(..., gt=0, description='上架库位ID')
    warehouse_id: int = Field(..., gt=0, description='仓库ID')
    warehouse_area_id: int = Field(..., gt=0, description='库区ID')


class InboundPutawayTaskViewModel(BaseModel):
    id: int
    pick_putaway_item_id: int
    putaway_qty: int
    weight: float
    volume: float
    price: float
    expiry_date: int
    goods_location_id: int
    warehouse_id: int
    warehouse_name: Optional[str] = None
    warehouse_area_id: int
    warehouse_area_name: Optional[str] = None
    warehouse_location_name: Optional[str] = None
    putaway_person_id: int
    putaway_person: str
    putaway_time: int
    series_number: str
    tenant_id: str
    create_time: int
