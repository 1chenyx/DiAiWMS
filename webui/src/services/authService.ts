import { http } from './api'

export interface LoginInput {
  tenant_code: string
  user_name: string
  password: string
}

export interface LoginOutput {
  user_num: string
  user_name: string
  user_id: number
  user_role: string
  userrole_id: number
  tenant_id: string
  expire: number
  access_token: string
  refresh_token: string
}

export interface RefreshTokenInput {
  access_token: string
  refresh_token: string
}

export interface RefreshTokenOutput {
  access_token: string
  expire: number
}

export const authService = {
  login: (data: LoginInput): Promise<LoginOutput> => {
    return http.post('/common/login', data)
  },
  
  refreshToken: (data: RefreshTokenInput): Promise<RefreshTokenOutput> => {
    return http.post('/common/refresh-token', data)
  }
}

export default authService
