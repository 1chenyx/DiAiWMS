from typing import Optional, List
from pydantic import BaseModel, Field


class InboundOrderItemCreate(BaseModel):
    spu_id: int = Field(..., description='SPU ID')
    sku_id: int = Field(..., description='SKU ID')
    qty: int = Field(..., gt=0, description='数量')
    weight: float = Field(..., ge=0, description='重量')
    volume: float = Field(..., ge=0, description='体积')
    price: Optional[float] = Field(None, ge=0, description='价格')
    expiry_date: int = Field(default=0, description='过期日期')
    batch_no: Optional[str] = Field(None, max_length=64, description='批次号')
    production_date: Optional[int] = Field(None, description='生产日期')


class InboundOrderCreate(BaseModel):
    supplier_id: int = Field(..., description='供应商ID')
    supplier_name: Optional[str] = Field(None, max_length=128, description='供应商名称')
    warehouse_id: int = Field(..., description='仓库ID')
    goods_owner_id: int = Field(default=0, description='货主ID')
    goods_owner_name: Optional[str] = Field(None, max_length=128, description='货主名称')
    estimated_arrival_time: Optional[int] = Field(None, description='预计到货时间')
    remark: Optional[str] = Field(None, max_length=512, description='备注')
    items: List[InboundOrderItemCreate] = Field(..., min_items=1, description='订单明细')


class InboundOrderUpdate(BaseModel):
    id: int = Field(..., description='入库订单ID')
    supplier_id: Optional[int] = Field(None, description='供应商ID')
    supplier_name: Optional[str] = Field(None, max_length=128, description='供应商名称')
    warehouse_id: Optional[int] = Field(None, description='仓库ID')
    goods_owner_id: Optional[int] = Field(None, description='货主ID')
    goods_owner_name: Optional[str] = Field(None, max_length=128, description='货主名称')
    estimated_arrival_time: Optional[int] = Field(None, description='预计到货时间')
    remark: Optional[str] = Field(None, max_length=512, description='备注')


class InboundOrderViewModel(BaseModel):
    id: int
    order_no: str
    order_status: int
    supplier_id: int
    supplier_name: str
    warehouse_id: int
    warehouse_name: Optional[str] = None
    goods_owner_id: int
    goods_owner_name: str
    total_qty: int
    total_weight: float
    total_volume: float
    estimated_arrival_time: int
    remark: Optional[str]
    creator: str
    create_time: int
    last_update_time: int
    tenant_id: str
    items: Optional[List['InboundOrderItemViewModel']] = None


class InboundOrderItemViewModel(BaseModel):
    id: int
    order_id: int
    spu_id: int
    spu_code: Optional[str] = None
    spu_name: Optional[str] = None
    sku_id: int
    sku_code: Optional[str] = None
    sku_name: Optional[str] = None
    qty: int
    weight: float
    volume: float
    price: float
    expiry_date: int
    tenant_id: str


class InboundOrderPageParams(BaseModel):
    page_index: int = Field(default=1, ge=1, description='页码')
    page_size: int = Field(default=10, ge=1, le=100, description='每页数量')
    order_no: Optional[str] = Field(None, description='入库订单号')
    order_status: Optional[int] = Field(None, description='订单状态')
    supplier_id: Optional[int] = Field(None, description='供应商ID')


class InboundOrderPageResult(BaseModel):
    rows: List[InboundOrderViewModel]
    totals: int
