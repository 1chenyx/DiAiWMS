import { ElMessage } from 'element-plus'

export enum ErrorCode {
  SUCCESS = 200,
  UNAUTHORIZED = 401,
  FORBIDDEN = 403,
  NOT_FOUND = 404,
  SERVER_ERROR = 500,
  NETWORK_ERROR = 0
}

export interface ApiError {
  code: number
  msg: string
  data?: any
}

export class ErrorHandler {
  static handle(error: any): ApiError {
    if (error.response) {
      return this.handleResponseError(error)
    } else if (error.request) {
      return this.handleNetworkError(error)
    } else {
      return this.handleRequestError(error)
    }
  }

  private static handleResponseError(error: any): ApiError {
    const { status, data } = error.response
    console.error('API Error:', status, data, 'URL:', error.config?.url)

    switch (status) {
      case ErrorCode.UNAUTHORIZED:
        this.handleUnauthorized()
        return { code: status, msg: '认证失败，请重新登录' }
      case ErrorCode.FORBIDDEN:
        return { code: status, msg: '拒绝访问' }
      case ErrorCode.NOT_FOUND:
        return { code: status, msg: '请求的资源不存在' }
      case ErrorCode.SERVER_ERROR:
        return { code: status, msg: data?.msg || '服务器内部错误' }
      default:
        return { code: status, msg: data?.msg || `请求失败: ${status}` }
    }
  }

  private static handleNetworkError(error: any): ApiError {
    console.error('Network Error:', error.request)
    return { code: ErrorCode.NETWORK_ERROR, msg: '网络错误，请检查网络连接' }
  }

  private static handleRequestError(error: any): ApiError {
    console.error('Request Error:', error.message)
    return { code: -1, msg: error.message || '请求失败' }
  }

  private static handleUnauthorized() {
    ElMessage.error('认证失败，请重新登录')
    const userStore = useUserStore()
    userStore.logout()
    setTimeout(() => {
      window.location.href = '/login'
    }, 1000)
  }

  static showMessage(error: ApiError) {
    ElMessage.error(error.msg)
  }
}

export default ErrorHandler
