import { BaseService } from './baseService'
import { http } from './api'
import type { BaseEntity, PageParams, PageResult } from '@/types/common'
import { PaginationHelper } from '@/utils/pagination'

export interface OutboundPickPutawayItem {
  outbound_order_item_id: number
  spu_id: number
  sku_id: number
  qty: number
  picked_qty: number
  location_id?: number
  location_name?: string
}

export interface OutboundPickPutawayCreate {
  outbound_order_id: number
}

export interface OutboundPickPutawayUpdate {
  id: number
  remark?: string
}

export interface OutboundPickPutawayItemUpdate {
  id: number
  picked_qty?: number
  location_id?: number
}

export interface OutboundPickPutawayItemViewModel {
  id: number
  outbound_pick_putaway_id: number
  outbound_order_item_id: number
  spu_id: number
  sku_id: number
  spu_name: string
  sku_name: string
  sku_code: string
  qty: number
  picked_qty: number
  location_id?: number
  location_name?: string
}

export interface OutboundPickPutawayViewModel extends BaseEntity {
  id: number
  pick_putaway_no: string
  outbound_order_id: number
  order_no: string
  customer_id: number
  customer_name: string
  warehouse_id: number
  warehouse_name: string
  pick_putaway_status: number
  total_qty: number
  total_picked_qty: number
  picker_id?: number
  picker?: string
  pick_time?: string
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
