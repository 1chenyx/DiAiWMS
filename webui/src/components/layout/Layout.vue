<template>
  <div class="app-container">
    <!-- 侧边栏 -->
    <el-aside width="200px" class="sidebar">
      <div class="logo">
        <h1>WMS系统</h1>
      </div>
      <el-menu
        :default-active="activeMenu"
        class="el-menu-vertical-demo"
        router
        @select="handleMenuSelect"
      >
        <el-menu-item index="/">
          <el-icon><House /></el-icon>
          <span>仪表盘</span>
        </el-menu-item>
        
        <el-sub-menu index="basic">
          <template #title>
            <el-icon><Collection /></el-icon>
            <span>基础数据</span>
          </template>
          <el-menu-item index="/basic/warehouse-location">仓库管理</el-menu-item>
          <el-menu-item index="/basic/product">商品管理</el-menu-item>
          <el-menu-item index="/basic/supplier">供应商管理</el-menu-item>
          <el-menu-item index="/basic/customer">客户管理</el-menu-item>
          <el-menu-item index="/basic/goods-owner">货主管理</el-menu-item>
          <el-menu-item index="/basic/ai-config">租户AI配置</el-menu-item>
        </el-sub-menu>
        
        <el-sub-menu index="inbound">
          <template #title>
            <el-icon><ArrowUp /></el-icon>
            <span>入库管理</span>
          </template>
          <el-menu-item index="/inbound/order">入库订单</el-menu-item>
          <el-menu-item index="/inbound/pick-putaway">入库拣货上架</el-menu-item>
          <el-menu-item index="/inbound/receipt">入库单</el-menu-item>
        </el-sub-menu>
        
        <el-sub-menu index="outbound">
          <template #title>
            <el-icon><ArrowDown /></el-icon>
            <span>出库管理</span>
          </template>
          <el-menu-item index="/outbound/order">出库订单</el-menu-item>
          <el-menu-item index="/outbound/pick-putaway">出库拣货</el-menu-item>
          <el-menu-item index="/outbound/receipt">出库单</el-menu-item>
        </el-sub-menu>
        
        <el-sub-menu index="inventory">
          <template #title>
            <el-icon><Box /></el-icon>
            <span>库存管理</span>
          </template>
          <el-menu-item index="/inventory/stock">库存查询</el-menu-item>
          <el-menu-item index="/inventory/stocktaking">库存盘点</el-menu-item>
        </el-sub-menu>
      </el-menu>
    </el-aside>
    
    <!-- 主内容区 -->
    <el-container>
      <!-- 顶部导航栏 -->
      <el-header height="60px" class="header">
        <div class="header-left">
          <el-button type="text" @click="toggleSidebar">
            <el-icon><Menu /></el-icon>
          </el-button>
          <span class="breadcrumb">{{ currentPageTitle }}</span>
        </div>
        <div class="header-right">
          <el-dropdown>
            <span class="user-info">
              <el-avatar size="small">{{ userStore.userInfo?.user_name?.charAt(0) || 'U' }}</el-avatar>
              <span>{{ userStore.userInfo?.user_name || '未登录' }}</span>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item>个人中心</el-dropdown-item>
                <el-dropdown-item>修改密码</el-dropdown-item>
                <el-dropdown-item @click="handleLogout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      
      <!-- 内容区 -->
      <el-main>
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessageBox } from 'element-plus'
import { House, Collection, ArrowUp, ArrowDown, Box, Menu } from '@element-plus/icons-vue'
import { useUserStore } from '@/store/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const isSidebarCollapsed = ref(false)

const activeMenu = computed(() => {
  const path = route.path
  const segments = path.split('/')
  if (segments.length >= 2) {
    return segments[1] || '/'  
  }
  return '/'  
})

const currentPageTitle = computed(() => {
  return route.meta.title as string || 'WMS系统'
})

const toggleSidebar = () => {
  isSidebarCollapsed.value = !isSidebarCollapsed.value
}

const handleMenuSelect = (key: string) => {
  console.log('Selected menu:', key)
}

const handleLogout = () => {
  ElMessageBox.confirm('确定要退出登录吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    userStore.logout()
    router.push('/login')
  }).catch(() => {
  })
}

watch(
  () => route.meta.title,
  (newTitle) => {
    document.title = newTitle as string || 'WMS系统'
  },
  { immediate: true }
)
</script>

<style scoped>
.app-container {
  display: flex;
  height: 100vh;
  overflow: hidden;
}

.sidebar {
  background-color: #001529;
  color: #fff;
  transition: width 0.3s;
}

.sidebar.collapsed {
  width: 64px;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-bottom: 1px solid #002140;
}

.logo h1 {
  font-size: 18px;
  margin: 0;
  color: #fff;
}

.header {
  background-color: #fff;
  border-bottom: 1px solid #e8e8e8;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 20px;
}

.breadcrumb {
  font-size: 14px;
  color: #666;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  padding: 5px 10px;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.user-info:hover {
  background-color: #f5f5f5;
}

.el-main {
  background-color: #f0f2f5;
  padding: 20px;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
