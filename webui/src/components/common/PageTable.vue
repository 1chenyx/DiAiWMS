<template>
  <div class="page-table">
    <el-card shadow="hover" class="table-card">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <h3 class="card-title">{{ title }}</h3>
            <span v-if="total > 0" class="total-count">共 {{ total }} 条</span>
          </div>
          <div class="header-right">
            <slot name="header-actions"></slot>
          </div>
        </div>
      </template>

      <div v-if="$slots.search" class="search-section">
        <slot name="search"></slot>
      </div>

      <el-table 
        :data="data" 
        style="width: 100%" 
        v-loading="loading"
        :header-cell-style="{
          backgroundColor: 'var(--color-bg-secondary)',
          color: 'var(--color-text-secondary)',
          fontWeight: 'var(--font-weight-semibold)',
          fontSize: 'var(--font-size-sm)'
        }"
        :cell-style="{
          color: 'var(--color-text-primary)',
          fontSize: 'var(--font-size-base)'
        }"
        v-bind="$attrs"
      >
        <slot></slot>
      </el-table>

      <div v-if="showPagination" class="pagination-section">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="currentPageSize"
          :page-sizes="pageSizes"
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
interface Props {
  title?: string
  data: any[]
  loading?: boolean
  total?: number
  currentPage?: number
  currentPageSize?: number
  pageSizes?: number[]
  showPagination?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  title: '',
  data: () => [],
  loading: false,
  total: 0,
  currentPage: 1,
  currentPageSize: 10,
  pageSizes: () => [10, 20, 50, 100],
  showPagination: true
})

const emit = defineEmits<{
  'update:currentPage': [value: number]
  'update:currentPageSize': [value: number]
  'size-change': [size: number]
  'current-change': [current: number]
}>()

const handleSizeChange = (size: number) => {
  emit('update:currentPageSize', size)
  emit('size-change', size)
}

const handleCurrentChange = (current: number) => {
  emit('update:currentPage', current)
  emit('current-change', current)
}
</script>

<style scoped>
.page-table {
  width: 100%;
}

.table-card {
  border-radius: var(--radius-xl);
  border: 1px solid var(--color-border-primary);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.card-title {
  font-size: 18px;
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0;
}

.total-count {
  font-size: var(--font-size-sm);
  color: var(--color-text-tertiary);
  padding: 4px 12px;
  background: var(--color-bg-secondary);
  border-radius: var(--radius-full);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.search-section {
  margin-bottom: 24px;
  padding: 20px;
  background: var(--color-bg-secondary);
  border-radius: var(--radius-lg);
}

.pagination-section {
  margin-top: 24px;
  display: flex;
  justify-content: flex-end;
}

:deep(.el-table) {
  border-radius: var(--radius-lg);
  overflow: hidden;
}

:deep(.el-table__header-wrapper) {
  border-radius: var(--radius-lg) var(--radius-lg) 0 0;
}

:deep(.el-table--striped .el-table__body tr.el-table__row--striped td.el-table__cell) {
  background-color: var(--color-bg-secondary);
}

:deep(.el-table__row) {
  transition: all var(--duration-fast) var(--ease-in-out);
}

:deep(.el-table__row:hover > td) {
  background-color: rgba(79, 70, 229, 0.05) !important;
}

:deep(.el-pagination) {
  gap: 8px;
}

:deep(.el-pagination button),
:deep(.el-pagination .el-pager li) {
  border-radius: var(--radius-base);
  font-weight: var(--font-weight-medium);
}

:deep(.el-pagination .el-pager li.is-active) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

@media (max-width: 768px) {
  .card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .pagination-section {
    justify-content: center;
  }
  
  :deep(.el-pagination) {
    flex-wrap: wrap;
    justify-content: center;
  }
}
</style>
