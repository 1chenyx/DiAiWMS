import { BaseService } from './baseService'
import { http } from './api'
import type { BaseEntity, PageParams, PageResult } from '@/types/common'
import { PaginationHelper } from '@/utils/pagination'

export interface Stocktaking extends BaseEntity {
  id: number
  job_code: string
  job_status: number
  remark?: string
  creator?: string
  handler?: string
  sku_id?: number
  sku_code?: string
  sku_name?: string
  location_code?: string
  goods_owner_id?: number
  goods_location_id?: number
  series_number?: string
  expiry_date?: number
  price?: number
  putaway_date?: number
  book_qty?: number
  counted_qty?: number
  difference_qty?: number
  handle_time?: number
}

export interface StocktakingCreate {
  job_code: string
  remark?: string
  sku_id?: number
  goods_owner_id?: number
  goods_location_id?: number
  series_number?: string
  expiry_date?: number
  price?: number
  putaway_date?: number
  book_qty?: number
}

export interface StocktakingUpdate {
  id: number
  job_code?: string
  remark?: string
  sku_id?: number
  goods_owner_id?: number
  goods_location_id?: number
  series_number?: string
  expiry_date?: number
  price?: number
  putaway_date?: number
  book_qty?: number
  counted_qty?: number
}

export interface StocktakingPageParams extends PageParams {
  job_code?: string
}

class StocktakingService extends BaseService<Stocktaking, StocktakingCreate, StocktakingUpdate> {
  constructor() {
    super({
      basePath: '/stocktaking',
      usePostForList: true,
      usePostForDelete: true
    })
  }

  getPage(params: StocktakingPageParams): Promise<PageResult<Stocktaking>> {
    const normalizedParams = PaginationHelper.normalizeParams(params)
    return http.post('/stocktaking/list', null, { params: normalizedParams })
  }
}

export const stocktakingService = new StocktakingService()
export default stocktakingService
