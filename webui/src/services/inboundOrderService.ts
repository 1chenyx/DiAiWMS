import { BaseService } from './baseService'
import { http } from './api'
import type { BaseEntity, PageParams, PageResult } from '@/types/common'
import { PaginationHelper } from '@/utils/pagination'

export interface InboundOrderItem {
  spu_id: number
  sku_id: number
  qty: number
  weight?: number
  volume?: number
}

export interface InboundOrderCreate {
  supplier_id: number
  warehouse_id: number
  remark?: string
  items: InboundOrderItem[]
}

export interface InboundOrderUpdate {
  id: number
  supplier_id?: number
  warehouse_id?: number
  remark?: string
  items?: InboundOrderItem[]
}

export interface InboundOrderItemViewModel {
  id: number
  inbound_order_id: number
  spu_id: number
  sku_id: number
  spu_name: string
  sku_name: string
  sku_code: string
  qty: number
  weight?: number
  volume?: number
}

export interface InboundOrderViewModel extends BaseEntity {
  id: number
  order_no: string
  supplier_id: number
  supplier_name: string
  warehouse_id: number
  warehouse_name: string
  order_status: number
  total_qty: number
  total_weight?: number
  total_volume?: number
  remark?: string
  items?: InboundOrderItemViewModel[]
}

export interface InboundOrderPageParams extends PageParams {
  order_no?: string
  order_status?: number
  supplier_id?: number
}

class InboundOrderService extends BaseService<InboundOrderViewModel, InboundOrderCreate, InboundOrderUpdate> {
  constructor() {
    super({
      basePath: '/inbound-order',
      usePostForList: true,
      usePostForDelete: true
    })
  }

  getPage(params: InboundOrderPageParams): Promise<PageResult<InboundOrderViewModel>> {
    const normalizedParams = PaginationHelper.normalizeParams(params)
    return http.post('/inbound-order/list', null, { params: normalizedParams })
  }
}

export const inboundOrderService = new InboundOrderService()
export default inboundOrderService
