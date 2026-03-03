export interface PageParams {
  page_index?: number
  page_size?: number
  [key: string]: any
}

export interface PageResult<T> {
  data?: T[]
  rows?: T[]
  totals: number
  page_index?: number
  page_size?: number
}

export interface BaseEntity {
  id: number
  create_time?: string
  update_time?: string
}

export interface CreateResult {
  id: number
}

export interface UpdateResult {
  id: number
}

export interface DeleteResult {
  id: number
}

export interface ApiResponse<T = any> {
  isSuccess: boolean
  code: number
  msg: string
  data: T
}

export interface SelectOption {
  label: string
  value: any
  disabled?: boolean
}

export interface TableColumn {
  prop: string
  label: string
  width?: number | string
  minWidth?: number | string
  fixed?: boolean | 'left' | 'right'
  align?: 'left' | 'center' | 'right'
  sortable?: boolean
  formatter?: (row: any, column: any, cellValue: any, index: number) => any
}

export interface SearchFormItem {
  prop: string
  label: string
  type: 'input' | 'select' | 'date' | 'daterange' | 'number'
  placeholder?: string
  options?: SelectOption[]
  clearable?: boolean
}
