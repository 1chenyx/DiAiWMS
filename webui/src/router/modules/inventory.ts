import type { RouteRecordRaw } from 'vue-router'

const inventoryRoutes: RouteRecordRaw[] = [
  {
    path: 'inventory',
    name: 'Inventory',
    meta: { title: '库存管理', requiresAuth: true },
    children: [
      {
        path: 'stock',
        name: 'Stock',
        component: () => import('@/views/inventory/stock.vue'),
        meta: { title: '库存查询' }
      },
      {
        path: 'stocktaking',
        name: 'Stocktaking',
        component: () => import('@/views/inventory/stocktaking.vue'),
        meta: { title: '库存盘点' }
      }
    ]
  }
]

export default inventoryRoutes
