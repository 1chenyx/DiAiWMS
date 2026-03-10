import { BaseService } from './baseService'
import { http } from './api'
import type { BaseEntity, PageParams, PageResult } from '@/types/common'
import { PaginationHelper } from '@/utils/pagination'

export interface Category extends BaseEntity {
  id: number
  parent_id: number
  category_name: string
  category_code: string
  is_valid: boolean
  sort_order?: number
}

export interface CategoryCreate {
  parent_id?: number
  category_name: string
  category_code: string
  sort_order?: number
}

export interface CategoryUpdate {
  id: number
  parent_id?: number
  category_name?: string
  category_code?: string
  is_valid?: boolean
  sort_order?: number
}

export interface CategoryPageParams extends PageParams {
  category_name?: string
  category_code?: string
  parent_id?: number
  is_valid?: boolean
}

export interface CategoryTreeNode {
  id: number
  parent_id: number
  category_name: string
  category_code: string
  is_valid: boolean
  sort_order?: number
  children?: CategoryTreeNode[]
}

class CategoryService extends BaseService<Category, CategoryCreate, CategoryUpdate> {
  constructor() {
    super({
      basePath: '/category',
      usePostForList: false,
      usePostForDelete: true
    })
  }

  getPage(params: CategoryPageParams): Promise<PageResult<Category>> {
    const normalizedParams = PaginationHelper.normalizeParams(params)
    return http.get('/category/page', { params: normalizedParams })
  }

  getTree(): Promise<CategoryTreeNode[]> {
    return http.get('/category/tree')
  }

  getAll(): Promise<Category[]> {
    return http.get('/category/list')
  }
}

export const categoryService = new CategoryService()
export default categoryService
