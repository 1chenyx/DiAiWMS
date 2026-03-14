import { BaseService } from './baseService'
import { http } from './api'
import type { BaseEntity, PageParams, PageResult } from '@/types/common'
import { PaginationHelper } from '@/utils/pagination'

export interface InboundReceiptCreate {
  order_id?: number
  inbound_pick_putaway_id?: number
  inbound_person: string
  remark?: string
}

export interface InboundReceiptUpdate {
  id: number
  remark?: string
}

export interface InboundReceiptItemViewModel {
  id: number
  receipt_id: number
  pick_putaway_item_id: number
  spu_id: number
  spu_code?: string
  spu_name?: string
  sku_id: number
  sku_code?: string
  sku_name?: string
  qty: number
  actual_qty: number
  weight: number
  actual_weight: number
  volume: number
  actual_volume: number
  price: number
  expiry_date: number
  goods_location_id: number
  goods_location_code?: string
  series_number: string
  batch_no: string
  production_date: number
  tenant_id: string
}

export interface InboundReceiptViewModel extends BaseEntity {
  id: number
  receipt_no: string
  order_id: number
  order_no: string
  receipt_status: number
  inbound_person: string
  inbound_time?: string
  pick_putaway_no?: string
  supplier_name?: string
  warehouse_name?: string
  total_qty?: number
  items?: InboundReceiptItemViewModel[]
  remark?: string
}

export interface InboundReceiptPageParams extends PageParams {
  receipt_no?: string
  receipt_status?: number
  order_no?: string
}

class InboundReceiptService extends BaseService<InboundReceiptViewModel, InboundReceiptCreate, InboundReceiptUpdate> {
  constructor() {
    super({
      basePath: '/inbound-receipt',
      usePostForList: true,
      usePostForDelete: true
    })
  }

  getPage(params: InboundReceiptPageParams): Promise<PageResult<InboundReceiptViewModel>> {
    const normalizedParams = PaginationHelper.normalizeParams(params)
    return http.post('/inbound-receipt/list', null, { params: normalizedParams })
  }

  completeInbound(id: number, inbound_person: string): Promise<void> {
    return http.post('/inbound-receipt/complete-inbound', null, {
      params: { id, inbound_person }
    })
  }
}

export const inboundReceiptService = new InboundReceiptService()
export default inboundReceiptService
