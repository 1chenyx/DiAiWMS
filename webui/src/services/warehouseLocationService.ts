import { BaseService } from './baseService'
import { http } from './api'
import type { BaseEntity, PageParams, PageResult } from '@/types/common'
import { PaginationHelper } from '@/utils/pagination'

export interface WarehouseLocation extends BaseEntity {
  id: number
  parent_id: number
  node_type: number
  node_name: string
  node_code: string
  is_valid: boolean
  creator?: string
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
}

export interface WarehouseLocationCreate {
  parent_id: number
  node_type: number
  node_name: string
  node_code: string
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
  parent_id?: number
  node_type?: number
  node_name?: string
  node_code?: string
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

export interface WarehouseLocationPageParams extends PageParams {
  node_name?: string
  node_type?: number
  parent_id?: number
  is_valid?: boolean
}

export interface WarehouseLocationTreeNode {
  id: number
  parent_id: number
  node_type: number
  node_name: string
  node_code: string
  is_valid: boolean
  children?: WarehouseLocationTreeNode[]
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

  getTreeByWarehouse(warehouseId: number): Promise<WarehouseLocationTreeNode> {
    return http.get('/warehouselocation/tree-by-warehouse', { params: { warehouse_id: warehouseId } })
  }

  getChildren(parentId: number, nodeType?: number): Promise<WarehouseLocation[]> {
    return http.get('/warehouselocation/children', {
      params: { parent_id: parentId, node_type: nodeType }
    })
  }

  getAll(nodeType?: number, parentId?: number): Promise<WarehouseLocation[]> {
    const params: any = {}
    if (nodeType !== undefined) params.node_type = nodeType
    if (parentId !== undefined) params.parent_id = parentId
    return http.get('/warehouselocation/list', { params })
  }
}

export const warehouseLocationService = new WarehouseLocationService()
export default warehouseLocationService
