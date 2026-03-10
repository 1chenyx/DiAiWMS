export const InboundOrderStatus = {
  PENDING: 0,
  GENERATED: 1,
  CANCELLED: 2
} as const

export type InboundOrderStatus = typeof InboundOrderStatus[keyof typeof InboundOrderStatus]

export const InboundOrderStatusMap: Record<number, string> = {
  [InboundOrderStatus.PENDING]: '待处理',
  [InboundOrderStatus.GENERATED]: '已生成上架单',
  [InboundOrderStatus.CANCELLED]: '已取消'
}

export const InboundOrderStatusTypeMap: Record<number, 'info' | 'warning' | 'success' | 'danger'> = {
  [InboundOrderStatus.PENDING]: 'info',
  [InboundOrderStatus.GENERATED]: 'warning',
  [InboundOrderStatus.CANCELLED]: 'danger'
}

export const OutboundOrderStatus = {
  PENDING: 0,
  GENERATED: 1,
  CANCELLED: 2
} as const

export type OutboundOrderStatus = typeof OutboundOrderStatus[keyof typeof OutboundOrderStatus]

export const OutboundOrderStatusMap: Record<number, string> = {
  [OutboundOrderStatus.PENDING]: '待处理',
  [OutboundOrderStatus.GENERATED]: '已生成拣货单',
  [OutboundOrderStatus.CANCELLED]: '已取消'
}

export const OutboundOrderStatusTypeMap: Record<number, 'info' | 'warning' | 'success' | 'danger'> = {
  [OutboundOrderStatus.PENDING]: 'info',
  [OutboundOrderStatus.GENERATED]: 'warning',
  [OutboundOrderStatus.CANCELLED]: 'danger'
}

export const OutboundPickPutawayStatus = {
  PENDING: 0,
  IN_PROGRESS: 1,
  COMPLETED: 2,
  RECEIPT_GENERATED: 3,
  CANCELLED: 4
} as const

export type OutboundPickPutawayStatus = typeof OutboundPickPutawayStatus[keyof typeof OutboundPickPutawayStatus]

export const OutboundPickPutawayStatusMap: Record<number, string> = {
  [OutboundPickPutawayStatus.PENDING]: '待拣货',
  [OutboundPickPutawayStatus.IN_PROGRESS]: '拣货中',
  [OutboundPickPutawayStatus.COMPLETED]: '拣货完成',
  [OutboundPickPutawayStatus.RECEIPT_GENERATED]: '已生成出库单',
  [OutboundPickPutawayStatus.CANCELLED]: '已取消'
}

export const OutboundPickPutawayStatusTypeMap: Record<number, 'info' | 'warning' | 'success' | 'danger' | 'primary'> = {
  [OutboundPickPutawayStatus.PENDING]: 'info',
  [OutboundPickPutawayStatus.IN_PROGRESS]: 'warning',
  [OutboundPickPutawayStatus.COMPLETED]: 'success',
  [OutboundPickPutawayStatus.RECEIPT_GENERATED]: 'primary',
  [OutboundPickPutawayStatus.CANCELLED]: 'danger'
}

export const OutboundReceiptStatus = {
  PENDING: 0,
  COMPLETED: 1,
  CANCELLED: 2
} as const

export type OutboundReceiptStatus = typeof OutboundReceiptStatus[keyof typeof OutboundReceiptStatus]

export const OutboundReceiptStatusMap: Record<number, string> = {
  [OutboundReceiptStatus.PENDING]: '待出库',
  [OutboundReceiptStatus.COMPLETED]: '已出库',
  [OutboundReceiptStatus.CANCELLED]: '已取消'
}

export const OutboundReceiptStatusTypeMap: Record<number, 'info' | 'warning' | 'success' | 'danger'> = {
  [OutboundReceiptStatus.PENDING]: 'info',
  [OutboundReceiptStatus.COMPLETED]: 'success',
  [OutboundReceiptStatus.CANCELLED]: 'danger'
}

export const PickPutawayStatus = {
  PENDING: 0,
  IN_PROGRESS: 1,
  COMPLETED: 2,
  RECEIPT_GENERATED: 3,
  CANCELLED: 4
} as const

export type PickPutawayStatus = typeof PickPutawayStatus[keyof typeof PickPutawayStatus]

export const PickPutawayStatusMap: Record<number, string> = {
  [PickPutawayStatus.PENDING]: '待上架',
  [PickPutawayStatus.IN_PROGRESS]: '上架中',
  [PickPutawayStatus.COMPLETED]: '上架完成',
  [PickPutawayStatus.RECEIPT_GENERATED]: '已生成入库单',
  [PickPutawayStatus.CANCELLED]: '已取消'
}

export const PickPutawayStatusTypeMap: Record<number, 'info' | 'warning' | 'success' | 'danger' | 'primary'> = {
  [PickPutawayStatus.PENDING]: 'info',
  [PickPutawayStatus.IN_PROGRESS]: 'warning',
  [PickPutawayStatus.COMPLETED]: 'success',
  [PickPutawayStatus.RECEIPT_GENERATED]: 'primary',
  [PickPutawayStatus.CANCELLED]: 'danger'
}

export const StocktakingStatus = {
  DRAFT: 1,
  IN_PROGRESS: 2,
  COMPLETED: 3,
  CANCELLED: 4
} as const

export type StocktakingStatus = typeof StocktakingStatus[keyof typeof StocktakingStatus]

export const StocktakingStatusMap: Record<number, string> = {
  [StocktakingStatus.DRAFT]: '草稿',
  [StocktakingStatus.IN_PROGRESS]: '盘点中',
  [StocktakingStatus.COMPLETED]: '已完成',
  [StocktakingStatus.CANCELLED]: '已取消'
}

export const StocktakingStatusTypeMap: Record<number, 'info' | 'warning' | 'success' | 'danger'> = {
  [StocktakingStatus.DRAFT]: 'info',
  [StocktakingStatus.IN_PROGRESS]: 'warning',
  [StocktakingStatus.COMPLETED]: 'success',
  [StocktakingStatus.CANCELLED]: 'danger'
}
