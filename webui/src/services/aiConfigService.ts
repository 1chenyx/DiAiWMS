import { BaseService } from './baseService'
import { http } from './api'
import type { BaseEntity, PageParams, PageResult } from '@/types/common'
import { PaginationHelper } from '@/utils/pagination'

export interface AIProviderInfo {
  code: string
  name: string
  description: string
  api_base?: string
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
  api_base?: string
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
  id: number
  api_key?: string
  api_endpoint?: string
  is_default?: boolean
}

export interface TenantAIConfigPageParams extends PageParams {
  provider_code?: string
  is_default?: boolean
}

export interface TenantAITool extends BaseEntity {
  id: number
  tool_code: string
  tool_name: string
  tool_category: string
  description?: string
  config?: string
  is_active: boolean
  tenant_id: string
  creator?: string
}

export interface TenantAIToolCreate {
  tool_code: string
  tool_name: string
  tool_category: string
  description?: string
  config?: string
}

export interface TenantAIToolUpdate {
  id: number
  tool_name?: string
  description?: string
  config?: string
  is_active?: boolean
}

export interface TenantAIToolPageParams extends PageParams {
  category?: string
}

export interface TenantAISkill extends BaseEntity {
  id: number
  skill_code: string
  skill_name: string
  skill_type: string
  description?: string
  prompt_template?: string
  tools?: string
  rules?: string
  is_active: boolean
  tenant_id: string
  creator?: string
}

export interface TenantAISkillCreate {
  skill_code: string
  skill_name: string
  skill_type: string
  description?: string
  prompt_template?: string
  tools?: string
  rules?: string
  is_active?: boolean
}

export interface TenantAISkillUpdate {
  id: number
  skill_name?: string
  description?: string
  prompt_template?: string
  tools?: string
  rules?: string
  is_active?: boolean
}

export interface TenantAISkillPageParams extends PageParams {
  skill_type?: string
}

export interface SkillGenerateRequest {
  skill_name: string
  skill_type: string
  description: string
  business_context?: string
}

export interface TenantAIRule extends BaseEntity {
  id: number
  rule_code: string
  rule_name: string
  category: string
  description?: string
  rule_content: string
  priority: number
  is_active: boolean
  is_system: boolean
  tenant_id: string
  creator?: string
}

export interface TenantAIRuleCreate {
  rule_code: string
  rule_name: string
  category: string
  description?: string
  rule_content: string
  priority?: number
  is_active?: boolean
}

export interface TenantAIRuleUpdate {
  id: number
  rule_name?: string
  description?: string
  rule_content?: string
  priority?: number
  is_active?: boolean
}

export interface TenantAIRulePageParams extends PageParams {
  category?: string
}

class TenantAIConfigService extends BaseService<TenantAIConfig, TenantAIConfigCreate, TenantAIConfigUpdate> {
  constructor() {
    super({
      basePath: '/ai/config/llm',
      usePostForList: false,
      usePostForDelete: true
    })
  }

  getList(params?: TenantAIConfigPageParams): Promise<PageResult<TenantAIConfig>> {
    const normalizedParams = params ? PaginationHelper.normalizeParams(params) : {}
    return http.get('/ai/config/llm/list', { params: normalizedParams })
  }

  getById(configId: number): Promise<TenantAIConfig> {
    return http.get('/ai/config/llm', { params: { config_id: configId } })
  }

  getDefault(): Promise<TenantAIConfig> {
    return http.get('/ai/config/llm/default')
  }

  setDefault(configId: number): Promise<{ id: number }> {
    return http.post('/ai/config/llm/set-default', null, { params: { config_id: configId } })
  }

  create(data: TenantAIConfigCreate): Promise<TenantAIConfig> {
    return http.post('/ai/config/llm', data)
  }

  update(data: TenantAIConfigUpdate): Promise<TenantAIConfig> {
    return http.post('/ai/config/llm/update', data)
  }

  delete(id: number): Promise<{ id: number }> {
    return http.post('/ai/config/llm/delete', null, { params: { config_id: id } }).then(() => ({ id }))
  }
}

class TenantAIToolService extends BaseService<TenantAITool, TenantAIToolCreate, TenantAIToolUpdate> {
  constructor() {
    super({
      basePath: '/ai/config/tools',
      usePostForList: false,
      usePostForDelete: true
    })
  }

  getList(params?: TenantAIToolPageParams): Promise<PageResult<TenantAITool>> {
    const normalizedParams = params ? PaginationHelper.normalizeParams(params) : {}
    return http.get('/ai/config/tools/list', { params: normalizedParams })
  }

  getActive(): Promise<TenantAITool[]> {
    return http.get('/ai/config/tools/active')
  }

  activate(data: TenantAIToolCreate): Promise<TenantAITool> {
    return http.post('/ai/config/tools/activate', data)
  }

  deactivate(toolId: number): Promise<{ id: number }> {
    return http.post('/ai/config/tools/deactivate', null, { params: { tool_id: toolId } }).then(() => ({ id: toolId }))
  }

  update(data: TenantAIToolUpdate): Promise<TenantAITool> {
    return http.post('/ai/config/tools/update', data)
  }
}

class TenantAISkillService extends BaseService<TenantAISkill, TenantAISkillCreate, TenantAISkillUpdate> {
  constructor() {
    super({
      basePath: '/ai/config/skills',
      usePostForList: false,
      usePostForDelete: true
    })
  }

  getList(params?: TenantAISkillPageParams): Promise<PageResult<TenantAISkill>> {
    const normalizedParams = params ? PaginationHelper.normalizeParams(params) : {}
    return http.get('/ai/config/skills/list', { params: normalizedParams })
  }

  getActive(): Promise<TenantAISkill[]> {
    return http.get('/ai/config/skills/active')
  }

  create(data: TenantAISkillCreate): Promise<TenantAISkill> {
    return http.post('/ai/config/skills', data)
  }

  update(data: TenantAISkillUpdate): Promise<TenantAISkill> {
    return http.post('/ai/config/skills/update', data)
  }

  delete(id: number): Promise<{ id: number }> {
    return http.post('/ai/config/skills/delete', null, { params: { skill_id: id } }).then(() => ({ id }))
  }

  generate(data: SkillGenerateRequest): Promise<TenantAISkillCreate> {
    return http.post('/ai/config/skills/generate', data)
  }
}

class TenantAIRuleService extends BaseService<TenantAIRule, TenantAIRuleCreate, TenantAIRuleUpdate> {
  constructor() {
    super({
      basePath: '/ai/config/rules',
      usePostForList: false,
      usePostForDelete: true
    })
  }

  getList(params?: TenantAIRulePageParams): Promise<PageResult<TenantAIRule>> {
    const normalizedParams = params ? PaginationHelper.normalizeParams(params) : {}
    return http.get('/ai/config/rules/list', { params: normalizedParams })
  }

  getActive(): Promise<TenantAIRule[]> {
    return http.get('/ai/config/rules/active')
  }

  create(data: TenantAIRuleCreate): Promise<TenantAIRule> {
    return http.post('/ai/config/rules', data)
  }

  update(data: TenantAIRuleUpdate): Promise<TenantAIRule> {
    return http.post('/ai/config/rules/update', data)
  }

  delete(id: number): Promise<{ id: number }> {
    return http.post('/ai/config/rules/delete', null, { params: { rule_id: id } }).then(() => ({ id }))
  }
}

export const tenantAIConfigService = new TenantAIConfigService()
export const tenantAIToolService = new TenantAIToolService()
export const tenantAISkillService = new TenantAISkillService()
export const tenantAIRuleService = new TenantAIRuleService()

export interface AIToolCategoryInfo {
  code: string
  name: string
  description?: string
  icon?: string
  color?: string
}

export interface AIRuleCategoryInfo {
  code: string
  name: string
  description?: string
  priority_range?: number[]
  color?: string
}

export interface SystemAITool {
  code: string
  name: string
  category: string
  description?: string
  is_active: boolean
  is_system: boolean
  config_schema?: Record<string, any>
}

export interface SystemAIRule {
  code: string
  name: string
  category: string
  priority: number
  content: string
  description?: string
  is_active: boolean
  is_system: boolean
}

export const aiConfigService = {
  getProviders: (): Promise<AIProviderInfo[]> => {
    return http.get('/common/ai/system/providers')
  },

  getProvider: (providerCode: string): Promise<AIProviderInfo> => {
    return http.get('/common/ai/system/provider', { params: { provider_code: providerCode } })
  },

  getProviderModels: (providerCode: string): Promise<AIModelInfo[]> => {
    return http.get('/common/ai/system/provider/models', { params: { provider_code: providerCode } })
  },

  getProvidersWithModels: (): Promise<AIProviderWithModels[]> => {
    return http.get('/common/ai/system/providers-with-models')
  },

  getToolCategories: (): Promise<AIToolCategoryInfo[]> => {
    return http.get('/common/ai/system/tools/categories')
  },

  getRuleCategories: (): Promise<AIRuleCategoryInfo[]> => {
    return http.get('/common/ai/system/rules/categories')
  },

  getSystemTools: (): Promise<SystemAITool[]> => {
    return http.get('/common/ai/system/tools')
  },

  getSystemTool: (toolCode: string): Promise<SystemAITool> => {
    return http.get('/common/ai/system/tool', { params: { tool_code: toolCode } })
  },

  getSystemRules: (): Promise<SystemAIRule[]> => {
    return http.get('/common/ai/system/rules')
  },

  getSystemRule: (ruleCode: string): Promise<SystemAIRule> => {
    return http.get('/common/ai/system/rule', { params: { rule_code: ruleCode } })
  }
}

export default {
  aiConfigService,
  tenantAIConfigService,
  tenantAIToolService,
  tenantAISkillService,
  tenantAIRuleService
}
