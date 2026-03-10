from typing import Optional, List
from pydantic import BaseModel, Field


class InboundPickPutawayItemCreate(BaseModel):
    order_item_id: int = Field(..., description='入库订单明细ID')
    spu_id: int = Field(..., description='SPU ID')
    sku_id: int = Field(..., description='SKU ID')
    qty: int = Field(..., gt=0, description='上架数量')
    weight: float = Field(..., ge=0, description='重量')
    volume: float = Field(..., ge=0, description='体积')
    price: float = Field(..., ge=0, description='价格')
    expiry_date: int = Field(default=0, description='过期日期')
    goods_location_id: int = Field(..., description='上架库位ID')
    series_number: str = Field(default='', max_length=100, description='序列号')


class InboundPickPutawayCreate(BaseModel):
    inbound_order_ids: List[int] = Field(..., min_items=1, description='入库订单ID列表')
    remark: Optional[str] = Field(None, max_length=512, description='备注')


class InboundPickPutawayUpdate(BaseModel):
    id: int = Field(..., description='拣货上架单ID')
    pick_putaway_status: Optional[int] = Field(None, description='拣货上架状态')
    putaway_person_id: Optional[int] = Field(None, description='上架人ID')
    putaway_person: Optional[str] = Field(None, max_length=64, description='上架人')
    remark: Optional[str] = Field(None, max_length=512, description='备注')


class InboundPickPutawayItemUpdate(BaseModel):
    id: int = Field(..., description='拣货上架单明细ID')
    putaway_qty: int = Field(..., ge=0, description='已上架数量')
    putaway_person_id: int = Field(..., description='上架人ID')
    putaway_person: str = Field(..., max_length=64, description='上架人')
    putaway_time: int = Field(..., description='上架时间')
    warehouse_id: int = Field(..., gt=0, description='仓库ID')
    warehouse_area_id: int = Field(..., gt=0, description='库区ID')
    goods_location_id: int = Field(..., gt=0, description='库位ID')


class InboundPickPutawayItemSelectLocation(BaseModel):
    id: int = Field(..., description='拣货上架单明细ID')
    goods_location_id: int = Field(..., gt=0, description='上架库位ID')


class InboundPickPutawayViewModel(BaseModel):
    id: int
    pick_putaway_no: str
    pick_putaway_status: int
    order_id: int
    order_no: str
    supplier_id: int
    supplier_name: str
    warehouse_id: int
    warehouse_name: Optional[str] = None
    goods_owner_id: int
    goods_owner_name: str
    total_qty: int
    putaway_qty: int
    total_weight: float
    total_volume: float
    putaway_person_id: int
    putaway_person: str
    putaway_start_time: int
    putaway_end_time: int
    remark: Optional[str]
    creator: str
    create_time: int
    last_update_time: int
    tenant_id: str
    items: Optional[List['InboundPickPutawayItemViewModel']] = None


class InboundPickPutawayItemViewModel(BaseModel):
    id: int
    pick_putaway_id: int
    order_item_id: int
    spu_id: int
    spu_code: Optional[str] = None
    spu_name: Optional[str] = None
    sku_id: int
    sku_code: Optional[str] = None
    sku_name: Optional[str] = None
    qty: int
    putaway_qty: int
    weight: float
    volume: float
    price: float
    expiry_date: int
    batch_no: str
    production_date: int
    goods_location_id: int
    goods_location_code: Optional[str] = None
    putaway_person_id: int
    putaway_person: str
    putaway_time: int
    series_number: str
    tenant_id: str


class InboundPickPutawayPageParams(BaseModel):
    page_index: int = Field(default=1, ge=1, description='页码')
    page_size: int = Field(default=10, ge=1, le=100, description='每页数量')
    pick_putaway_no: Optional[str] = Field(None, description='拣货上架单号')
    pick_putaway_status: Optional[int] = Field(None, description='拣货上架状态')
    order_no: Optional[str] = Field(None, description='入库订单号')


class InboundPickPutawayPageResult(BaseModel):
    rows: List[InboundPickPutawayViewModel]
    totals: int
