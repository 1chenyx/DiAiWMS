import axios, { type AxiosInstance, type AxiosRequestConfig } from 'axios'
import { InterceptorManager } from '@/utils/interceptor'
import { API_CONFIG } from '@/config'

const apiClient: AxiosInstance = axios.create({
  baseURL: API_CONFIG.FULL_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

const interceptorManager = new InterceptorManager(apiClient)
interceptorManager.setup()

export const http = {
  get: <T = any>(url: string, config?: AxiosRequestConfig): Promise<T> => {
    return apiClient.get(url, config)
  },
  
  post: <T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> => {
    return apiClient.post(url, data, config)
  },
  
  put: <T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> => {
    return apiClient.put(url, data, config)
  },
  
  delete: <T = any>(url: string, config?: AxiosRequestConfig): Promise<T> => {
    return apiClient.delete(url, config)
  },
  
  patch: <T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> => {
    return apiClient.patch(url, data, config)
  }
}

export default apiClient
