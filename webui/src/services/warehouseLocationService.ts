import { BaseService } from './baseService'
import { http } from './api'
import type { BaseEntity, PageParams, PageResult } from '@/types/common'
import { PaginationHelper } from '@/utils/pagination'

export interface WarehouseLocation extends BaseEntity {
  id: number
  node_type: number
  parent_id: number
  node_name: string
  city: string
  address: string
  email: string
  manager: string
  contact_tel: string
  area_property: number
  location_length: number
  location_width: number
  location_height: number
  location_volume: number
  location_load: number
  roadway_number: string
  shelf_number: string
  layer_number: string
  tag_number: string
  is_valid: boolean
}

export interface WarehouseLocationCreate {
  node_type: number
  parent_id: number
  node_name: string
  city?: string
  address?: string
  email?: string
  manager?: string
  contact_tel?: string
  area_property?: number
  location_length?: number
  location_width?: number
  location_height?: number
  location_volume?: number
  location_load?: number
  roadway_number?: string
  shelf_number?: string
  layer_number?: string
  tag_number?: string
  is_valid?: boolean
}

export interface WarehouseLocationUpdate {
  id: number
  node_name?: string
  city?: string
  address?: string
  email?: string
  manager?: string
  contact_tel?: string
  area_property?: number
  location_length?: number
  location_width?: number
  location_height?: number
  location_volume?: number
  location_load?: number
  roadway_number?: string
  shelf_number?: string
  layer_number?: string
  tag_number?: string
  is_valid?: boolean
}

export interface WarehouseLocationTreeNode {
  id: number
  node_type: number
  node_name: string
  parent_id: number
  children: WarehouseLocationTreeNode[]
}

export interface WarehouseLocationPageParams extends PageParams {
  node_name?: string
  node_type?: number
  parent_id?: number
  is_valid?: boolean
}

class WarehouseLocationService extends BaseService<WarehouseLocation, WarehouseLocationCreate, WarehouseLocationUpdate> {
  constructor() {
    super({
      basePath: '/warehouselocation',
      usePostForList: false,
      usePostForDelete: true
    })
  }

  getPage(params: WarehouseLocationPageParams): Promise<PageResult<WarehouseLocation>> {
    const normalizedParams = PaginationHelper.normalizeParams(params)
    return http.get('/warehouselocation/page', { params: normalizedParams })
  }

  getTree(): Promise<WarehouseLocationTreeNode[]> {
    return http.get('/warehouselocation/tree')
  }

  getChildren(parentId: number, nodeType?: number): Promise<WarehouseLocation[]> {
    return http.get('/warehouselocation/children', { 
      params: { 
        parent_id: parentId,
        ...(nodeType !== undefined && { node_type: nodeType })
      } 
    })
  }

  getList(nodeType?: number, parentId?: number): Promise<WarehouseLocation[]> {
    return http.get('/warehouselocation/list', { 
      params: { 
        ...(nodeType !== undefined && { node_type: nodeType }),
        ...(parentId !== undefined && { parent_id: parentId })
      } 
    })
  }

  getSelectItems(nodeType: number, parentId: number): Promise<Array<{ id: number; node_name: string }>> {
    return http.get('/warehouselocation/select-items', { 
      params: { 
        node_type: nodeType,
        parent_id: parentId
      } 
    })
  }
}

export const warehouseLocationService = new WarehouseLocationService()
export default warehouseLocationService
