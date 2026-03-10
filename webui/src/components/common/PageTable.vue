<template>
  <div class="page-table">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <span>{{ title }}</span>
          <slot name="header-actions"></slot>
        </div>
      </template>

      <div class="search-section" v-if="$slots.search">
        <slot name="search"></slot>
      </div>

      <el-table 
        :data="data" 
        style="width: 100%" 
        v-loading="loading"
        v-bind="$attrs"
      >
        <slot></slot>
      </el-table>

      <div class="pagination" v-if="showPagination">
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
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-section {
  margin-bottom: 20px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
