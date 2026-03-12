<template>
  <div class="login-container">
    <div class="login-background">
      <div class="bg-shape bg-shape-1"></div>
      <div class="bg-shape bg-shape-2"></div>
      <div class="bg-shape bg-shape-3"></div>
      <div class="bg-grid"></div>
    </div>
    
    <div class="login-content">
      <div class="login-left">
        <div class="brand-section">
          <div class="brand-logo">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M2 17L12 22L22 17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M2 12L12 17L22 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <h1 class="brand-title">WMS 智能仓储系统</h1>
          <p class="brand-subtitle">高效 · 智能 · 精准</p>
        </div>
        
        <div class="features-section">
          <div class="feature-item">
            <div class="feature-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/>
              </svg>
            </div>
            <div class="feature-content">
              <h3>快速响应</h3>
              <p>毫秒级响应速度，提升工作效率</p>
            </div>
          </div>
          
          <div class="feature-item">
            <div class="feature-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
              </svg>
            </div>
            <div class="feature-content">
              <h3>安全可靠</h3>
              <p>多重安全防护，数据加密存储</p>
            </div>
          </div>
          
          <div class="feature-item">
            <div class="feature-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"/>
                <path d="M2 12h20M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>
              </svg>
            </div>
            <div class="feature-content">
              <h3>全球部署</h3>
              <p>云端部署，随时随地访问</p>
            </div>
          </div>
        </div>
      </div>
      
      <div class="login-right">
        <div class="login-card">
          <div class="login-header">
            <h2>欢迎回来</h2>
            <p>请登录您的账号继续使用</p>
          </div>
          
          <el-form
            ref="loginFormRef"
            :model="loginForm"
            :rules="loginRules"
            class="login-form"
            size="large"
          >
            <el-form-item prop="tenant_code">
              <el-input
                v-model="loginForm.tenant_code"
                placeholder="请输入租户编号"
                :prefix-icon="OfficeBuilding"
                clearable
              />
            </el-form-item>
            
            <el-form-item prop="user_name">
              <el-input
                v-model="loginForm.user_name"
                placeholder="请输入账号"
                :prefix-icon="User"
                clearable
              />
            </el-form-item>
            
            <el-form-item prop="password">
              <el-input
                v-model="loginForm.password"
                type="password"
                placeholder="请输入密码"
                :prefix-icon="Lock"
                show-password
                @keyup.enter="handleLogin"
              />
            </el-form-item>
            
            <div class="form-options">
              <el-checkbox v-model="loginForm.remember">
                <span class="remember-text">记住我</span>
              </el-checkbox>
              <a href="#" class="forgot-link">忘记密码？</a>
            </div>
            
            <el-form-item>
              <el-button
                type="primary"
                :loading="loading"
                @click="handleLogin"
                class="login-button"
              >
                <span v-if="!loading">登录</span>
                <span v-else>登录中...</span>
              </el-button>
            </el-form-item>
          </el-form>
          
          <div class="login-footer">
            <p class="footer-text">
              还没有账号？
              <a href="#" class="register-link">联系管理员</a>
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { OfficeBuilding, User, Lock } from '@element-plus/icons-vue'
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
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
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
    
    ElMessage({
      message: '登录成功，欢迎回来！',
      type: 'success',
      duration: 2000
    })
    
    router.push('/')
  } catch (error) {
    console.error('登录失败:', error)
  } finally {
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
  position: relative;
  width: 100%;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
}

.bg-shape {
  position: absolute;
  border-radius: 50%;
  opacity: 0.1;
  animation: float 20s infinite ease-in-out;
}

.bg-shape-1 {
  width: 600px;
  height: 600px;
  background: white;
  top: -200px;
  right: -200px;
  animation-delay: 0s;
}

.bg-shape-2 {
  width: 400px;
  height: 400px;
  background: white;
  bottom: -100px;
  left: -100px;
  animation-delay: 5s;
}

.bg-shape-3 {
  width: 300px;
  height: 300px;
  background: white;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  animation-delay: 10s;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0) scale(1);
  }
  50% {
    transform: translateY(-30px) scale(1.1);
  }
}

.bg-grid {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: 
    linear-gradient(rgba(255, 255, 255, 0.05) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.05) 1px, transparent 1px);
  background-size: 50px 50px;
}

.login-content {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  max-width: 1200px;
  padding: 40px;
  gap: 80px;
}

.login-left {
  flex: 1;
  color: white;
}

.brand-section {
  margin-bottom: 60px;
}

.brand-logo {
  width: 80px;
  height: 80px;
  margin-bottom: 24px;
  color: white;
  animation: pulse 2s ease-in-out infinite;
}

.brand-logo svg {
  width: 100%;
  height: 100%;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.05);
    opacity: 0.9;
  }
}

.brand-title {
  font-size: 48px;
  font-weight: var(--font-weight-bold);
  margin-bottom: 12px;
  background: linear-gradient(135deg, #fff 0%, rgba(255, 255, 255, 0.8) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.brand-subtitle {
  font-size: 20px;
  opacity: 0.9;
  letter-spacing: 4px;
}

.features-section {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.feature-item {
  display: flex;
  align-items: flex-start;
  gap: 20px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: var(--radius-lg);
  backdrop-filter: blur(10px);
  transition: all var(--duration-base) var(--ease-in-out);
}

.feature-item:hover {
  background: rgba(255, 255, 255, 0.15);
  transform: translateX(10px);
}

.feature-icon {
  width: 48px;
  height: 48px;
  flex-shrink: 0;
  padding: 12px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: var(--radius-md);
  color: white;
}

.feature-icon svg {
  width: 100%;
  height: 100%;
}

.feature-content h3 {
  font-size: 18px;
  font-weight: var(--font-weight-semibold);
  margin-bottom: 4px;
  color: white;
}

.feature-content p {
  font-size: 14px;
  opacity: 0.9;
  color: rgba(255, 255, 255, 0.9);
}

.login-right {
  width: 100%;
  max-width: 420px;
}

.login-card {
  background: white;
  border-radius: var(--radius-2xl);
  padding: 48px;
  box-shadow: var(--shadow-2xl);
  backdrop-filter: blur(20px);
}

.login-header {
  text-align: center;
  margin-bottom: 40px;
}

.login-header h2 {
  font-size: 28px;
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  margin-bottom: 8px;
}

.login-header p {
  font-size: 14px;
  color: var(--color-text-secondary);
}

.login-form {
  margin-bottom: 24px;
}

.login-form :deep(.el-input__wrapper) {
  padding: 12px 16px;
  border-radius: var(--radius-lg);
  box-shadow: 0 0 0 1px var(--color-border-primary) inset;
  transition: all var(--duration-fast) var(--ease-in-out);
}

.login-form :deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px var(--color-primary) inset;
}

.login-form :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 2px var(--color-primary) inset;
}

.login-form :deep(.el-input__inner) {
  font-size: 15px;
}

.form-options {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}

.remember-text {
  font-size: 14px;
  color: var(--color-text-secondary);
}

.forgot-link {
  font-size: 14px;
  color: var(--color-primary);
  text-decoration: none;
  transition: color var(--duration-fast) var(--ease-in-out);
}

.forgot-link:hover {
  color: var(--color-primary-light);
}

.login-button {
  width: 100%;
  height: 48px;
  font-size: 16px;
  font-weight: var(--font-weight-semibold);
  border-radius: var(--radius-lg);
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  transition: all var(--duration-base) var(--ease-in-out);
}

.login-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
}

.login-button:active {
  transform: translateY(0);
}

.login-footer {
  text-align: center;
  padding-top: 24px;
  border-top: 1px solid var(--color-border-primary);
}

.footer-text {
  font-size: 14px;
  color: var(--color-text-secondary);
}

.register-link {
  color: var(--color-primary);
  text-decoration: none;
  font-weight: var(--font-weight-medium);
  transition: color var(--duration-fast) var(--ease-in-out);
}

.register-link:hover {
  color: var(--color-primary-light);
}

@media (max-width: 1024px) {
  .login-left {
    display: none;
  }
  
  .login-content {
    justify-content: center;
    padding: 20px;
  }
}

@media (max-width: 480px) {
  .login-card {
    padding: 32px 24px;
  }
  
  .brand-title {
    font-size: 36px;
  }
}
</style>
