<template>
  <div class="login-container">
    <div class="login-form-wrapper">
      <div class="login-header">
        <h2>WMS系统登录</h2>
        <p>请输入您的账号和密码</p>
      </div>
      <el-form
        ref="loginFormRef"
        :model="loginForm"
        :rules="loginRules"
        label-position="top"
        class="login-form"
      >
        <el-form-item label="租户编号" prop="tenant_code">
          <el-input
            v-model="loginForm.tenant_code"
            placeholder="请输入租户编号"
            prefix-icon="OfficeBuilding"
          />
        </el-form-item>
        <el-form-item label="账号" prop="user_name">
          <el-input
            v-model="loginForm.user_name"
            placeholder="请输入账号"
            prefix-icon="User"
          />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
            prefix-icon="Lock"
            show-password
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        <el-form-item>
          <el-checkbox v-model="loginForm.remember">记住我</el-checkbox>
        </el-form-item>
        <el-form-item>
          <el-button
            type="primary"
            :loading="loading"
            @click="handleLogin"
            class="login-button"
          >
            登录
          </el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { authService, type LoginInput, type LoginOutput } from '@/services'
import { useUserStore } from '@/store/user'

const router = useRouter()
const userStore = useUserStore()
const loginFormRef = ref<FormInstance>()
const loading = ref(false)

const loginForm = reactive<LoginInput & { remember: boolean }>({
  tenant_code: '',
  user_name: '',
  password: '',
  remember: false
})

const loginRules = reactive<FormRules>({
  tenant_code: [
    { required: true, message: '请输入租户编号', trigger: 'blur' }
  ],
  user_name: [
    { required: true, message: '请输入账号', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' }
  ]
})

const handleLogin = async () => {
  if (!loginFormRef.value) return
  
  try {
    await loginFormRef.value.validate()
    loading.value = true
    
    const result: LoginOutput = await authService.login({
      tenant_code: loginForm.tenant_code,
      user_name: loginForm.user_name,
      password: loginForm.password
    })
    
    userStore.setToken(result.access_token)
    userStore.setRefreshToken(result.refresh_token)
    userStore.setUserInfo({
      user_num: result.user_num,
      user_name: result.user_name,
      user_id: result.user_id,
      user_role: result.user_role,
      userrole_id: result.userrole_id,
      tenant_id: result.tenant_id
    })
    
    if (loginForm.remember) {
      localStorage.setItem('remember_tenant_code', loginForm.tenant_code)
      localStorage.setItem('remember_user_name', loginForm.user_name)
    } else {
      localStorage.removeItem('remember_tenant_code')
      localStorage.removeItem('remember_user_name')
    }
    
    ElMessage.success('登录成功')
    router.push('/')
  } catch (error) {
    console.error('登录失败:', error)
    loading.value = false
  }
}

const initRememberedUser = () => {
  const rememberedTenantCode = localStorage.getItem('remember_tenant_code')
  const rememberedUserName = localStorage.getItem('remember_user_name')
  if (rememberedTenantCode) {
    loginForm.tenant_code = rememberedTenantCode
  }
  if (rememberedUserName) {
    loginForm.user_name = rememberedUserName
  }
  if (rememberedTenantCode && rememberedUserName) {
    loginForm.remember = true
  }
}

initRememberedUser()
</script>

<style scoped>
.login-container {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100vh;
  background-color: #f0f2f5;
  background-image: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-form-wrapper {
  width: 400px;
  padding: 40px;
  background: white;
  border-radius: 10px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.login-header h2 {
  margin: 0 0 10px 0;
  color: #333;
  font-size: 24px;
}

.login-header p {
  margin: 0;
  color: #666;
  font-size: 14px;
}

.login-form {
  margin-top: 20px;
}

.login-button {
  width: 100%;
  height: 40px;
  font-size: 16px;
}
</style>
