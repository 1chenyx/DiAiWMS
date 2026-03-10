import { BaseService } from './baseService'
import { http } from './api'
import type { BaseEntity, PageParams, PageResult } from '@/types/common'
import { PaginationHelper } from '@/utils/pagination'

export interface InboundPickPutawayItem {
  sku_id: number
  qty: number
  goods_location_id: number
  batch_no?: string
  production_date?: number
  remark?: string
}

export interface InboundPickPutawayCreate {
  inbound_order_ids?: number[]
  remark?: string
}

export interface InboundPickPutawayUpdate {
  id: number
  remark?: string
}

export interface InboundPickPutawayItemUpdate {
  id: number
  putaway_qty: number
  goods_location_id: number
  warehouse_id?: number
  warehouse_area_id?: number
  putaway_person_id: number
  putaway_person: string
  putaway_time: number
  batch_no?: string
  production_date?: number
}

export interface InboundPickPutawayItemViewModel {
  id: number
  inbound_pick_putaway_id: number
  sku_id: number
  sku_code: string
  sku_name: string
  qty: number
  putaway_qty: number
  goods_location_id: number
  goods_location_code: string
  warehouse_id?: number
  warehouse_name?: string
  warehouse_area_id?: number
  warehouse_area_name?: string
  batch_no?: string
  production_date?: number
  remark?: string
}

export interface InboundPickPutawayViewModel extends BaseEntity {
  id: number
  pick_putaway_no: string
  order_id: number
  order_no: string
  pick_putaway_status: number
  total_qty: number
  putaway_qty?: number
  total_putaway_qty?: number
  supplier_id?: number
  supplier_name?: string
  warehouse_id?: number
  warehouse_name?: string
  goods_owner_id?: number
  goods_owner_name?: string
  total_weight?: number
  total_volume?: number
  putaway_person_id?: number
  putaway_person?: string
  putaway_time?: string
  putaway_start_time?: number
  putaway_end_time?: number
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
