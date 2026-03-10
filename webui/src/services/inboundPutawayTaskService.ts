import { http } from './api'

export interface InboundPutawayTaskCreate {
  pick_putaway_item_id: number
  putaway_qty: number
  goods_location_id: number
  warehouse_id: number
  warehouse_area_id: number
}

export interface InboundPutawayTaskViewModel {
  id: number
  pick_putaway_item_id: number
  putaway_qty: number
  weight: number
  volume: number
  price: number
  expiry_date: number
  goods_location_id: number
  warehouse_id: number
  warehouse_name?: string
  warehouse_area_id: number
  warehouse_area_name?: string
  warehouse_location_name?: string
  putaway_person_id: number
  putaway_person: string
  putaway_time: number
  series_number: string
  tenant_id: string
  create_time: number
}

class InboundPutawayTaskService {
  async createTask(data: InboundPutawayTaskCreate): Promise<{ id: number; message: string }> {
    return http.post('/inbound-pick-putaway-task/create', data)
  }

  async getTasksByPickPutawayItemId(pickPutawayItemId: number): Promise<{ rows: InboundPutawayTaskViewModel[] }> {
    return http.get(`/inbound-pick-putaway-task/list/${pickPutawayItemId}`)
  }
}

export const inboundPutawayTaskService = new InboundPutawayTaskService()
export default inboundPutawayTaskService
