<template>
  <div class="app-container">
    <el-aside 
      :width="isSidebarCollapsed ? '64px' : '240px'" 
      class="sidebar"
      :class="{ 'sidebar-collapsed': isSidebarCollapsed }"
    >
      <div class="logo">
        <div class="logo-icon">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M2 17L12 22L22 17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M2 12L12 17L22 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <transition name="fade">
          <h1 v-if="!isSidebarCollapsed" class="logo-text">WMS系统</h1>
        </transition>
      </div>

      <el-scrollbar class="menu-scrollbar">
        <el-menu
          :default-active="activeMenu"
          class="sidebar-menu"
          :collapse="isSidebarCollapsed"
          :collapse-transition="false"
          router
          @select="handleMenuSelect"
        >
          <el-menu-item index="/">
            <el-icon><House /></el-icon>
            <template #title>仪表盘</template>
          </el-menu-item>
          
          <el-sub-menu index="basic">
            <template #title>
              <el-icon><Collection /></el-icon>
              <span>基础数据</span>
            </template>
            <el-menu-item index="/basic/warehouse-location">
              <el-icon><OfficeBuilding /></el-icon>
              <span>仓库管理</span>
            </el-menu-item>
            <el-menu-item index="/basic/product">
              <el-icon><Box /></el-icon>
              <span>商品管理</span>
            </el-menu-item>
            <el-menu-item index="/basic/supplier">
              <el-icon><Van /></el-icon>
              <span>供应商管理</span>
            </el-menu-item>
            <el-menu-item index="/basic/customer">
              <el-icon><User /></el-icon>
              <span>客户管理</span>
            </el-menu-item>
            <el-menu-item index="/basic/goods-owner">
              <el-icon><Briefcase /></el-icon>
              <span>货主管理</span>
            </el-menu-item>
            <el-menu-item index="/basic/ai-config">
              <el-icon><MagicStick /></el-icon>
              <span>AI配置</span>
            </el-menu-item>
          </el-sub-menu>
          
          <el-sub-menu index="inbound">
            <template #title>
              <el-icon><ArrowUp /></el-icon>
              <span>入库管理</span>
            </template>
            <el-menu-item index="/inbound/order">
              <el-icon><Document /></el-icon>
              <span>入库订单</span>
            </el-menu-item>
            <el-menu-item index="/inbound/pick-putaway">
              <el-icon><Upload /></el-icon>
              <span>入库拣货上架</span>
            </el-menu-item>
            <el-menu-item index="/inbound/receipt">
              <el-icon><DocumentChecked /></el-icon>
              <span>入库单</span>
            </el-menu-item>
          </el-sub-menu>
          
          <el-sub-menu index="outbound">
            <template #title>
              <el-icon><ArrowDown /></el-icon>
              <span>出库管理</span>
            </template>
            <el-menu-item index="/outbound/order">
              <el-icon><Document /></el-icon>
              <span>出库订单</span>
            </el-menu-item>
            <el-menu-item index="/outbound/pick-putaway">
              <el-icon><Download /></el-icon>
              <span>出库拣货</span>
            </el-menu-item>
            <el-menu-item index="/outbound/receipt">
              <el-icon><DocumentChecked /></el-icon>
              <span>出库单</span>
            </el-menu-item>
          </el-sub-menu>
          
          <el-sub-menu index="inventory">
            <template #title>
              <el-icon><Box /></el-icon>
              <span>库存管理</span>
            </template>
            <el-menu-item index="/inventory/stock">
              <el-icon><Search /></el-icon>
              <span>库存查询</span>
            </el-menu-item>
            <el-menu-item index="/inventory/stocktaking">
              <el-icon><List /></el-icon>
              <span>库存盘点</span>
            </el-menu-item>
          </el-sub-menu>
          
          <el-sub-menu index="ai">
            <template #title>
              <el-icon><MagicStick /></el-icon>
              <span>AI服务</span>
            </template>
            <el-menu-item index="/ai/chat">
              <el-icon><ChatDotRound /></el-icon>
              <span>AI对话</span>
            </el-menu-item>
          </el-sub-menu>
        </el-menu>
      </el-scrollbar>
    </el-aside>
    
    <el-container class="main-container">
      <el-header height="60px" class="header">
        <div class="header-left">
          <el-button 
            class="collapse-btn"
            @click="toggleSidebar"
          >
            <el-icon :size="20">
              <Fold v-if="!isSidebarCollapsed" />
              <Expand v-else />
            </el-icon>
          </el-button>
          
          <el-breadcrumb separator="/" class="breadcrumb">
            <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item v-if="currentPageTitle !== '仪表盘'">
              {{ currentPageTitle }}
            </el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        
        <div class="header-right">
          <el-tooltip content="切换主题" placement="bottom">
            <el-button class="theme-btn" @click="toggleTheme">
              <el-icon :size="20">
                <Sunny v-if="isDarkTheme" />
                <Moon v-else />
              </el-icon>
            </el-button>
          </el-tooltip>
          
          <el-tooltip content="全屏" placement="bottom">
            <el-button class="theme-btn" @click="toggleFullscreen">
              <el-icon :size="20">
                <FullScreen />
              </el-icon>
            </el-button>
          </el-tooltip>
          
          <el-badge :value="3" :max="99" class="notification-badge">
            <el-button class="theme-btn">
              <el-icon :size="20"><Bell /></el-icon>
            </el-button>
          </el-badge>
          
          <el-dropdown class="user-dropdown" @command="handleUserCommand">
            <div class="user-info">
              <el-avatar 
                :size="36" 
                class="user-avatar"
                :style="{ backgroundColor: getAvatarColor(userStore.userInfo?.user_name) }"
              >
                {{ userStore.userInfo?.user_name?.charAt(0) || 'U' }}
              </el-avatar>
              <div class="user-details">
                <span class="user-name">{{ userStore.userInfo?.user_name || '未登录' }}</span>
                <span class="user-role">{{ getRoleName(userStore.userInfo?.user_role) }}</span>
              </div>
              <el-icon class="dropdown-icon"><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">
                  <el-icon><User /></el-icon>
                  <span>个人中心</span>
                </el-dropdown-item>
                <el-dropdown-item command="settings">
                  <el-icon><Setting /></el-icon>
                  <span>系统设置</span>
                </el-dropdown-item>
                <el-dropdown-item command="password">
                  <el-icon><Lock /></el-icon>
                  <span>修改密码</span>
                </el-dropdown-item>
                <el-dropdown-item divided command="logout">
                  <el-icon><SwitchButton /></el-icon>
                  <span>退出登录</span>
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      
      <el-main class="main-content">
        <router-view v-slot="{ Component }">
          <transition name="slide-fade" mode="out-in">
            <keep-alive :include="cachedViews">
              <component :is="Component" />
            </keep-alive>
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessageBox, ElMessage } from 'element-plus'
import { 
  House, Collection, ArrowUp, ArrowDown, Box,
  OfficeBuilding, Van, User, Briefcase, MagicStick, ChatDotRound,
  Document, Upload, DocumentChecked, Download, Search, List,
  Fold, Expand, Sunny, Moon, FullScreen, Bell, Setting, Lock, SwitchButton
} from '@element-plus/icons-vue'
import { useUserStore } from '@/store/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const isSidebarCollapsed = ref(false)
const isDarkTheme = ref(false)
const cachedViews = ref(['Dashboard'])

const activeMenu = computed(() => {
  const path = route.path
  return path || '/'
})

const currentPageTitle = computed(() => {
  return route.meta.title as string || '仪表盘'
})

const toggleSidebar = () => {
  isSidebarCollapsed.value = !isSidebarCollapsed.value
}

const toggleTheme = () => {
  isDarkTheme.value = !isDarkTheme.value
  document.documentElement.setAttribute('data-theme', isDarkTheme.value ? 'dark' : 'light')
  localStorage.setItem('theme', isDarkTheme.value ? 'dark' : 'light')
}

const toggleFullscreen = () => {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen()
  } else {
    document.exitFullscreen()
  }
}

const handleMenuSelect = (key: string) => {
  console.log('Selected menu:', key)
}

const handleUserCommand = (command: string) => {
  switch (command) {
    case 'profile':
      ElMessage.info('个人中心功能开发中...')
      break
    case 'settings':
      ElMessage.info('系统设置功能开发中...')
      break
    case 'password':
      ElMessage.info('修改密码功能开发中...')
      break
    case 'logout':
      handleLogout()
      break
  }
}

const handleLogout = () => {
  ElMessageBox.confirm('确定要退出登录吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    userStore.logout()
    router.push('/login')
    ElMessage.success('已退出登录')
  }).catch(() => {
  })
}

const getAvatarColor = (name: string | undefined) => {
  const colors = [
    '#4F46E5', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6',
    '#EC4899', '#06B6D4', '#84CC16', '#F97316', '#6366F1'
  ]
  const index = name ? name.charCodeAt(0) % colors.length : 0
  return colors[index]
}

const getRoleName = (role: number | string | undefined) => {
  const roleMap: Record<number, string> = {
    1: '管理员',
    2: '操作员',
    3: '查看员'
  }
  if (role === undefined) return '未登录'
  const roleNum = typeof role === 'string' ? parseInt(role) : role
  return roleMap[roleNum] || '未知角色'
}

watch(
  () => route.meta.title,
  (newTitle) => {
    document.title = newTitle as string || 'WMS系统'
  },
  { immediate: true }
)

onMounted(() => {
  const savedTheme = localStorage.getItem('theme')
  if (savedTheme === 'dark') {
    isDarkTheme.value = true
    document.documentElement.setAttribute('data-theme', 'dark')
  }
})
</script>

<style scoped>
.app-container {
  display: flex;
  height: 100vh;
  overflow: hidden;
  background-color: var(--color-bg-secondary);
}

.sidebar {
  background: linear-gradient(180deg, #1E293B 0%, #0F172A 100%);
  color: #fff;
  transition: width var(--duration-base) var(--ease-in-out);
  box-shadow: var(--shadow-lg);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.sidebar-collapsed {
  width: 64px;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 0 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  flex-shrink: 0;
}

.logo-icon {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-primary-light);
}

.logo-icon svg {
  width: 100%;
  height: 100%;
}

.logo-text {
  font-size: 18px;
  font-weight: var(--font-weight-bold);
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  white-space: nowrap;
}

.menu-scrollbar {
  flex: 1;
  overflow: hidden;
}

.sidebar-menu {
  border-right: none;
  background-color: transparent;
}

.sidebar-menu:not(.el-menu--collapse) {
  width: 240px;
}

:deep(.el-menu-item),
:deep(.el-sub-menu__title) {
  color: rgba(255, 255, 255, 0.7);
  transition: all var(--duration-fast) var(--ease-in-out);
}

:deep(.el-menu-item:hover),
:deep(.el-sub-menu__title:hover) {
  background-color: rgba(255, 255, 255, 0.05) !important;
  color: #fff;
}

:deep(.el-menu-item.is-active) {
  background: linear-gradient(90deg, rgba(79, 70, 229, 0.2) 0%, rgba(79, 70, 229, 0.05) 100%) !important;
  color: var(--color-primary-light) !important;
  border-right: 3px solid var(--color-primary-light);
}

:deep(.el-sub-menu.is-active > .el-sub-menu__title) {
  color: #fff !important;
}

:deep(.el-menu-item .el-icon),
:deep(.el-sub-menu__title .el-icon) {
  color: inherit;
}

:deep(.el-sub-menu .el-menu) {
  background-color: rgba(0, 0, 0, 0.2) !important;
}

:deep(.el-sub-menu .el-menu-item) {
  background-color: transparent !important;
  color: rgba(255, 255, 255, 0.65) !important;
  min-width: auto;
  margin: 0 8px;
  border-radius: 8px;
}

:deep(.el-sub-menu .el-menu-item:hover) {
  background-color: rgba(255, 255, 255, 0.08) !important;
  color: #fff !important;
}

:deep(.el-sub-menu .el-menu-item.is-active) {
  background: linear-gradient(90deg, rgba(79, 70, 229, 0.3) 0%, rgba(79, 70, 229, 0.1) 100%) !important;
  color: var(--color-primary-light) !important;
  border-right: none;
}

.main-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.header {
  background-color: var(--color-bg-primary);
  border-bottom: 1px solid var(--color-border-primary);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  box-shadow: var(--shadow-sm);
  z-index: 10;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.collapse-btn {
  padding: 8px;
  border: none;
  background: transparent;
  color: var(--color-text-secondary);
  transition: all var(--duration-fast) var(--ease-in-out);
}

.collapse-btn:hover {
  background-color: var(--color-bg-secondary);
  color: var(--color-primary);
}

.breadcrumb {
  font-size: var(--font-size-base);
}

:deep(.el-breadcrumb__item:last-child .el-breadcrumb__inner) {
  color: var(--color-text-primary);
  font-weight: var(--font-weight-medium);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.theme-btn {
  padding: 8px;
  border: none;
  background: transparent;
  color: var(--color-text-secondary);
  transition: all var(--duration-fast) var(--ease-in-out);
}

.theme-btn:hover {
  background-color: var(--color-bg-secondary);
  color: var(--color-primary);
}

.notification-badge {
  margin-right: 8px;
}

:deep(.el-badge__content) {
  border: none;
}

.user-dropdown {
  cursor: pointer;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 6px 12px;
  border-radius: var(--radius-lg);
  transition: background-color var(--duration-fast) var(--ease-in-out);
}

.user-info:hover {
  background-color: var(--color-bg-secondary);
}

.user-avatar {
  font-weight: var(--font-weight-semibold);
  color: white;
}

.user-details {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.user-name {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
}

.user-role {
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
}

.dropdown-icon {
  color: var(--color-text-tertiary);
  transition: transform var(--duration-fast) var(--ease-in-out);
}

.user-dropdown :deep(.el-dropdown-menu__item) {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
}

.main-content {
  background-color: var(--color-bg-secondary);
  padding: 24px;
  overflow-y: auto;
  overflow-x: hidden;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity var(--duration-base) var(--ease-in-out);
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

@media (max-width: 768px) {
  .sidebar {
    position: fixed;
    left: 0;
    top: 0;
    height: 100vh;
    z-index: var(--z-modal);
    transform: translateX(0);
    transition: transform var(--duration-base) var(--ease-in-out);
  }

  .sidebar-collapsed {
    transform: translateX(-100%);
  }

  .user-details {
    display: none;
  }

  .main-content {
    padding: 16px;
  }
}
</style>
