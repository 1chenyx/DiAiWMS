import { BaseService } from './baseService'
import { http } from './api'
import type { BaseEntity, PageParams, PageResult } from '@/types/common'
import { PaginationHelper } from '@/utils/pagination'

export interface OutboundReceiptItem {
  outbound_pick_putaway_item_id: number
  spu_id: number
  sku_id: number
  qty: number
  location_id?: number
  location_name?: string
}

export interface OutboundReceiptCreate {
  outbound_pick_putaway_id: number
}

export interface OutboundReceiptUpdate {
  id: number
  remark?: string
}

export interface OutboundReceiptItemViewModel {
  id: number
  outbound_receipt_id: number
  outbound_pick_putaway_item_id: number
  spu_id: number
  sku_id: number
  spu_name: string
  sku_name: string
  sku_code: string
  qty: number
  location_id?: number
  location_name?: string
}

export interface OutboundReceiptViewModel extends BaseEntity {
  id: number
  receipt_no: string
  outbound_pick_putaway_id: number
  pick_putaway_no: string
  outbound_order_id: number
  order_no: string
  customer_id: number
  customer_name: string
  warehouse_id: number
  warehouse_name: string
  receipt_status: number
  total_qty: number
  outbound_person?: string
  outbound_time?: string
  remark?: string
  items?: OutboundReceiptItemViewModel[]
}

export interface OutboundReceiptPageParams extends PageParams {
  receipt_no?: string
  receipt_status?: number
  order_no?: string
}

class OutboundReceiptService extends BaseService<OutboundReceiptViewModel, OutboundReceiptCreate, OutboundReceiptUpdate> {
  constructor() {
    super({
      basePath: '/outbound-receipt',
      usePostForList: true,
      usePostForDelete: true
    })
  }

  getPage(params: OutboundReceiptPageParams): Promise<PageResult<OutboundReceiptViewModel>> {
    const normalizedParams = PaginationHelper.normalizeParams(params)
    return http.post('/outbound-receipt/list', null, { params: normalizedParams })
  }

  completeOutbound(id: number, outbound_person: string): Promise<void> {
    return http.post('/outbound-receipt/complete-outbound', null, {
      params: { id, outbound_person }
    })
  }
}

export const outboundReceiptService = new OutboundReceiptService()
export default outboundReceiptService
