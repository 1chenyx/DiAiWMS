import { BaseService } from './baseService'
import { http } from './api'
import type { BaseEntity, PageParams, PageResult } from '@/types/common'
import { PaginationHelper } from '@/utils/pagination'

export interface Spu extends BaseEntity {
  id: number
  spu_code: string
  spu_name: string
  category_id: number
  category_name: string
  is_valid: boolean
  supplier_id?: number
  brand?: string
  spu_description?: string
}

export interface SpuCreate {
  spu_code: string
  spu_name: string
  category_id?: number
  supplier_id?: number
  brand?: string
  spu_description?: string
  is_valid?: boolean
}

export interface SpuUpdate {
  id: number
  spu_code?: string
  spu_name?: string
  category_id?: number
  supplier_id?: number
  brand?: string
  spu_description?: string
  is_valid?: boolean
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

  getAll(): Promise<Spu[]> {
    return http.get('/spu/list')
  }
}

export const spuService = new SpuService()
export default spuService
