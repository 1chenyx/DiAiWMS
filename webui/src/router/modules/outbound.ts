import type { RouteRecordRaw } from 'vue-router'

const outboundRoutes: RouteRecordRaw[] = [
  {
    path: 'outbound',
    name: 'Outbound',
    meta: { title: '出库管理', requiresAuth: true },
    children: [
      {
        path: 'order',
        name: 'OutboundOrder',
        component: () => import('@/views/outbound/order.vue'),
        meta: { title: '出库订单' }
      },
      {
        path: 'pick-putaway',
        name: 'OutboundPickPutaway',
        component: () => import('@/views/outbound/pick-putaway.vue'),
        meta: { title: '出库拣货' }
      },
      {
        path: 'receipt',
        name: 'OutboundReceipt',
        component: () => import('@/views/outbound/receipt.vue'),
        meta: { title: '出库单' }
      }
    ]
  }
]

export default outboundRoutes
