import { http } from './api'
import { API_CONFIG } from '@/config'

export interface ChatMessage {
  role: 'user' | 'assistant' | 'system'
  content: string
}

export interface ChatRequest {
  messages: ChatMessage[]
  config_id?: number
  stream?: boolean
  temperature?: number
  max_tokens?: number
}

export interface ChatResponse {
  message: ChatMessage
  usage: {
    prompt_tokens: number
    completion_tokens: number
    total_tokens: number
  }
  agent_info: {
    provider_code: string
    model_code: string
    tools_count: number
    skills_count: number
    rules_count: number
  }
}

export interface PoolStats {
  total_tenants: number
  total_agents: number
  tenants: Record<string, any>
}

class AIChatService {
  async completions(request: ChatRequest): Promise<ChatResponse> {
    return http.post('/ai/chat/completions', request)
  }

  async stream(request: ChatRequest): Promise<ReadableStream<Uint8Array>> {
    const token = localStorage.getItem('token')
    const tenantId = localStorage.getItem('tenant_id')

    const response = await fetch(`${API_CONFIG.FULL_URL}/ai/chat/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': token ? `Bearer ${token}` : '',
        'X-Tenant-ID': tenantId || ''
      },
      body: JSON.stringify({ ...request, stream: true })
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    return response.body!
  }

  async getPoolStats(): Promise<PoolStats> {
    return http.get('/ai/chat/pool/stats')
  }

  async clearPool(configId?: number): Promise<{ message: string }> {
    const params = configId ? { config_id: configId } : {}
    return http.post('/ai/chat/pool/clear', null, { params })
  }

  async cleanupExpired(): Promise<{ message: string }> {
    return http.post('/ai/chat/pool/cleanup')
  }
}

export const aiChatService = new AIChatService()
export default aiChatService
