import { BaseService } from './baseService'
import { http } from './api'
import type { BaseEntity, PageParams, PageResult } from '@/types/common'
import { PaginationHelper } from '@/utils/pagination'

export interface InboundPickPutawayItem {
  inbound_order_item_id: number
  spu_id: number
  sku_id: number
  qty: number
  picked_qty: number
  putaway_qty: number
  location_id?: number
  location_name?: string
}

export interface InboundPickPutawayCreate {
  inbound_order_id: number
}

export interface InboundPickPutawayUpdate {
  id: number
  remark?: string
}

export interface InboundPickPutawayItemUpdate {
  id: number
  picked_qty?: number
  putaway_qty?: number
  location_id?: number
}

export interface InboundPickPutawayItemViewModel {
  id: number
  inbound_pick_putaway_id: number
  inbound_order_item_id: number
  spu_id: number
  sku_id: number
  spu_name: string
  sku_name: string
  sku_code: string
  qty: number
  picked_qty: number
  putaway_qty: number
  location_id?: number
  location_name?: string
}

export interface InboundPickPutawayViewModel extends BaseEntity {
  id: number
  pick_putaway_no: string
  inbound_order_id: number
  order_no: string
  supplier_id: number
  supplier_name: string
  warehouse_id: number
  warehouse_name: string
  pick_putaway_status: number
  total_qty: number
  total_picked_qty: number
  total_putaway_qty: number
  putaway_person_id?: number
  putaway_person?: string
  putaway_time?: string
  remark?: string
  items?: InboundPickPutawayItemViewModel[]
}

export interface InboundPickPutawayPageParams extends PageParams {
  pick_putaway_no?: string
  pick_putaway_status?: number
  order_no?: string
}

class InboundPickPutawayService extends BaseService<InboundPickPutawayViewModel, InboundPickPutawayCreate, InboundPickPutawayUpdate> {
  constructor() {
    super({
      basePath: '/inbound-pick-putaway',
      usePostForList: true,
      usePostForDelete: true
    })
  }

  getPage(params: InboundPickPutawayPageParams): Promise<PageResult<InboundPickPutawayViewModel>> {
    const normalizedParams = PaginationHelper.normalizeParams(params)
    return http.post('/inbound-pick-putaway/list', null, { params: normalizedParams })
  }

  updateItem(data: InboundPickPutawayItemUpdate): Promise<void> {
    return http.post('/inbound-pick-putaway/item/update', data)
  }

  startPutaway(id: number, putaway_person_id: number, putaway_person: string): Promise<void> {
    return http.post('/inbound-pick-putaway/start-putaway', null, {
      params: { id, putaway_person_id, putaway_person }
    })
  }

  completePutaway(id: number): Promise<void> {
    return http.post('/inbound-pick-putaway/complete-putaway', null, { params: { id } })
  }
}

export const inboundPickPutawayService = new InboundPickPutawayService()
export default inboundPickPutawayService
