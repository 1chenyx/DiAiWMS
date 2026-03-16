import type { RouteRecordRaw } from 'vue-router'

const aiRoutes: RouteRecordRaw[] = [
  {
    path: 'ai',
    name: 'AI',
    meta: { title: 'AI服务', requiresAuth: true },
    children: [
      {
        path: 'chat',
        name: 'AIChat',
        component: () => import('@/views/ai/chat.vue'),
        meta: { title: 'AI对话' }
      }
    ]
  }
]

export default aiRoutes
