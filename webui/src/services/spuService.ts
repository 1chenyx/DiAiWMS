import { BaseService } from './baseService'
import { http } from './api'
import type { BaseEntity, PageParams, PageResult } from '@/types/common'
import { PaginationHelper } from '@/utils/pagination'
import type { SkuCreate, SkuUpdate } from './skuService'

export interface Spu extends BaseEntity {
  id: number
  spu_name: string
  spu_code: string
  category_id?: number
  category_name?: string
  supplier_id?: number
  supplier_name?: string
  brand?: string
  spu_description?: string
  is_valid: boolean
}

export interface SpuCreate {
  spu_name: string
  spu_code: string
  category_id: number
  supplier_id?: number
  brand?: string
  spu_description?: string
  is_valid?: boolean
  skus?: SkuCreate[]
}

export interface SpuUpdate {
  id: number
  spu_name?: string
  spu_code?: string
  category_id?: number
  supplier_id?: number
  brand?: string
  spu_description?: string
  is_valid?: boolean
  skus?: SkuUpdate[]
  delete_sku_ids?: number[]
}

export interface SpuPageParams extends PageParams {
  spu_code?: string
  spu_name?: string
  category_id?: number
  is_valid?: boolean
}

class SpuService extends BaseService<Spu, SpuCreate, SpuUpdate> {
  constructor() {
    super({
      basePath: '/spu',
      usePostForList: false,
      usePostForDelete: true
    })
  }

  getPage(params: SpuPageParams): Promise<PageResult<Spu>> {
    const normalizedParams = PaginationHelper.normalizeParams(params)
    return http.get('/spu/page', { params: normalizedParams })
  }
}

export const spuService = new SpuService()
export default spuService
