from typing import Optional, List
from pydantic import BaseModel, Field


class OutboundPickPutawayItemCreate(BaseModel):
    order_item_id: int = Field(..., description='出库订单明细ID')
    spu_id: int = Field(..., description='SPU ID')
    sku_id: int = Field(..., description='SKU ID')
    qty: int = Field(..., gt=0, description='拣货数量')
    weight: float = Field(..., ge=0, description='重量')
    volume: float = Field(..., ge=0, description='体积')
    price: float = Field(..., ge=0, description='价格')
    expiry_date: int = Field(default=0, description='过期日期')
    goods_location_id: int = Field(..., description='拣货库位ID')
    series_number: str = Field(default='', max_length=100, description='序列号')


class OutboundPickPutawayCreate(BaseModel):
    order_id: int = Field(..., description='出库订单ID')
    remark: Optional[str] = Field(None, max_length=512, description='备注')


class OutboundPickPutawayUpdate(BaseModel):
    id: int = Field(..., description='拣货上架单ID')
    pick_putaway_status: Optional[int] = Field(None, description='拣货上架状态')
    picker_id: Optional[int] = Field(None, description='拣货人ID')
    picker: Optional[str] = Field(None, max_length=64, description='拣货人')
    remark: Optional[str] = Field(None, max_length=512, description='备注')


class OutboundPickPutawayItemUpdate(BaseModel):
    id: int = Field(..., description='拣货上架单明细ID')
    picked_qty: int = Field(..., ge=0, description='已拣货数量')
    picker_id: int = Field(..., description='拣货人ID')
    picker: str = Field(..., max_length=64, description='拣货人')
    pick_time: int = Field(..., description='拣货时间')


class OutboundPickPutawayViewModel(BaseModel):
    id: int
    pick_putaway_no: str
    pick_putaway_status: int
    order_id: int
    order_no: str
    customer_id: int
    customer_name: str
    warehouse_id: int
    warehouse_name: Optional[str] = None
    goods_owner_id: int
    goods_owner_name: str
    total_qty: int
    picked_qty: int
    total_weight: float
    total_volume: float
    picker_id: int
    picker: str
    pick_start_time: int
    pick_end_time: int
    remark: Optional[str]
    creator: str
    create_time: int
    last_update_time: int
    tenant_id: str
    items: Optional[List['OutboundPickPutawayItemViewModel']] = None


class OutboundPickPutawayItemViewModel(BaseModel):
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
    picked_qty: int
    weight: float
    volume: float
    price: float
    expiry_date: int
    goods_location_id: int
    goods_location_code: Optional[str] = None
    picker_id: int
    picker: str
    pick_time: int
    series_number: str
    tenant_id: str


class OutboundPickPutawayPageParams(BaseModel):
    page_index: int = Field(default=1, ge=1, description='页码')
    page_size: int = Field(default=10, ge=1, le=100, description='每页数量')
    pick_putaway_no: Optional[str] = Field(None, description='拣货上架单号')
    pick_putaway_status: Optional[int] = Field(None, description='拣货上架状态')
    order_no: Optional[str] = Field(None, description='出库订单号')


class OutboundPickPutawayPageResult(BaseModel):
    rows: List[OutboundPickPutawayViewModel]
    totals: int
