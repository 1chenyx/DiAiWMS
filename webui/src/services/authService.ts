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

export interface EnterpriseRegisterInput {
  tenant_name: string
  tenant_code: string
  contact_person: string
  contact_phone: string
  contact_email: string
  address?: string
  description?: string
  admin_user_name: string
  admin_password: string
  admin_contact_tel?: string
  admin_email?: string
}

export interface EnterpriseRegisterOutput {
  tenant_id: string
  tenant_name: string
  tenant_code: string
  user_id: number
  user_name: string
}

export const authService = {
  login: (data: LoginInput): Promise<LoginOutput> => {
    return http.post('/common/login', data)
  },
  
  refreshToken: (data: RefreshTokenInput): Promise<RefreshTokenOutput> => {
    return http.post('/common/refresh-token', data)
  },
  
  register: (data: EnterpriseRegisterInput): Promise<EnterpriseRegisterOutput> => {
    return http.post('/common/register', data)
  }
}

export default authService
