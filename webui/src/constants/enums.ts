export enum OrderStatus {
  PENDING = 1,
  PROCESSING = 2,
  COMPLETED = 3,
  CANCELLED = 4
}

export const OrderStatusMap: Record<OrderStatus, string> = {
  [OrderStatus.PENDING]: '待处理',
  [OrderStatus.PROCESSING]: '处理中',
  [OrderStatus.COMPLETED]: '已完成',
  [OrderStatus.CANCELLED]: '已取消'
}

export const OrderStatusTypeMap: Record<OrderStatus, 'info' | 'warning' | 'success' | 'danger'> = {
  [OrderStatus.PENDING]: 'info',
  [OrderStatus.PROCESSING]: 'warning',
  [OrderStatus.COMPLETED]: 'success',
  [OrderStatus.CANCELLED]: 'danger'
}

export enum InboundOrderStatus {
  PENDING = 1,
  RECEIVED = 2,
  PUTAWAY = 3,
  COMPLETED = 4,
  CANCELLED = 5
}

export const InboundOrderStatusMap: Record<InboundOrderStatus, string> = {
  [InboundOrderStatus.PENDING]: '待收货',
  [InboundOrderStatus.RECEIVED]: '已收货',
  [InboundOrderStatus.PUTAWAY]: '上架中',
  [InboundOrderStatus.COMPLETED]: '已完成',
  [InboundOrderStatus.CANCELLED]: '已取消'
}

export enum OutboundOrderStatus {
  PENDING = 1,
  PICKING = 2,
  PICKED = 3,
  PACKED = 4,
  SHIPPED = 5,
  COMPLETED = 6,
  CANCELLED = 7
}

export const OutboundOrderStatusMap: Record<OutboundOrderStatus, string> = {
  [OutboundOrderStatus.PENDING]: '待拣货',
  [OutboundOrderStatus.PICKING]: '拣货中',
  [OutboundOrderStatus.PICKED]: '已拣货',
  [OutboundOrderStatus.PACKED]: '已打包',
  [OutboundOrderStatus.SHIPPED]: '已发货',
  [OutboundOrderStatus.COMPLETED]: '已完成',
  [OutboundOrderStatus.CANCELLED]: '已取消'
}

export enum StocktakingStatus {
  DRAFT = 1,
  IN_PROGRESS = 2,
  COMPLETED = 3,
  CANCELLED = 4
}

export const StocktakingStatusMap: Record<StocktakingStatus, string> = {
  [StocktakingStatus.DRAFT]: '草稿',
  [StocktakingStatus.IN_PROGRESS]: '盘点中',
  [StocktakingStatus.COMPLETED]: '已完成',
  [StocktakingStatus.CANCELLED]: '已取消'
}

export const PAGE_SIZES = [10, 20, 50, 100] as const
export const MAX_PAGE_SIZE = 100
export const DEFAULT_PAGE_SIZE = 10
export const DEFAULT_PAGE_INDEX = 1
