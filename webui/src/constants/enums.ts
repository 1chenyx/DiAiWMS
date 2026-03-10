export const OrderStatus = {
  PENDING: 1,
  PROCESSING: 2,
  COMPLETED: 3,
  CANCELLED: 4
} as const

export type OrderStatus = typeof OrderStatus[keyof typeof OrderStatus]

export const OrderStatusMap: Record<number, string> = {
  [OrderStatus.PENDING]: '待处理',
  [OrderStatus.PROCESSING]: '处理中',
  [OrderStatus.COMPLETED]: '已完成',
  [OrderStatus.CANCELLED]: '已取消'
}

export const OrderStatusTypeMap: Record<number, 'info' | 'warning' | 'success' | 'danger'> = {
  [OrderStatus.PENDING]: 'info',
  [OrderStatus.PROCESSING]: 'warning',
  [OrderStatus.COMPLETED]: 'success',
  [OrderStatus.CANCELLED]: 'danger'
}

export const PAGE_SIZES = [10, 20, 50, 100] as const
export const MAX_PAGE_SIZE = 100
export const DEFAULT_PAGE_SIZE = 10
export const DEFAULT_PAGE_INDEX = 1
