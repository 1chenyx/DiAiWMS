import { BaseService } from './baseService'
import { http } from './api'
import type { BaseEntity } from '@/types/common'

export interface Category extends BaseEntity {
  id: number
  category_name: string
  category_code: string
  parent_id?: number
  level?: number
  sort_order?: number
  is_valid: boolean
}

export interface CategoryCreate {
  category_name: string
  category_code: string
  parent_id?: number
  sort_order?: number
  is_valid?: boolean
}

export interface CategoryUpdate {
  id: number
  category_name?: string
  category_code?: string
  parent_id?: number
  sort_order?: number
  is_valid?: boolean
}

export interface CategoryTreeNode {
  id: number
  category_name: string
  category_code: string
  parent_id?: number
  level?: number
  sort_order?: number
  is_valid: boolean
  create_time?: string
  update_time?: string
  children: CategoryTreeNode[]
}

class CategoryService extends BaseService<Category, CategoryCreate, CategoryUpdate> {
  constructor() {
    super({
      basePath: '/category',
      usePostForList: false,
      usePostForDelete: true
    })
  }

  getTree(): Promise<CategoryTreeNode[]> {
    return http.get('/category/tree')
  }
}

export const categoryService = new CategoryService()
export default categoryService
