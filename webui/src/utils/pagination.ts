import { DEFAULT_PAGE_SIZE, DEFAULT_PAGE_INDEX, MAX_PAGE_SIZE } from '@/constants/enums'

export interface PageParams {
  page_index?: number
  page_size?: number
  [key: string]: any
}

export interface PageResult<T> {
  data?: T[]
  rows?: T[]
  totals: number
  page_index?: number
  page_size?: number
}

export class PaginationHelper {
  static normalizeParams(params: PageParams): PageParams {
    const normalized = { ...params }
    
    normalized.page_index = params.page_index ?? DEFAULT_PAGE_INDEX
    normalized.page_size = Math.min(
      params.page_size ?? DEFAULT_PAGE_SIZE,
      MAX_PAGE_SIZE
    )
    
    if (normalized.page_index < 1) {
      normalized.page_index = DEFAULT_PAGE_INDEX
    }
    
    if (normalized.page_size < 1) {
      normalized.page_size = DEFAULT_PAGE_SIZE
    }
    
    return normalized
  }
  
  static createPageParams(
    page_index?: number,
    page_size?: number,
    additionalParams?: Record<string, any>
  ): PageParams {
    const params: PageParams = {
      page_index,
      page_size,
      ...additionalParams
    }
    
    return this.normalizeParams(params)
  }
}

export default PaginationHelper
