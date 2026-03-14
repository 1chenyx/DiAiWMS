import { BaseService } from './baseService'
import { http } from './api'
import type { BaseEntity, PageParams, PageResult } from '@/types/common'
import { PaginationHelper } from '@/utils/pagination'

export interface OutboundPickPutawayItem {
  sku_id: number
  qty: number
  goods_location_id: number
  remark?: string
}

export interface OutboundPickPutawayCreate {
  order_ids: number[]
  remark?: string
}

export interface OutboundPickPutawayUpdate {
  id: number
  remark?: string
}

export interface OutboundPickPutawayItemUpdate {
  id: number
  picked_qty: number
  goods_location_id: number
  picker_id: number
  picker: string
  pick_time: number
}

export interface OutboundPickPutawayItemViewModel {
  id: number
  pick_putaway_id: number
  order_item_id: number
  spu_id: number
  spu_code?: string
  spu_name?: string
  sku_id: number
  sku_code?: string
  sku_name?: string
  qty: number
  picked_qty: number
  weight: number
  volume: number
  price: number
  expiry_date: number
  batch_no: string
  production_date: number
  goods_location_id: number
  goods_location_code?: string
  picker_id: number
  picker: string
  pick_time: number
  series_number: string
  tenant_id: string
}

export interface OutboundPickPutawayViewModel extends BaseEntity {
  id: number
  pick_putaway_no: string
  order_id: number
  order_ids: string
  order_no: string
  order_nos: string
  customer_name?: string
  pick_putaway_status: number
  total_qty: number
  total_picked_qty?: number
  warehouse_name?: string
  picker?: string
  pick_time?: string
  warehouse_id?: number
  remark?: string
  items?: OutboundPickPutawayItemViewModel[]
}

export interface OutboundPickPutawayPageParams extends PageParams {
  pick_putaway_no?: string
  pick_putaway_status?: number
  order_no?: string
}

class OutboundPickPutawayService extends BaseService<OutboundPickPutawayViewModel, OutboundPickPutawayCreate, OutboundPickPutawayUpdate> {
  constructor() {
    super({
      basePath: '/outbound-pick-putaway',
      usePostForList: true,
      usePostForDelete: true
    })
  }

  getPage(params: OutboundPickPutawayPageParams): Promise<PageResult<OutboundPickPutawayViewModel>> {
    const normalizedParams = PaginationHelper.normalizeParams(params)
    return http.post('/outbound-pick-putaway/list', null, { params: normalizedParams })
  }

  updateItem(data: OutboundPickPutawayItemUpdate): Promise<void> {
    return http.post('/outbound-pick-putaway/item/update', data)
  }

  startPick(id: number, picker_id: number, picker: string): Promise<void> {
    return http.post('/outbound-pick-putaway/start-pick', null, {
      params: { id, picker_id, picker }
    })
  }

  completePick(id: number): Promise<void> {
    return http.post('/outbound-pick-putaway/complete-pick', null, { params: { id } })
  }
}

export const outboundPickPutawayService = new OutboundPickPutawayService()
export default outboundPickPutawayService
