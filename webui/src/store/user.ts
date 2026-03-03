import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export interface UserInfo {
  user_num: string
  user_name: string
  user_id: number
  user_role: string
  userrole_id: number
  tenant_id: string
}

export const useUserStore = defineStore('user', () => {
  const token = ref<string>('')
  const refreshToken = ref<string>('')
  const userInfo = ref<UserInfo | null>(null)

  const isLoggedIn = computed(() => !!token.value)

  const setToken = (newToken: string) => {
    token.value = newToken
    localStorage.setItem('token', newToken)
  }

  const setRefreshToken = (newRefreshToken: string) => {
    refreshToken.value = newRefreshToken
    localStorage.setItem('refresh_token', newRefreshToken)
  }

  const setUserInfo = (info: UserInfo) => {
    userInfo.value = info
    localStorage.setItem('user_id', info.user_id.toString())
    localStorage.setItem('user_name', info.user_name)
    localStorage.setItem('user_role', info.user_role)
    localStorage.setItem('tenant_id', info.tenant_id)
  }

  const logout = () => {
    token.value = ''
    refreshToken.value = ''
    userInfo.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user_id')
    localStorage.removeItem('user_name')
    localStorage.removeItem('user_role')
    localStorage.removeItem('tenant_id')
  }

  const initFromStorage = () => {
    const storedToken = localStorage.getItem('token')
    const storedRefreshToken = localStorage.getItem('refresh_token')
    const storedUserId = localStorage.getItem('user_id')
    const storedUserName = localStorage.getItem('user_name')
    const storedUserRole = localStorage.getItem('user_role')
    const storedTenantId = localStorage.getItem('tenant_id')

    if (storedToken) {
      token.value = storedToken
    }
    if (storedRefreshToken) {
      refreshToken.value = storedRefreshToken
    }
    if (storedUserId && storedUserName && storedUserRole && storedTenantId) {
      userInfo.value = {
        user_num: '',
        user_name: storedUserName,
        user_id: parseInt(storedUserId),
        user_role: storedUserRole,
        userrole_id: 0,
        tenant_id: storedTenantId
      }
    }
  }

  return {
    token,
    refreshToken,
    userInfo,
    isLoggedIn,
    setToken,
    setRefreshToken,
    setUserInfo,
    logout,
    initFromStorage
  }
})
