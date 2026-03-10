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
  inbound_receipt_id: number
  sku_id: number
  sku_code: string
  sku_name: string
  qty: number
  batch_no?: string
  production_date?: number
  remark?: string
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
