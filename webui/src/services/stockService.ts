import { BaseService } from './baseService'
import { http } from './api'
import type { BaseEntity, PageParams, PageResult } from '@/types/common'
import { PaginationHelper } from '@/utils/pagination'

export interface Stock extends BaseEntity {
  id: number
  sku_id: number
  sku_code: string
  sku_name: string
  spu_name: string
  goods_location_id: number
  warehouse_location_name: string
  location_code?: string
  qty: number
  qty_available?: number
  qty_frozen?: number
  is_freeze: boolean
  goods_owner_id: number
  goods_owner_name: string
  warehouse_id: number
  warehouse_name: string
  warehouse_area_id: number
  warehouse_area_name: string
  batch_no: string
  production_date: number
  expiry_date: number
  putaway_date: number
  price: number
  series_number: string
}

export interface StockCreate {
  sku_id: number
  goods_location_id: number
  qty: number
  goods_owner_id: number
}

export interface StockUpdate {
  id: number
  sku_id?: number
  goods_location_id?: number
  qty?: number
  is_freeze?: boolean
  goods_owner_id?: number
}

export interface StockPageParams extends PageParams {
  sku_id?: number
  goods_location_id?: number
  is_freeze?: boolean
  goods_owner_id?: number
}

interface StockPageResponse {
  data: Stock[]
  totals: number
  page_index: number
  page_size: number
}

class StockService extends BaseService<Stock, StockCreate, StockUpdate> {
  constructor() {
    super({
      basePath: '/stock',
      usePostForList: false,
      usePostForDelete: true
    })
  }

  async getPage(params: StockPageParams): Promise<PageResult<Stock>> {
    const normalizedParams = PaginationHelper.normalizeParams(params)
    const response = await http.get<StockPageResponse>('/stock/page', { params: normalizedParams })
    return {
      rows: response.data,
      totals: response.totals
    }
  }

  getAll(): Promise<Stock[]> {
    return http.get('/stock/list')
  }
}

export const stockService = new StockService()
export default stockService
