---
name: "vue-frontend-design"
description: "Guides Vue 3 + TypeScript + Element Plus frontend development following project conventions. Invoke when creating Vue components, pages, composables, or styling."
---

# Vue 前端设计开发指南

本技能提供完整的 Vue 3 + TypeScript + Element Plus 前端开发指导，严格遵循项目统一风格和架构模式。

## 项目架构概览

```
webui/
├── src/
│   ├── components/          # 组件目录
│   │   ├── business/        # 业务组件（如：ItemTable, SkuSelector）
│   │   ├── common/          # 通用组件（如：PageTable, FormDialog）
│   │   └── layout/          # 布局组件（Layout）
│   ├── composables/         # 组合式函数
│   │   ├── useTable.ts      # 表格数据管理
│   │   ├── useForm.ts       # 表单管理
│   │   ├── useConfirm.ts    # 确认对话框
│   │   └── useDialog.ts     # 对话框管理
│   ├── constants/           # 常量定义
│   │   ├── enums.ts         # 枚举常量
│   │   ├── index.ts         # 常量导出
│   │   └── status.ts        # 状态映射
│   ├── router/              # 路由配置
│   │   ├── index.ts         # 路由主文件
│   │   └── modules/         # 路由模块
│   ├── services/            # API服务层
│   │   ├── api.ts           # HTTP客户端
│   │   ├── baseService.ts   # 基础服务类
│   │   └── xxxService.ts    # 业务服务类
│   ├── store/               # Pinia状态管理
│   │   └── user.ts          # 用户状态
│   ├── types/               # TypeScript类型定义
│   │   └── common.ts        # 通用类型
│   ├── utils/               # 工具函数
│   │   ├── pagination.ts    # 分页工具
│   │   └── interceptor.ts   # 拦截器
│   └── views/               # 页面视图
│       ├── basic/           # 基础数据模块
│       ├── inbound/         # 入库管理模块
│       ├── outbound/        # 出库管理模块
│       └── inventory/       # 库存管理模块
```

## 核心开发模式

### 1. 组件开发规范

#### 组件文件结构
```vue
<template>
  <!-- 模板内容 -->
</template>

<script setup lang="ts">
// 导入
import { ref, computed } from 'vue'
import type { FormInstance } from 'element-plus'

// 类型定义
interface Props {
  title: string
  data: any[]
}

// Props和Emits
const props = withDefaults(defineProps<Props>(), {
  title: ''
})

const emit = defineEmits<{
  'update:data': [value: any[]]
  'submit': [data: any]
}>()

// 响应式数据
const loading = ref(false)

// 计算属性
const computedValue = computed(() => {
  return props.data.length
})

// 方法
const handleClick = () => {
  emit('submit', { id: 1 })
}
</script>

<style scoped>
/* 样式内容 */
</style>
```

#### Props定义规范
```typescript
// 使用TypeScript接口定义Props
interface Props {
  title: string              // 必填属性
  data: any[]               // 必填属性
  loading?: boolean         // 可选属性
  width?: string | number   // 可选属性
}

// 使用withDefaults设置默认值
const props = withDefaults(defineProps<Props>(), {
  loading: false,
  width: '600px'
})
```

#### Emits定义规范
```typescript
// 使用类型化事件定义
const emit = defineEmits<{
  'update:visible': [value: boolean]
  'update:data': [value: any[]]
  'submit': [data: Record<string, any>]
  'close': []
}>()
```

### 2. Service层开发

#### BaseService使用
```typescript
import { BaseService } from './baseService'
import type { Warehouse, WarehouseCreate, WarehouseUpdate } from '@/types/warehouse'

class WarehouseService extends BaseService<Warehouse, WarehouseCreate, WarehouseUpdate> {
  constructor() {
    super({ basePath: '/warehouse-location' })
  }

  // 自定义方法
  async getTree(): Promise<Warehouse[]> {
    return http.get(`${this.basePath}/tree`)
  }
}

export const warehouseService = new WarehouseService()
```

#### HTTP客户端使用
```typescript
import { http } from './api'

// GET请求
const data = await http.get<User>('/user', { params: { id: 1 } })

// POST请求
const result = await http.post<User>('/user', { name: '张三' })

// PUT请求
const updated = await http.put<User>('/user/1', { name: '李四' })

// DELETE请求
await http.delete('/user/1')
```

### 3. Composables开发

#### useTable使用
```typescript
import { useTable } from '@/composables/useTable'
import { warehouseService } from '@/services/warehouseService'

// 在组件中使用
const {
  loading,
  data,
  total,
  pagination,
  handleSearch,
  handleReset,
  handleSizeChange,
  handleCurrentChange,
  refresh
} = useTable({
  fetchFn: (params) => warehouseService.getPage(params),
  immediate: true,
  defaultPageSize: 10
})
```

#### useForm使用
```typescript
import { useForm } from '@/composables/useForm'

const { formData, loading, reset, handleSubmit } = useForm({
  defaultData: () => ({
    name: '',
    age: 0
  }),
  validate: async (data) => {
    if (!data.name) {
      throw new Error('请输入姓名')
    }
    return true
  },
  submit: async (data) => {
    await warehouseService.create(data)
  }
})

// 提交表单
await handleSubmit(() => {
  // 成功回调
  refresh()
  dialogVisible.value = false
})
```

#### useConfirm使用
```typescript
import { useConfirm } from '@/composables/useConfirm'

const { confirm, confirmDelete, confirmAction } = useConfirm()

// 删除确认
const handleDelete = async (id: number) => {
  const confirmed = await confirmDelete('该仓库')
  if (confirmed) {
    await warehouseService.delete(id)
    refresh()
  }
}

// 操作确认
const handleAction = async () => {
  const confirmed = await confirmAction('提交订单')
  if (confirmed) {
    // 执行操作
  }
}
```

### 4. 类型定义规范

#### 通用类型定义
```typescript
// types/common.ts

// 分页参数
export interface PageParams {
  page_index?: number
  page_size?: number
  [key: string]: any
}

// 分页结果
export interface PageResult<T> {
  data?: T[]
  rows?: T[]
  totals: number
  page_index?: number
  page_size?: number
}

// 基础实体
export interface BaseEntity {
  id: number
  create_time?: string | number
  update_time?: string | number
}

// API响应
export interface ApiResponse<T = any> {
  isSuccess: boolean
  code: number
  msg: string
  data: T
}

// 选择选项
export interface SelectOption {
  label: string
  value: any
  disabled?: boolean
}
```

#### 业务类型定义
```typescript
// types/warehouse.ts

export interface Warehouse extends BaseEntity {
  warehouse_name: string
  city: string
  address: string
  manager: string
  contact_tel: string
  email: string
  is_valid: boolean
  tenant_id: string
}

export interface WarehouseCreate {
  warehouse_name: string
  city: string
  address: string
  manager?: string
  contact_tel?: string
  email?: string
  is_valid?: boolean
}

export interface WarehouseUpdate extends Partial<WarehouseCreate> {
  id: number
}
```

### 5. 路由配置规范

#### 模块化路由
```typescript
// router/modules/basic.ts
import type { RouteRecordRaw } from 'vue-router'

const basicRoutes: RouteRecordRaw[] = [
  {
    path: 'basic',
    name: 'Basic',
    meta: { title: '基础数据', requiresAuth: true },
    children: [
      {
        path: 'warehouse-location',
        name: 'WarehouseLocation',
        component: () => import('@/views/basic/warehouse-location.vue'),
        meta: { title: '仓库管理' }
      },
      {
        path: 'product',
        name: 'Product',
        component: () => import('@/views/basic/product.vue'),
        meta: { title: '商品管理' }
      }
    ]
  }
]

export default basicRoutes
```

#### 路由主文件
```typescript
// router/index.ts
import { createRouter, createWebHistory } from 'vue-router'
import Layout from '@/components/layout/Layout.vue'
import basicRoutes from './modules/basic'
import inboundRoutes from './modules/inbound'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      component: Layout,
      children: [
        ...basicRoutes,
        ...inboundRoutes
      ]
    }
  ]
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
  
  if (requiresAuth && !userStore.isLoggedIn) {
    next('/login')
  } else {
    next()
  }
})

export default router
```

### 6. 常量定义规范

#### 枚举常量
```typescript
// constants/enums.ts

// 订单状态
export const OrderStatus = {
  PENDING: 1,
  PROCESSING: 2,
  COMPLETED: 3,
  CANCELLED: 4
} as const

export type OrderStatus = typeof OrderStatus[keyof typeof OrderStatus]

// 状态映射
export const OrderStatusMap: Record<number, string> = {
  [OrderStatus.PENDING]: '待处理',
  [OrderStatus.PROCESSING]: '处理中',
  [OrderStatus.COMPLETED]: '已完成',
  [OrderStatus.CANCELLED]: '已取消'
}

// 状态类型映射（用于Element Plus Tag）
export const OrderStatusTypeMap: Record<number, 'info' | 'warning' | 'success' | 'danger'> = {
  [OrderStatus.PENDING]: 'info',
  [OrderStatus.PROCESSING]: 'warning',
  [OrderStatus.COMPLETED]: 'success',
  [OrderStatus.CANCELLED]: 'danger'
}

// 分页常量
export const PAGE_SIZES = [10, 20, 50, 100] as const
export const MAX_PAGE_SIZE = 100
export const DEFAULT_PAGE_SIZE = 10
export const DEFAULT_PAGE_INDEX = 1
```

### 7. 工具函数规范

#### 分页工具
```typescript
// utils/pagination.ts
import { DEFAULT_PAGE_SIZE, DEFAULT_PAGE_INDEX, MAX_PAGE_SIZE } from '@/constants/enums'

export class PaginationHelper {
  static normalizeParams(params: PageParams): PageParams {
    const normalized = { ...params }
    
    normalized.page_index = params.page_index ?? DEFAULT_PAGE_INDEX
    normalized.page_size = Math.min(
      params.page_size ?? DEFAULT_PAGE_SIZE,
      MAX_PAGE_SIZE
    )
    
    return normalized
  }
  
  static createPageParams(
    page_index?: number,
    page_size?: number,
    additionalParams?: Record<string, any>
  ): PageParams {
    return this.normalizeParams({
      page_index,
      page_size,
      ...additionalParams
    })
  }
}
```

## 页面开发模板

### 标准CRUD页面模板
```vue
<template>
  <div class="page-container">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <span>{{ pageTitle }}</span>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon> 新增
          </el-button>
        </div>
      </template>

      <!-- 搜索表单 -->
      <el-form :model="searchForm" inline class="search-form">
        <el-form-item label="名称">
          <el-input v-model="searchForm.name" placeholder="请输入名称" clearable />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 数据表格 -->
      <el-table :data="data" v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="名称" />
        <el-table-column prop="status" label="状态">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="handleEdit(row)">
              编辑
            </el-button>
            <el-button type="danger" size="small" @click="handleDelete(row.id)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-model:current-page="pagination.page_index"
        v-model:page-size="pagination.page_size"
        :page-sizes="PAGE_SIZES"
        :total="total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </el-card>

    <!-- 编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px">
      <el-form ref="formRef" :model="formData" :rules="formRules" label-width="100px">
        <el-form-item label="名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入名称" />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-select v-model="formData.status" placeholder="请选择状态">
            <el-option label="启用" :value="1" />
            <el-option label="禁用" :value="0" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitLoading">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { useTable } from '@/composables/useTable'
import { useConfirm } from '@/composables/useConfirm'
import { xxxService } from '@/services/xxxService'
import { PAGE_SIZES } from '@/constants/enums'
import type { FormInstance, FormRules } from 'element-plus'

// 页面标题
const pageTitle = '数据管理'

// 表格数据
const {
  loading,
  data,
  total,
  pagination,
  handleSearch: search,
  handleReset: reset,
  handleSizeChange,
  handleCurrentChange,
  refresh
} = useTable({
  fetchFn: (params) => xxxService.getPage(params),
  immediate: true
})

// 搜索表单
const searchForm = reactive({
  name: ''
})

const handleSearch = () => {
  search(searchForm)
}

const handleReset = () => {
  Object.keys(searchForm).forEach(key => {
    searchForm[key] = ''
  })
  reset()
}

// 对话框
const dialogVisible = ref(false)
const dialogTitle = ref('新增')
const formRef = ref<FormInstance>()
const submitLoading = ref(false)

const formData = reactive({
  id: 0,
  name: '',
  status: 1
})

const formRules: FormRules = {
  name: [
    { required: true, message: '请输入名称', trigger: 'blur' }
  ],
  status: [
    { required: true, message: '请选择状态', trigger: 'change' }
  ]
}

// 新增
const handleAdd = () => {
  dialogTitle.value = '新增'
  Object.assign(formData, {
    id: 0,
    name: '',
    status: 1
  })
  dialogVisible.value = true
}

// 编辑
const handleEdit = (row: any) => {
  dialogTitle.value = '编辑'
  Object.assign(formData, row)
  dialogVisible.value = true
}

// 删除
const { confirmDelete } = useConfirm()

const handleDelete = async (id: number) => {
  const confirmed = await confirmDelete('该记录')
  if (confirmed) {
    await xxxService.delete(id)
    ElMessage.success('删除成功')
    refresh()
  }
}

// 提交
const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate()
  submitLoading.value = true
  
  try {
    if (formData.id) {
      await xxxService.update(formData)
      ElMessage.success('更新成功')
    } else {
      await xxxService.create(formData)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    refresh()
  } finally {
    submitLoading.value = false
  }
}

// 状态映射
const getStatusType = (status: number) => {
  const map: Record<number, any> = {
    1: 'success',
    0: 'danger'
  }
  return map[status] || 'info'
}

const getStatusText = (status: number) => {
  const map: Record<number, string> = {
    1: '启用',
    0: '禁用'
  }
  return map[status] || '未知'
}
</script>

<style scoped>
.page-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-form {
  margin-bottom: 20px;
}

.el-pagination {
  margin-top: 20px;
  justify-content: flex-end;
}
</style>
```

## Element Plus使用规范

### 1. 表单验证
```typescript
import type { FormRules } from 'element-plus'

const formRules: FormRules = {
  name: [
    { required: true, message: '请输入名称', trigger: 'blur' },
    { min: 2, max: 20, message: '长度在 2 到 20 个字符', trigger: 'blur' }
  ],
  email: [
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ]
}
```

### 2. 消息提示
```typescript
import { ElMessage, ElMessageBox } from 'element-plus'

// 成功消息
ElMessage.success('操作成功')

// 错误消息
ElMessage.error('操作失败')

// 警告消息
ElMessage.warning('请注意')

// 确认对话框
await ElMessageBox.confirm('确定要删除吗？', '提示', {
  confirmButtonText: '确定',
  cancelButtonText: '取消',
  type: 'warning'
})
```

### 3. 表格操作
```vue
<el-table :data="tableData" v-loading="loading">
  <el-table-column prop="name" label="名称" />
  <el-table-column label="操作" width="200">
    <template #default="{ row }">
      <el-button size="small" @click="handleEdit(row)">编辑</el-button>
      <el-button size="small" type="danger" @click="handleDelete(row.id)">
        删除
      </el-button>
    </template>
  </el-table-column>
</el-table>
```

## 最佳实践

### 1. 组件拆分原则
- **通用组件**: 放在 `components/common/`
- **业务组件**: 放在 `components/business/`
- **布局组件**: 放在 `components/layout/`

### 2. 命名规范
- **组件文件**: PascalCase (例如: `UserTable.vue`)
- **Composables**: camelCase + use前缀 (例如: `useTable.ts`)
- **Types**: PascalCase (例如: `UserTableProps`)
- **常量**: UPPER_SNAKE_CASE (例如: `DEFAULT_PAGE_SIZE`)
- **Service**: camelCase + Service后缀 (例如: `userService.ts`)

### 3. 导入顺序
```typescript
// 1. Vue相关
import { ref, computed, onMounted } from 'vue'

// 2. 第三方库
import { ElMessage } from 'element-plus'

// 3. 项目内部模块
import { useTable } from '@/composables/useTable'
import { userService } from '@/services/userService'
import type { User } from '@/types/user'
```

### 4. 错误处理
```typescript
try {
  const result = await service.getData()
  // 处理结果
} catch (error: any) {
  console.error('获取数据失败:', error)
  ElMessage.error(error.message || '获取数据失败')
}
```

### 5. 性能优化
```typescript
// 懒加载组件
const AsyncComponent = defineAsyncComponent(() =>
  import('@/components/HeavyComponent.vue')
)

// 计算属性缓存
const filteredList = computed(() => {
  return list.value.filter(item => item.active)
})

// 使用keep-alive
<keep-alive :include="cachedViews">
  <router-view />
</keep-alive>
```

## 开发流程 Checklist

- [ ] 创建类型定义文件（`types/xxx.ts`）
- [ ] 创建Service类（`services/xxxService.ts`）
- [ ] 创建页面组件（`views/module/xxx.vue`）
- [ ] 配置路由（`router/modules/xxx.ts`）
- [ ] 使用Composables封装逻辑
- [ ] 添加Element Plus组件
- [ ] 编写样式（使用scoped）
- [ ] 测试功能

## 常见问题

### 1. Props类型错误
```typescript
// ❌ 错误
const props = defineProps({
  data: Array
})

// ✅ 正确
interface Props {
  data: any[]
}
const props = defineProps<Props>()
```

### 2. 响应式丢失
```typescript
// ❌ 错误
const data = { count: 0 }

// ✅ 正确
import { ref, reactive } from 'vue'
const count = ref(0)
const data = reactive({ count: 0 })
```

### 3. 样式污染
```vue
<!-- ❌ 错误 -->
<style>
.container { /* 全局样式 */ }
</style>

<!-- ✅ 正确 -->
<style scoped>
.container { /* 局部样式 */ }
</style>
```

### 4. Service未正确初始化
```typescript
// ❌ 错误
class UserService {
  constructor() {
    super({ basePath: '/user' })  // 缺少类型参数
  }
}

// ✅ 正确
class UserService extends BaseService<User, UserCreate, UserUpdate> {
  constructor() {
    super({ basePath: '/user' })
  }
}
```
