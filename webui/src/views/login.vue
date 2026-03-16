<template>
  <div class="login-container">
    <div class="login-background">
      <div class="gradient-orb orb-1"></div>
      <div class="gradient-orb orb-2"></div>
      <div class="gradient-orb orb-3"></div>
      <div class="noise-overlay"></div>
    </div>
    
    <div class="login-content">
      <div class="login-left">
        <div class="brand-section">
          <div class="brand-logo">
            <div class="logo-icon">
              <svg viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
                <rect width="40" height="40" rx="10" fill="url(#logoGradient)"/>
                <path d="M20 8L10 14L20 20L30 14L20 8Z" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M10 26L20 32L30 26" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M10 20L20 26L30 20" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <defs>
                  <linearGradient id="logoGradient" x1="0" y1="0" x2="40" y2="40" gradientUnits="userSpaceOnUse">
                    <stop stop-color="#667eea"/>
                    <stop offset="1" stop-color="#764ba2"/>
                  </linearGradient>
                </defs>
              </svg>
            </div>
          </div>
          <h1 class="brand-title">WMS 智能仓储系统</h1>
          <p class="brand-subtitle">高效 · 智能 · 精准</p>
          
          <div class="tech-badges">
            <span class="tech-badge">
              <svg viewBox="0 0 16 16" fill="currentColor">
                <path d="M8 0a8 8 0 1 0 0 16A8 8 0 0 0 8 0zM4.5 7.5a.5.5 0 0 1 0-1h7a.5.5 0 0 1 0 1h-7z"/>
              </svg>
              AI Agent
            </span>
            <span class="tech-badge">
              <svg viewBox="0 0 16 16" fill="currentColor">
                <path d="M8 1a2 2 0 0 1 2 2v4H6V3a2 2 0 0 1 2-2zm3 6V3a3 3 0 0 0-6 0v4a2 2 0 0 0-2 2v3a2 2 0 0 0 2 2h6a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2z"/>
              </svg>
              安全加密
            </span>
            <span class="tech-badge">
              <svg viewBox="0 0 16 16" fill="currentColor">
                <path d="M0 8a8 8 0 1 1 16 0A8 8 0 0 1 0 8zm7.5-3.5a.5.5 0 0 0-1 0v4a.5.5 0 0 0 .276.447l2.5 1.25a.5.5 0 0 0 .448-.894L7.5 8.382V4.5z"/>
              </svg>
              实时同步
            </span>
          </div>
        </div>
        
        <div class="features-section">
          <div class="feature-item">
            <div class="feature-number">01</div>
            <div class="feature-content">
              <h3>智能调度</h3>
              <p>AI驱动的智能仓储调度，优化作业流程</p>
            </div>
          </div>
          
          <div class="feature-item">
            <div class="feature-number">02</div>
            <div class="feature-content">
              <h3>数据安全</h3>
              <p>企业级数据加密，多租户架构隔离</p>
            </div>
          </div>
          
          <div class="feature-item">
            <div class="feature-number">03</div>
            <div class="feature-content">
              <h3>高效协同</h3>
              <p>全流程数字化管理，提升运营效率</p>
            </div>
          </div>
        </div>
      </div>
      
      <div class="login-right">
        <div class="login-card">
          <div class="card-header">
            <div class="tab-buttons">
              <button 
                :class="['tab-btn', { active: activeTab === 'login' }]"
                @click="activeTab = 'login'"
              >
                登录
              </button>
              <button 
                :class="['tab-btn', { active: activeTab === 'register' }]"
                @click="activeTab = 'register'"
              >
                企业注册
              </button>
              <div class="tab-indicator" :style="{ left: activeTab === 'login' ? '0' : '50%' }"></div>
            </div>
          </div>
          
          <div class="card-body">
            <transition name="fade" mode="out-in">
              <div v-if="activeTab === 'login'" key="login" class="form-panel">
                <div class="form-header">
                  <h2>欢迎回来</h2>
                  <p>请登录您的账号</p>
                </div>
                
                <el-form
                  ref="loginFormRef"
                  :model="loginForm"
                  :rules="loginRules"
                  class="auth-form"
                >
                  <el-form-item prop="tenant_code">
                    <el-input
                      v-model="loginForm.tenant_code"
                      placeholder="租户编号"
                      :prefix-icon="OfficeBuilding"
                      clearable
                    />
                  </el-form-item>
                  
                  <el-form-item prop="user_name">
                    <el-input
                      v-model="loginForm.user_name"
                      placeholder="账号"
                      :prefix-icon="User"
                      clearable
                    />
                  </el-form-item>
                  
                  <el-form-item prop="password">
                    <el-input
                      v-model="loginForm.password"
                      type="password"
                      placeholder="密码"
                      :prefix-icon="Lock"
                      show-password
                      @keyup.enter="handleLogin"
                    />
                  </el-form-item>
                  
                  <div class="form-row">
                    <el-checkbox v-model="loginForm.remember">记住我</el-checkbox>
                    <a href="#" class="link">忘记密码？</a>
                  </div>
                  
                  <el-form-item>
                    <el-button
                      type="primary"
                      :loading="loading"
                      @click="handleLogin"
                      class="submit-btn"
                    >
                      {{ loading ? '登录中...' : '登录' }}
                    </el-button>
                  </el-form-item>
                </el-form>
              </div>
              
              <div v-else key="register" class="form-panel">
                <div class="form-header">
                  <h2>创建企业账户</h2>
                  <p>填写以下信息完成注册</p>
                </div>
                
                <el-form
                  ref="registerFormRef"
                  :model="registerForm"
                  :rules="registerRules"
                  class="auth-form"
                >
                  <div class="form-section">
                    <div class="section-title">企业信息</div>
                    <el-form-item prop="tenant_name">
                      <el-input
                        v-model="registerForm.tenant_name"
                        placeholder="企业名称"
                        :prefix-icon="OfficeBuilding"
                        clearable
                      />
                    </el-form-item>
                    
                    <el-form-item prop="tenant_code">
                      <el-input
                        v-model="registerForm.tenant_code"
                        placeholder="企业编码（用于登录）"
                        :prefix-icon="Key"
                        clearable
                      />
                    </el-form-item>
                    
                    <div class="form-grid">
                      <el-form-item prop="contact_person">
                        <el-input
                          v-model="registerForm.contact_person"
                          placeholder="联系人"
                          :prefix-icon="User"
                          clearable
                        />
                      </el-form-item>
                      
                      <el-form-item prop="contact_phone">
                        <el-input
                          v-model="registerForm.contact_phone"
                          placeholder="联系电话"
                          :prefix-icon="Phone"
                          clearable
                        />
                      </el-form-item>
                    </div>
                    
                    <el-form-item prop="contact_email">
                      <el-input
                        v-model="registerForm.contact_email"
                        placeholder="联系邮箱"
                        :prefix-icon="Message"
                        clearable
                      />
                    </el-form-item>
                  </div>
                  
                  <div class="form-section">
                    <div class="section-title">管理员账户</div>
                    <el-form-item prop="admin_user_name">
                      <el-input
                        v-model="registerForm.admin_user_name"
                        placeholder="管理员用户名"
                        :prefix-icon="UserFilled"
                        clearable
                      />
                    </el-form-item>
                    
                    <div class="form-grid">
                      <el-form-item prop="admin_password">
                        <el-input
                          v-model="registerForm.admin_password"
                          type="password"
                          placeholder="密码"
                          :prefix-icon="Lock"
                          show-password
                        />
                      </el-form-item>
                      
                      <el-form-item prop="confirm_password">
                        <el-input
                          v-model="registerForm.confirm_password"
                          type="password"
                          placeholder="确认密码"
                          :prefix-icon="Lock"
                          show-password
                        />
                      </el-form-item>
                    </div>
                  </div>
                  
                  <el-form-item>
                    <el-button
                      type="primary"
                      :loading="registerLoading"
                      @click="handleRegister"
                      class="submit-btn"
                    >
                      {{ registerLoading ? '注册中...' : '注册企业' }}
                    </el-button>
                  </el-form-item>
                </el-form>
              </div>
            </transition>
          </div>
          
          <div class="card-footer">
            <span>遇到问题？</span>
            <a href="#" class="link">联系技术支持</a>
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
import { OfficeBuilding, User, Lock, Phone, Message, UserFilled, Key } from '@element-plus/icons-vue'
import { authService, type LoginInput, type LoginOutput, type EnterpriseRegisterInput } from '@/services'
import { useUserStore } from '@/store/user'

const router = useRouter()
const userStore = useUserStore()
const loginFormRef = ref<FormInstance>()
const registerFormRef = ref<FormInstance>()
const loading = ref(false)
const registerLoading = ref(false)
const activeTab = ref('login')

const loginForm = reactive<LoginInput & { remember: boolean }>({
  tenant_code: '',
  user_name: '',
  password: '',
  remember: false
})

const registerForm = reactive<EnterpriseRegisterInput & { confirm_password: string }>({
  tenant_name: '',
  tenant_code: '',
  contact_person: '',
  contact_phone: '',
  contact_email: '',
  address: '',
  description: '',
  admin_user_name: '',
  admin_password: '',
  confirm_password: '',
  admin_contact_tel: '',
  admin_email: ''
})

const validateConfirmPassword = (rule: any, value: string, callback: any) => {
  if (value !== registerForm.admin_password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

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

const registerRules = reactive<FormRules>({
  tenant_name: [
    { required: true, message: '请输入企业名称', trigger: 'blur' }
  ],
  tenant_code: [
    { required: true, message: '请输入企业编码', trigger: 'blur' },
    { min: 3, max: 20, message: '企业编码长度为3-20个字符', trigger: 'blur' },
    { pattern: /^[a-zA-Z][a-zA-Z0-9_]*$/, message: '企业编码必须以字母开头，只能包含字母、数字和下划线', trigger: 'blur' }
  ],
  contact_person: [
    { required: true, message: '请输入联系人', trigger: 'blur' }
  ],
  contact_phone: [
    { required: true, message: '请输入联系电话', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码', trigger: 'blur' }
  ],
  contact_email: [
    { required: true, message: '请输入联系邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ],
  admin_user_name: [
    { required: true, message: '请输入管理员用户名', trigger: 'blur' }
  ],
  admin_password: [
    { required: true, message: '请输入管理员密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ],
  confirm_password: [
    { required: true, message: '请确认管理员密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
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

const handleRegister = async () => {
  if (!registerFormRef.value) return
  
  try {
    await registerFormRef.value.validate()
    registerLoading.value = true
    
    const { confirm_password, ...registerData } = registerForm
    await authService.register(registerData)
    
    ElMessage({
      message: '企业注册成功！请使用企业编码登录',
      type: 'success',
      duration: 3000
    })
    
    loginForm.tenant_code = registerForm.tenant_code
    loginForm.user_name = registerForm.admin_user_name
    activeTab.value = 'login'
    
    registerFormRef.value.resetFields()
  } catch (error) {
    console.error('注册失败:', error)
  } finally {
    registerLoading.value = false
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
  background: #0f0f23;
}

.login-background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
}

.gradient-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.6;
  animation: float 20s ease-in-out infinite;
}

.orb-1 {
  width: 600px;
  height: 600px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  top: -200px;
  right: -100px;
  animation-delay: 0s;
}

.orb-2 {
  width: 500px;
  height: 500px;
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  bottom: -150px;
  left: -100px;
  animation-delay: 5s;
}

.orb-3 {
  width: 400px;
  height: 400px;
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  top: 50%;
  left: 30%;
  transform: translate(-50%, -50%);
  animation-delay: 10s;
}

@keyframes float {
  0%, 100% {
    transform: translate(0, 0) scale(1);
  }
  33% {
    transform: translate(30px, -30px) scale(1.1);
  }
  66% {
    transform: translate(-20px, 20px) scale(0.9);
  }
}

.noise-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E");
  opacity: 0.03;
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
  gap: 60px;
}

.login-left {
  flex: 1;
  color: white;
}

.brand-section {
  margin-bottom: 60px;
}

.brand-logo {
  margin-bottom: 32px;
}

.logo-icon {
  width: 56px;
  height: 56px;
  border-radius: 14px;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
}

.logo-icon svg {
  width: 100%;
  height: 100%;
}

.brand-title {
  font-size: 42px;
  font-weight: 700;
  margin-bottom: 12px;
  background: linear-gradient(135deg, #fff 0%, rgba(255, 255, 255, 0.7) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: -0.5px;
}

.brand-subtitle {
  font-size: 18px;
  opacity: 0.7;
  letter-spacing: 8px;
  margin-bottom: 32px;
}

.tech-badges {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.tech-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
}

.tech-badge svg {
  width: 14px;
  height: 14px;
  opacity: 0.8;
}

.tech-badge:hover {
  background: rgba(255, 255, 255, 0.15);
  border-color: rgba(255, 255, 255, 0.25);
  transform: translateY(-2px);
}

.features-section {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.feature-item {
  display: flex;
  align-items: flex-start;
  gap: 20px;
  padding: 24px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
}

.feature-item:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.12);
  transform: translateX(8px);
}

.feature-number {
  font-size: 28px;
  font-weight: 700;
  opacity: 0.3;
  line-height: 1;
}

.feature-content h3 {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 6px;
  color: white;
}

.feature-content p {
  font-size: 14px;
  opacity: 0.6;
  line-height: 1.5;
}

.login-right {
  width: 100%;
  max-width: 440px;
}

.login-card {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 24px;
  overflow: hidden;
  box-shadow: 
    0 20px 60px rgba(0, 0, 0, 0.3),
    0 0 0 1px rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
}

.card-header {
  padding: 32px 40px 0;
}

.tab-buttons {
  position: relative;
  display: flex;
  background: #f5f5f7;
  border-radius: 12px;
  padding: 4px;
}

.tab-btn {
  flex: 1;
  padding: 12px 24px;
  font-size: 15px;
  font-weight: 600;
  color: #666;
  background: transparent;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s ease;
  z-index: 1;
}

.tab-btn.active {
  color: #fff;
}

.tab-indicator {
  position: absolute;
  top: 4px;
  left: 0;
  width: 50%;
  height: calc(100% - 8px);
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 10px;
  transition: left 0.3s ease;
  z-index: 0;
}

.card-body {
  padding: 32px 40px;
  min-height: 420px;
}

.form-panel {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.form-header {
  text-align: center;
  margin-bottom: 32px;
}

.form-header h2 {
  font-size: 24px;
  font-weight: 700;
  color: #1a1a2e;
  margin-bottom: 8px;
}

.form-header p {
  font-size: 14px;
  color: #666;
}

.auth-form :deep(.el-form-item) {
  margin-bottom: 20px;
}

.auth-form :deep(.el-input__wrapper) {
  padding: 14px 16px;
  border-radius: 12px;
  box-shadow: 0 0 0 1px #e0e0e0 inset;
  transition: all 0.2s ease;
  background: #fafafa;
}

.auth-form :deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px #667eea inset;
  background: #fff;
}

.auth-form :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 2px #667eea inset;
  background: #fff;
}

.auth-form :deep(.el-input__inner) {
  font-size: 15px;
  color: #1a1a2e;
}

.auth-form :deep(.el-input__inner::placeholder) {
  color: #999;
}

.form-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}

.form-row :deep(.el-checkbox__label) {
  color: #666;
  font-size: 14px;
}

.link {
  font-size: 14px;
  color: #667eea;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.2s ease;
}

.link:hover {
  color: #764ba2;
}

.submit-btn {
  width: 100%;
  height: 50px;
  font-size: 16px;
  font-weight: 600;
  border-radius: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  transition: all 0.3s ease;
}

.submit-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.4);
}

.submit-btn:active {
  transform: translateY(0);
}

.form-section {
  margin-bottom: 24px;
}

.section-title {
  font-size: 13px;
  font-weight: 600;
  color: #999;
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid #eee;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.card-footer {
  padding: 24px 40px;
  text-align: center;
  background: #fafafa;
  border-top: 1px solid #eee;
  font-size: 14px;
  color: #999;
}

.card-footer .link {
  margin-left: 4px;
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
  .card-header,
  .card-body,
  .card-footer {
    padding-left: 24px;
    padding-right: 24px;
  }
  
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .brand-title {
    font-size: 32px;
  }
}
</style>
