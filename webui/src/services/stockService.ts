import { BaseService } from './baseService'
import { http } from './api'
import type { BaseEntity, PageParams, PageResult } from '@/types/common'
import { PaginationHelper } from '@/utils/pagination'

export interface Stock extends BaseEntity {
  id: number
  sku_id: number
  sku_code?: string
  sku_name?: string
  goods_location_id: number
  location_code?: string
  warehouse_id?: number
  warehouse_name?: string
  goods_owner_id?: number
  goods_owner_name?: string
  qty: number
  qty_available?: number
  qty_frozen?: number
  is_freeze: boolean
  batch_no?: string
}

export interface StockCreate {
  sku_id: number
  goods_location_id: number
  goods_owner_id?: number
  qty: number
  batch_no?: string
}

export interface StockUpdate {
  id: number
  qty?: number
  is_freeze?: boolean
  batch_no?: string
}

export interface StockPageParams extends PageParams {
  sku_id?: number
  goods_location_id?: number
  is_freeze?: boolean
  goods_owner_id?: number
}

class StockService extends BaseService<Stock, StockCreate, StockUpdate> {
  constructor() {
    super({
      basePath: '/stock',
      usePostForList: false,
      usePostForDelete: true
    })
  }

  getPage(params: StockPageParams): Promise<PageResult<Stock>> {
    const normalizedParams = PaginationHelper.normalizeParams(params)
    return http.get('/stock/page', { params: normalizedParams })
  }

  updateQty(id: number, qtyChange: number): Promise<Stock> {
    return http.post(`/stock/${id}/update-qty`, null, { params: { qty_change: qtyChange } })
  }
}

export const stockService = new StockService()
export default stockService
