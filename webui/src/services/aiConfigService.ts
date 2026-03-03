import { BaseService } from './baseService'
import { http } from './api'
import type { BaseEntity, PageParams, PageResult } from '@/types/common'
import { PaginationHelper } from '@/utils/pagination'

export interface AIProviderInfo {
  code: string
  name: string
  description: string
}

export interface AIModelInfo {
  code: string
  name: string
  type: string
  max_tokens: number
  description: string
}

export interface AIProviderWithModels {
  code: string
  name: string
  description: string
  models: AIModelInfo[]
}

export interface TenantAIConfig extends BaseEntity {
  id: number
  provider_code: string
  provider_name: string
  model_code: string
  model_name: string
  api_key: string
  api_endpoint?: string
  is_default: boolean
  tenant_id: string
  creator?: string
  is_valid: boolean
}

export interface TenantAIConfigCreate {
  provider_code: string
  model_code: string
  api_key: string
  api_endpoint?: string
  is_default?: boolean
}

export interface TenantAIConfigUpdate {
  api_key?: string
  api_endpoint?: string
  is_default?: boolean
}

export interface TenantAIConfigPageParams extends PageParams {
  provider_code?: string
  is_default?: boolean
}

class TenantAIConfigService extends BaseService<TenantAIConfig, TenantAIConfigCreate, TenantAIConfigUpdate> {
  constructor() {
    super({
      basePath: '/ai/tenant-config',
      usePostForList: false,
      usePostForDelete: true
    })
  }

  getList(params?: TenantAIConfigPageParams): Promise<PageResult<TenantAIConfig>> {
    const normalizedParams = params ? PaginationHelper.normalizeParams(params) : {}
    return http.get('/ai/tenant-config/list', { params: normalizedParams })
  }

  getDefault(): Promise<TenantAIConfig> {
    return http.get('/ai/tenant-config/default')
  }

  setDefault(configId: number): Promise<TenantAIConfig> {
    return http.post(`/ai/tenant-config/${configId}/set-default`)
  }

  update(configId: number, data: TenantAIConfigUpdate): Promise<TenantAIConfig> {
    return http.post(`/ai/tenant-config/${configId}/update`, data)
  }

  delete(configId: number): Promise<{ message: string }> {
    return http.post(`/ai/tenant-config/${configId}/delete`)
  }
}

export const tenantAIConfigService = new TenantAIConfigService()

export const aiConfigService = {
  getProviders: (): Promise<AIProviderInfo[]> => {
    return http.get('/ai/config/providers')
  },

  getProvider: (providerCode: string): Promise<AIProviderInfo> => {
    return http.get(`/ai/config/providers/${providerCode}`)
  },

  getProviderModels: (providerCode: string): Promise<AIModelInfo[]> => {
    return http.get(`/ai/config/providers/${providerCode}/models`)
  },

  getProvidersWithModels: (): Promise<AIProviderWithModels[]> => {
    return http.get('/ai/config/providers-with-models')
  }
}

export default {
  aiConfigService,
  tenantAIConfigService
}
