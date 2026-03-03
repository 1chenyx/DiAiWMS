import { BaseService } from './baseService'
import { http } from './api'
import type { BaseEntity, PageParams, PageResult } from '@/types/common'
import { PaginationHelper } from '@/utils/pagination'

export interface InboundReceiptItem {
  inbound_pick_putaway_item_id: number
  spu_id: number
  sku_id: number
  qty: number
  location_id?: number
  location_name?: string
}

export interface InboundReceiptCreate {
  inbound_pick_putaway_id: number
}

export interface InboundReceiptUpdate {
  id: number
  remark?: string
}

export interface InboundReceiptItemViewModel {
  id: number
  inbound_receipt_id: number
  inbound_pick_putaway_item_id: number
  spu_id: number
  sku_id: number
  spu_name: string
  sku_name: string
  sku_code: string
  qty: number
  location_id?: number
  location_name?: string
}

export interface InboundReceiptViewModel extends BaseEntity {
  id: number
  receipt_no: string
  inbound_pick_putaway_id: number
  pick_putaway_no: string
  inbound_order_id: number
  order_no: string
  supplier_id: number
  supplier_name: string
  warehouse_id: number
  warehouse_name: string
  receipt_status: number
  total_qty: number
  inbound_person?: string
  inbound_time?: string
  remark?: string
  items?: InboundReceiptItemViewModel[]
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
