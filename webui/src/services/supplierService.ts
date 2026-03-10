import { BaseService } from './baseService'
import { http } from './api'
import type { BaseEntity, PageParams, PageResult } from '@/types/common'
import { PaginationHelper } from '@/utils/pagination'

export interface Supplier extends BaseEntity {
  id: number
  supplier_name: string
  supplier_code?: string
  contact_person: string
  contact?: string
  phone?: string
  email?: string
  contact_tel: string
  address?: string
  description?: string
  is_valid: boolean
}

export interface SupplierCreate {
  supplier_name: string
  supplier_code?: string
  contact_person: string
  contact?: string
  phone?: string
  email?: string
  contact_tel: string
  address?: string
  description?: string
}

export interface SupplierUpdate {
  id: number
  supplier_name?: string
  supplier_code?: string
  contact_person?: string
  contact?: string
  phone?: string
  email?: string
  contact_tel?: string
  address?: string
  description?: string
  is_valid?: boolean
}

export interface SupplierPageParams extends PageParams {
  supplier_name?: string
  is_valid?: boolean
}

class SupplierService extends BaseService<Supplier, SupplierCreate, SupplierUpdate> {
  constructor() {
    super({
      basePath: '/supplier',
      usePostForList: true,
      usePostForDelete: true
    })
  }

  getPage(params: SupplierPageParams): Promise<PageResult<Supplier>> {
    const normalizedParams = PaginationHelper.normalizeParams(params)
    return http.post('/supplier/list', null, { params: normalizedParams })
  }

  getAll(): Promise<Supplier[]> {
    return http.get('/supplier/all')
  }
}

export const supplierService = new SupplierService()
export default supplierService
