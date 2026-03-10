import { BaseService } from './baseService'
import { http } from './api'
import type { BaseEntity, PageParams, PageResult } from '@/types/common'
import { PaginationHelper } from '@/utils/pagination'

export interface OutboundReceiptCreate {
  order_id?: number
  outbound_pick_putaway_id?: number
  outbound_person?: string
  remark?: string
}

export interface OutboundReceiptUpdate {
  id: number
  remark?: string
}

export interface OutboundReceiptViewModel extends BaseEntity {
  id: number
  receipt_no: string
  order_id: number
  order_no: string
  receipt_status: number
  outbound_person: string
  remark?: string
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
