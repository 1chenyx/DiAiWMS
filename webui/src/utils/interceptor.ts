import type { AxiosInstance, AxiosRequestConfig, AxiosResponse, InternalAxiosRequestConfig } from 'axios'
import { ElMessage } from 'element-plus'
import { ErrorHandler, ErrorCode } from '@/utils/errorHandler'

export interface RequestConfig extends InternalAxiosRequestConfig {
  skipAuth?: boolean
  skipTenant?: boolean
}

export interface ResponseInterceptorOptions {
  onSuccess?: (response: AxiosResponse) => AxiosResponse
  onError?: (error: any) => any
}

export class InterceptorManager {
  constructor(private axiosInstance: AxiosInstance) {}

  setupRequestInterceptor() {
    this.axiosInstance.interceptors.request.use(
      (config: RequestConfig) => {
        if (!config.skipAuth) {
          const token = localStorage.getItem('token')
          if (token) {
            config.headers.Authorization = `Bearer ${token}`
          }
        }

        if (!config.skipTenant) {
          const tenantId = localStorage.getItem('tenant_id')
          if (tenantId) {
            config.headers['X-Tenant-ID'] = tenantId
          }
        }

        return config
      },
      (error) => {
        return Promise.reject(error)
      }
    )
  }

  setupResponseInterceptor(options?: ResponseInterceptorOptions) {
    this.axiosInstance.interceptors.response.use(
      (response: AxiosResponse) => {
        const { data } = response

        if (data && typeof data.isSuccess !== 'undefined') {
          if (data.isSuccess) {
            return data.data
          } else {
            if (data.code === ErrorCode.UNAUTHORIZED) {
              ErrorHandler.handleUnauthorized()
              return Promise.reject(new Error(data.msg || '认证失败'))
            }
            ElMessage.error(data.msg || '请求失败')
            return Promise.reject(new Error(data.msg || '请求失败'))
          }
        }

        return data
      },
      (error) => {
        const apiError = ErrorHandler.handle(error)
        if (options?.onError) {
          return options.onError(error)
        }
        ElMessage.error(apiError.msg)
        return Promise.reject(error)
      }
    )
  }

  setup(options?: ResponseInterceptorOptions) {
    this.setupRequestInterceptor()
    this.setupResponseInterceptor(options)
  }
}

export default InterceptorManager
