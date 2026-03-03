import type { RouteRecordRaw } from 'vue-router'

const basicRoutes: RouteRecordRaw[] = [
  {
    path: 'basic',
    name: 'Basic',
    meta: { title: '基础数据', requiresAuth: true },
    children: [
      {
        path: 'warehouse-location',
        name: 'WarehouseLocation',
        component: () => import('@/views/basic/warehouse-location.vue'),
        meta: { title: '仓库管理' }
      },
      {
        path: 'product',
        name: 'Product',
        component: () => import('@/views/basic/product.vue'),
        meta: { title: '商品管理' }
      },
      {
        path: 'supplier',
        name: 'Supplier',
        component: () => import('@/views/basic/supplier.vue'),
        meta: { title: '供应商管理' }
      },
      {
        path: 'customer',
        name: 'Customer',
        component: () => import('@/views/basic/customer.vue'),
        meta: { title: '客户管理' }
      },
      {
        path: 'goods-owner',
        name: 'GoodsOwner',
        component: () => import('@/views/basic/goods-owner.vue'),
        meta: { title: '货主管理' }
      },
      {
        path: 'ai-config',
        name: 'AIConfig',
        component: () => import('@/views/basic/ai-config.vue'),
        meta: { title: 'AI配置' }
      }
    ]
  }
]

export default basicRoutes
