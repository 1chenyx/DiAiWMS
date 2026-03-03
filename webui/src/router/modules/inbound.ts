import type { RouteRecordRaw } from 'vue-router'

const inboundRoutes: RouteRecordRaw[] = [
  {
    path: 'inbound',
    name: 'Inbound',
    meta: { title: '入库管理', requiresAuth: true },
    children: [
      {
        path: 'order',
        name: 'InboundOrder',
        component: () => import('@/views/inbound/order.vue'),
        meta: { title: '入库订单' }
      },
      {
        path: 'pick-putaway',
        name: 'InboundPickPutaway',
        component: () => import('@/views/inbound/pick-putaway.vue'),
        meta: { title: '入库拣货上架' }
      },
      {
        path: 'receipt',
        name: 'InboundReceipt',
        component: () => import('@/views/inbound/receipt.vue'),
        meta: { title: '入库单' }
      }
    ]
  }
]

export default inboundRoutes
