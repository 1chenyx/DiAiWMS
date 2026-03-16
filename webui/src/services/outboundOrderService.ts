import { BaseService } from './baseService'
import { http } from './api'
import type { BaseEntity, PageParams, PageResult } from '@/types/common'
import { PaginationHelper } from '@/utils/pagination'

export interface OutboundOrderItem {
  sku_id: number
  qty: number
  weight?: number
  volume?: number
  price?: number
  expiry_date?: number
  batch_no?: string
  production_date?: string
  goods_location_id?: number
  remark?: string
}

export interface OutboundOrderCreate {
  customer_id: number
  customer_name?: string
  warehouse_id: number
  goods_owner_id?: number
  goods_owner_name?: string
  remark?: string
  items: OutboundOrderItem[]
}

export interface OutboundOrderUpdate {
  id: number
  customer_id?: number
  warehouse_id?: number
  remark?: string
  items?: OutboundOrderItem[]
}

export interface OutboundOrderItemViewModel {
  id: number
  outbound_order_id: number
  sku_id: number
  spu_id: number
  sku_code: string
  sku_name: string
  spu_name: string
  qty: number
  weight?: number
  volume?: number
  remark?: string
}

export interface OutboundOrderViewModel extends BaseEntity {
  id: number
  order_no: string
  customer_id: number
  customer_name: string
  warehouse_id: number
  warehouse_name: string
  order_status: number
  total_qty: number
  total_weight?: number
  total_volume?: number
  remark?: string
  items?: OutboundOrderItemViewModel[]
}

export interface OutboundOrderPageParams extends PageParams {
  order_no?: string
  order_status?: number
  customer_id?: number
}

class OutboundOrderService extends BaseService<OutboundOrderViewModel, OutboundOrderCreate, OutboundOrderUpdate> {
  constructor() {
    super({
      basePath: '/outbound-order',
      usePostForList: true,
      usePostForDelete: true
    })
  }

  getPage(params: OutboundOrderPageParams): Promise<PageResult<OutboundOrderViewModel>> {
    const normalizedParams = PaginationHelper.normalizeParams(params)
    return http.post('/outbound-order/list', null, { params: normalizedParams })
  }
}

export const outboundOrderService = new OutboundOrderService()
export default outboundOrderService
