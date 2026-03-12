import { reactive } from 'vue'
import { DEFAULT_PAGE_SIZE, DEFAULT_PAGE_INDEX, PAGE_SIZES } from '@/constants/enums'

export interface PaginationOptions {
  defaultPageSize?: number
  defaultPageIndex?: number
  pageSizes?: number[]
  onPageChange?: () => void
}

export function usePagination(options: PaginationOptions = {}) {
  const {
    defaultPageSize = DEFAULT_PAGE_SIZE,
    defaultPageIndex = DEFAULT_PAGE_INDEX,
    pageSizes = PAGE_SIZES,
    onPageChange
  } = options

  const pagination = reactive({
    page_index: defaultPageIndex,
    page_size: defaultPageSize,
    total: 0
  })

  const handleSizeChange = (size: number) => {
    pagination.page_size = size
    pagination.page_index = DEFAULT_PAGE_INDEX
    onPageChange?.()
  }

  const handleCurrentChange = (current: number) => {
    pagination.page_index = current
    onPageChange?.()
  }

  const resetPagination = () => {
    pagination.page_index = DEFAULT_PAGE_INDEX
    pagination.page_size = defaultPageSize
  }

  const setTotal = (total: number) => {
    pagination.total = total
  }

  return {
    pagination,
    handleSizeChange,
    handleCurrentChange,
    resetPagination,
    setTotal,
    PAGE_SIZES: pageSizes
  }
}
