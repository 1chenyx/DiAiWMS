import { BaseService } from './baseService'
import { http } from './api'
import type { BaseEntity, PageParams, PageResult } from '@/types/common'

export interface Sku extends BaseEntity {
  id: number
  sku_name: string
  sku_code: string
  spu_id: number
  spu_name?: string
  spu_code?: string
  bar_code?: string
  weight?: number
  volume?: number
  length?: number
  width?: number
  height?: number
  is_valid: boolean
}

export interface SkuCreate {
  sku_name: string
  sku_code: string
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
  sku_name?: string
  sku_code?: string
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

  getList(spu_id?: number): Promise<Sku[]> {
    return http.get('/sku/list', { params: { spu_id: spu_id || 0 } })
  }
}

export const skuService = new SkuService()
export default skuService
