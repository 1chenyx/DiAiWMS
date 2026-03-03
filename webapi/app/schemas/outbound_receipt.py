from typing import Optional, List
from pydantic import BaseModel, Field


class OutboundReceiptItemCreate(BaseModel):
    pick_putaway_item_id: int = Field(..., description='拣货上架单明细ID')
    spu_id: int = Field(..., description='SPU ID')
    sku_id: int = Field(..., description='SKU ID')
    qty: int = Field(..., gt=0, description='数量')
    actual_qty: int = Field(..., ge=0, description='实际数量')
    weight: float = Field(..., ge=0, description='重量')
    actual_weight: float = Field(..., ge=0, description='实际重量')
    volume: float = Field(..., ge=0, description='体积')
    actual_volume: float = Field(..., ge=0, description='实际体积')
    price: float = Field(..., ge=0, description='价格')
    expiry_date: int = Field(default=0, description='过期日期')
    goods_location_id: int = Field(..., description='出库库位ID')
    series_number: str = Field(default='', max_length=100, description='序列号')


class OutboundReceiptCreate(BaseModel):
    pick_putaway_id: int = Field(..., description='拣货上架单ID')
    package_no: Optional[str] = Field(None, max_length=64, description='打包单号')
    package_person: Optional[str] = Field(None, max_length=64, description='打包人')
    weighing_no: Optional[str] = Field(None, max_length=64, description='称重单号')
    weighing_person: Optional[str] = Field(None, max_length=64, description='称重人')
    weighing_weight: Optional[float] = Field(None, ge=0, description='称重重量')
    waybill_no: Optional[str] = Field(None, max_length=64, description='运单号')
    carrier: Optional[str] = Field(None, max_length=128, description='承运商')
    freightfee: Optional[float] = Field(None, ge=0, description='运费')
    remark: Optional[str] = Field(None, max_length=512, description='备注')


class OutboundReceiptUpdate(BaseModel):
    id: int = Field(..., description='出库单ID')
    package_no: Optional[str] = Field(None, max_length=64, description='打包单号')
    package_person: Optional[str] = Field(None, max_length=64, description='打包人')
    weighing_no: Optional[str] = Field(None, max_length=64, description='称重单号')
    weighing_person: Optional[str] = Field(None, max_length=64, description='称重人')
    weighing_weight: Optional[float] = Field(None, ge=0, description='称重重量')
    waybill_no: Optional[str] = Field(None, max_length=64, description='运单号')
    carrier: Optional[str] = Field(None, max_length=128, description='承运商')
    freightfee: Optional[float] = Field(None, ge=0, description='运费')
    remark: Optional[str] = Field(None, max_length=512, description='备注')


class OutboundReceiptViewModel(BaseModel):
    id: int
    receipt_no: str
    receipt_status: int
    pick_putaway_id: int
    order_id: int
    order_no: str
    customer_id: int
    customer_name: str
    warehouse_id: int
    warehouse_name: Optional[str] = None
    goods_owner_id: int
    goods_owner_name: str
    total_qty: int
    actual_qty: int
    total_weight: float
    actual_weight: float
    total_volume: float
    actual_volume: float
    package_no: str
    package_person: str
    package_time: int
    weighing_no: str
    weighing_person: str
    weighing_weight: float
    waybill_no: str
    carrier: str
    freightfee: float
    outbound_time: int
    outbound_person: str
    remark: Optional[str]
    creator: str
    create_time: int
    last_update_time: int
    tenant_id: str
    items: Optional[List['OutboundReceiptItemViewModel']] = None


class OutboundReceiptItemViewModel(BaseModel):
    id: int
    receipt_id: int
    pick_putaway_item_id: int
    spu_id: int
    spu_code: Optional[str] = None
    spu_name: Optional[str] = None
    sku_id: int
    sku_code: Optional[str] = None
    sku_name: Optional[str] = None
    qty: int
    actual_qty: int
    weight: float
    actual_weight: float
    volume: float
    actual_volume: float
    price: float
    expiry_date: int
    goods_location_id: int
    goods_location_code: Optional[str] = None
    series_number: str
    tenant_id: str


class OutboundReceiptPageParams(BaseModel):
    page_index: int = Field(default=1, ge=1, description='页码')
    page_size: int = Field(default=10, ge=1, le=100, description='每页数量')
    receipt_no: Optional[str] = Field(None, description='出库单号')
    receipt_status: Optional[int] = Field(None, description='出库单状态')
    order_no: Optional[str] = Field(None, description='出库订单号')


class OutboundReceiptPageResult(BaseModel):
    rows: List[OutboundReceiptViewModel]
    totals: int
