import { BaseService } from './baseService'
import { http } from './api'
import type { BaseEntity, PageParams, PageResult } from '@/types/common'
import { PaginationHelper } from '@/utils/pagination'

export interface Sku extends BaseEntity {
  id: number
  sku_code: string
  sku_name: string
  spu_id: number
  spu_code: string
  spu_name: string
  bar_code?: string
  is_valid: boolean
  weight?: number
  volume?: number
  length?: number
  width?: number
  height?: number
}

export interface SkuCreate {
  sku_code: string
  sku_name: string
  spu_id: number
  bar_code?: string
  weight?: number
  volume?: number
  length?: number
  width?: number
  height?: number
  is_valid?: boolean
}

export interface SkuUpdate {
  id: number
  sku_code?: string
  sku_name?: string
  spu_id?: number
  bar_code?: string
  weight?: number
  volume?: number
  length?: number
  width?: number
  height?: number
  is_valid?: boolean
}

export interface SkuPageParams extends PageParams {
  sku_code?: string
  sku_name?: string
  spu_id?: number
  bar_code?: string
}

class SkuService extends BaseService<Sku, SkuCreate, SkuUpdate> {
  constructor() {
    super({
      basePath: '/sku',
      usePostForList: false,
      usePostForDelete: true
    })
  }

  getPage(params: SkuPageParams): Promise<PageResult<Sku>> {
    const normalizedParams = PaginationHelper.normalizeParams(params)
    return http.get('/sku/page', { params: normalizedParams })
  }

  getList(spuId?: number): Promise<Sku[]> {
    const params = spuId !== undefined ? { spu_id: spuId } : {}
    return http.get('/sku/list', { params })
  }

  getAll(spuId?: number): Promise<Sku[]> {
    return this.getList(spuId)
  }
}

export const skuService = new SkuService()
export default skuService
