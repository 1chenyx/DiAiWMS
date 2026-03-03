import { http } from './api'
import { PaginationHelper, type PageParams } from '@/utils/pagination'
import type { BaseEntity, PageResult } from '@/types/common'

export interface BaseServiceOptions {
  basePath: string
  usePostForList?: boolean
  usePostForDelete?: boolean
}

export interface CreateParams<T> {
  data: T
}

export interface UpdateParams<T> {
  data: T
}

export interface GetByIdParams {
  id: number
}

export interface DeleteParams {
  id: number
}

export class BaseService<T extends BaseEntity, TCreate, TUpdate = Partial<TCreate>> {
  protected basePath: string
  protected usePostForList: boolean
  protected usePostForDelete: boolean

  constructor(options: BaseServiceOptions) {
    this.basePath = options.basePath
    this.usePostForList = options.usePostForList ?? false
    this.usePostForDelete = options.usePostForDelete ?? false
  }

  getById(id: number): Promise<T> {
    return http.get(this.basePath, { params: { id } })
  }

  getAll(): Promise<T[]> {
    return http.get(`${this.basePath}/list`)
  }

  getPage(params: PageParams): Promise<PageResult<T>> {
    const normalizedParams = PaginationHelper.normalizeParams(params)
    if (this.usePostForList) {
      return http.post(`${this.basePath}/list`, null, { params: normalizedParams })
    }
    return http.get(`${this.basePath}/page`, { params: normalizedParams })
  }

  create(data: TCreate): Promise<T> {
    return http.post(this.basePath, data)
  }

  update(data: TUpdate): Promise<T> {
    return http.post(`${this.basePath}/update`, data)
  }

  delete(id: number): Promise<{ id: number }> {
    if (this.usePostForDelete) {
      return http.post(`${this.basePath}/delete`, null, { params: { id } })
    }
    return http.delete(this.basePath, { params: { id } })
  }
}

export default BaseService
