import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import type { PageParams, PageResult } from '@/types/common'
import { DEFAULT_PAGE_INDEX, DEFAULT_PAGE_SIZE, PAGE_SIZES } from '@/constants/enums'

export interface UseTableOptions<T> {
  fetchFn: (params: PageParams) => Promise<PageResult<T>>
  immediate?: boolean
  defaultPageSize?: number
}

export function useTable<T>(options: UseTableOptions<T>) {
  const { fetchFn, immediate = true, defaultPageSize = DEFAULT_PAGE_SIZE } = options

  const loading = ref(false)
  const data = ref<T[]>([])
  const total = ref(0)

  const pagination = reactive({
    page_index: DEFAULT_PAGE_INDEX,
    page_size: defaultPageSize
  })

  const searchParams = reactive<Record<string, any>>({})

  const fetchData = async () => {
    loading.value = true
    try {
      const params: PageParams = {
        ...searchParams,
        page_index: pagination.page_index,
        page_size: pagination.page_size
      }
      const result = await fetchFn(params)
      data.value = result.data || result.rows || []
      total.value = result.totals
    } catch (error: any) {
      ElMessage.error(error.message || '获取数据失败')
    } finally {
      loading.value = false
    }
  }

  const handleSearch = (params?: Record<string, any>) => {
    if (params) {
      Object.assign(searchParams, params)
    }
    pagination.page_index = DEFAULT_PAGE_INDEX
    fetchData()
  }

  const handleReset = (defaultParams?: Record<string, any>) => {
    Object.keys(searchParams).forEach(key => {
      delete searchParams[key]
    })
    if (defaultParams) {
      Object.assign(searchParams, defaultParams)
    }
    pagination.page_index = DEFAULT_PAGE_INDEX
    fetchData()
  }

  const handleSizeChange = (size: number) => {
    pagination.page_size = size
    fetchData()
  }

  const handleCurrentChange = (current: number) => {
    pagination.page_index = current
    fetchData()
  }

  const refresh = () => {
    fetchData()
  }

  if (immediate) {
    fetchData()
  }

  return {
    loading,
    data,
    total,
    pagination,
    searchParams,
    fetchData,
    handleSearch,
    handleReset,
    handleSizeChange,
    handleCurrentChange,
    refresh,
    PAGE_SIZES
  }
}
