import { createRouter, createWebHistory } from 'vue-router'
import Layout from '@/components/layout/Layout.vue'
import { useUserStore } from '@/store/user'
import dashboardRoutes from './modules/dashboard'
import basicRoutes from './modules/basic'
import inboundRoutes from './modules/inbound'
import outboundRoutes from './modules/outbound'
import inventoryRoutes from './modules/inventory'
import authRoutes from './modules/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      component: Layout,
      children: [
        ...dashboardRoutes,
        ...basicRoutes,
        ...inboundRoutes,
        ...outboundRoutes,
        ...inventoryRoutes
      ]
    },
    ...authRoutes
  ]
})

router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
  
  if (requiresAuth && !userStore.isLoggedIn) {
    next('/login')
  } else if (to.path === '/login' && userStore.isLoggedIn) {
    next('/')
  } else {
    next()
  }
})

export default router
