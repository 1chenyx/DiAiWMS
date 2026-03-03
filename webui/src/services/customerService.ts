import { BaseService } from './baseService'
import { http } from './api'
import type { BaseEntity, PageParams, PageResult } from '@/types/common'
import { PaginationHelper } from '@/utils/pagination'

export interface Customer extends BaseEntity {
  id: number
  customer_name: string
  customer_code: string
  contact?: string
  phone?: string
  email?: string
  address?: string
  description?: string
  is_valid: boolean
}

export interface CustomerCreate {
  customer_name: string
  customer_code: string
  contact?: string
  phone?: string
  email?: string
  address?: string
  description?: string
  is_valid?: boolean
}

export interface CustomerUpdate {
  id: number
  customer_name?: string
  customer_code?: string
  contact?: string
  phone?: string
  email?: string
  address?: string
  description?: string
  is_valid?: boolean
}

export interface CustomerPageParams extends PageParams {
  customer_name?: string
}

class CustomerService extends BaseService<Customer, CustomerCreate, CustomerUpdate> {
  constructor() {
    super({
      basePath: '/customer',
      usePostForList: true,
      usePostForDelete: true
    })
  }

  getPage(params: CustomerPageParams): Promise<PageResult<Customer>> {
    const normalizedParams = PaginationHelper.normalizeParams(params)
    return http.post('/customer/list', null, { params: normalizedParams })
  }

  getAll(): Promise<Customer[]> {
    return http.get('/customer/all')
  }
}

export const customerService = new CustomerService()
export default customerService
