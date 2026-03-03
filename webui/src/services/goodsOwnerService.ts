import { BaseService } from './baseService'
import { http } from './api'
import type { BaseEntity, PageParams, PageResult } from '@/types/common'
import { PaginationHelper } from '@/utils/pagination'

export interface GoodsOwner extends BaseEntity {
  id: number
  goods_owner_name: string
  goods_owner_code: string
  contact?: string
  phone?: string
  email?: string
  address?: string
  description?: string
  is_valid: boolean
}

export interface GoodsOwnerCreate {
  goods_owner_name: string
  goods_owner_code: string
  contact?: string
  phone?: string
  email?: string
  address?: string
  description?: string
  is_valid?: boolean
}

export interface GoodsOwnerUpdate {
  id: number
  goods_owner_name?: string
  goods_owner_code?: string
  contact?: string
  phone?: string
  email?: string
  address?: string
  description?: string
  is_valid?: boolean
}

export interface GoodsOwnerPageParams extends PageParams {
  goods_owner_name?: string
}

class GoodsOwnerService extends BaseService<GoodsOwner, GoodsOwnerCreate, GoodsOwnerUpdate> {
  constructor() {
    super({
      basePath: '/goodsowner',
      usePostForList: true,
      usePostForDelete: true
    })
  }

  getPage(params: GoodsOwnerPageParams): Promise<PageResult<GoodsOwner>> {
    const normalizedParams = PaginationHelper.normalizeParams(params)
    return http.post('/goodsowner/list', null, { params: normalizedParams })
  }

  getAll(): Promise<GoodsOwner[]> {
    return http.get('/goodsowner/all')
  }
}

export const goodsOwnerService = new GoodsOwnerService()
export default goodsOwnerService
